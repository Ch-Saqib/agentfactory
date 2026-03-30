/**
 * Promptfoo Deterministic Adapter
 *
 * Bridges the existing deterministic.js grading logic to Promptfoo's custom
 * assertion format. Promptfoo calls this module for each assertion, passing:
 *   - output: string (the raw model response)
 *   - context: { vars, test, prompt }
 *
 * We need to:
 *   1. Parse the model output as YAML (the model should produce a flashcard deck)
 *   2. Write the parsed YAML to a temp file (deterministic.js reads from disk)
 *   3. Construct a caseDef and trialDef matching the evaluateCase() contract
 *   4. Call evaluateCase() and translate results into Promptfoo assertion format
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const yaml = require("yaml");

// We inline the evaluateCase function from the deterministic grader
// rather than require() it (since it's a CLI script with main()).
// Instead, we extract the pure function by loading the source and
// intercepting the module pattern.

const REPO_ROOT = path.resolve(__dirname, "../..");

/**
 * Load evaluateCase from deterministic.js by extracting the function.
 * The deterministic.js file defines evaluateCase and calls main().
 * We'll re-implement the core logic here to avoid side effects.
 */
function loadEvaluateCase() {
  // The deterministic.js has evaluateCase as a local function.
  // We can't require() it directly since main() runs on load.
  // Instead, we use a modified approach: read the source, extract
  // the function, and evaluate it in an isolated context.

  const deterministicPath = path.resolve(
    REPO_ROOT,
    "evals/flashcards/graders/deterministic.js"
  );
  const source = fs.readFileSync(deterministicPath, "utf-8");

  // Create a module-like wrapper that captures the function
  // but doesn't run main()
  const wrappedSource = source
    // Strip the shebang line (causes SyntaxError in vm.runInThisContext)
    .replace(/^#!.*\n/, "")
    // Replace the main() call at the bottom with an export
    .replace(/^main\(\);?\s*$/m, "// main() call removed by adapter")
    // Make loadYamlModule use our local yaml
    .replace(
      /function loadYamlModule\(repoRoot\)\s*\{[\s\S]*?\n\}/,
      'function loadYamlModule(repoRoot) { return require("yaml"); }'
    );

  // Create a module sandbox
  const Module = require("module");
  const m = new Module("deterministic-adapter-sandbox");
  m.paths = [
    path.join(__dirname, "node_modules"),
    ...Module._nodeModulePaths(__dirname),
  ];

  // Compile and run, capturing evaluateCase
  const wrapper = Module.wrap(
    wrappedSource + "\nmodule.exports = { evaluateCase };"
  );
  const compiledWrapper = require("vm").runInThisContext(wrapper);
  compiledWrapper(m.exports, (id) => {
    if (id === "yaml") {
      return yaml;
    }
    return require(id);
  }, m, __filename, __dirname);

  return m.exports.evaluateCase;
}

let _evaluateCase = null;
function getEvaluateCase() {
  if (!_evaluateCase) {
    _evaluateCase = loadEvaluateCase();
  }
  return _evaluateCase;
}

/**
 * Extract YAML content from model output.
 * Models may wrap YAML in markdown code fences or include preamble text.
 */
function extractYamlFromOutput(output) {
  if (!output || typeof output !== "string") {
    return null;
  }

  // Try to find YAML in code fences first
  const fenceMatch = output.match(/```(?:yaml|yml)?\s*\n([\s\S]*?)```/);
  if (fenceMatch) {
    return fenceMatch[1].trim();
  }

  // Try the whole output as YAML (skip any leading prose before "deck:")
  const deckStart = output.indexOf("deck:");
  if (deckStart !== -1) {
    return output.slice(deckStart).trim();
  }

  // Last resort: try the entire output
  return output.trim();
}

/**
 * Main assertion handler for Promptfoo.
 *
 * Promptfoo custom assertions are JS modules that export a default function
 * or an object with an `assert` method. The function receives:
 *   { output, context }
 * And must return:
 *   { pass: boolean, score: number, reason: string }
 */
module.exports = async function (output, context) {
  const evaluateCase = getEvaluateCase();

  // Extract case definition from test vars
  const caseDef = context.vars._caseDef;
  if (!caseDef) {
    return {
      pass: false,
      score: 0,
      reason:
        "Missing _caseDef in test vars. The test case must include a _caseDef variable with the case definition from cases.json.",
    };
  }

  // Parse the model output as YAML
  const yamlContent = extractYamlFromOutput(output);
  if (!yamlContent) {
    return {
      pass: false,
      score: 0,
      reason: "Could not extract YAML content from model output.",
    };
  }

  let parsed;
  try {
    parsed = yaml.parse(yamlContent);
  } catch (err) {
    return {
      pass: false,
      score: 0,
      reason: `YAML parse error: ${err.message}`,
    };
  }

  if (!parsed || !parsed.deck || !parsed.cards) {
    return {
      pass: false,
      score: 0,
      reason: `Parsed YAML does not have expected deck/cards structure. Keys found: ${Object.keys(parsed || {}).join(", ")}`,
    };
  }

  // Write parsed YAML to a temp file for evaluateCase (it reads from disk)
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "promptfoo-eval-"));
  const tmpYamlPath = path.join(tmpDir, "output.flashcards.yaml");
  fs.writeFileSync(tmpYamlPath, yamlContent);

  // Construct a trialDef matching what evaluateCase expects
  const trialDef = {
    deck_paths: [tmpYamlPath],
  };

  try {
    // evaluateCase expects (caseDef, trialDef, repoRoot)
    // But our temp file is an absolute path, so we pass "/" as repoRoot
    // so that path.resolve("/", absPath) === absPath
    const result = evaluateCase(caseDef, trialDef, "/");

    // Clean up temp files
    try {
      fs.unlinkSync(tmpYamlPath);
      fs.rmdirSync(tmpDir);
    } catch {
      // Best effort cleanup
    }

    // Translate to Promptfoo assertion format
    const score = result.deterministic_score_100 / 100; // Promptfoo uses 0-1 scale
    const pass = result.hard_pass;

    // Build a human-readable reason from the check results
    const failedChecks = result.checks
      .filter((c) => !c.pass)
      .map((c) => `${c.id}: ${c.details || "FAILED"}${c.hard ? " [HARD]" : ""}`)
      .join("\n  ");

    const passedChecks = result.checks
      .filter((c) => c.pass)
      .map((c) => c.id)
      .join(", ");

    const statsStr = Object.entries(result.stats)
      .map(([k, v]) => `${k}=${v}`)
      .join(", ");

    let reason;
    if (pass) {
      reason = `All hard gates passed. Score: ${result.deterministic_score_100}/100.\nStats: ${statsStr}\nPassed: ${passedChecks}`;
    } else {
      reason = `Hard gate failure. Score: ${result.deterministic_score_100}/100.\nFailed checks:\n  ${failedChecks}\nStats: ${statsStr}`;
    }

    return {
      pass,
      score,
      reason,
    };
  } catch (err) {
    // Clean up temp files on error
    try {
      fs.unlinkSync(tmpYamlPath);
      fs.rmdirSync(tmpDir);
    } catch {
      // Best effort cleanup
    }

    return {
      pass: false,
      score: 0,
      reason: `evaluateCase threw an error: ${err.message}\n${err.stack}`,
    };
  }
};
