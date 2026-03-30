#!/usr/bin/env node

/**
 * Standalone test of the deterministic adapter.
 * Uses the golden output from F01 as the "model output" to verify
 * the adapter correctly bridges to evaluateCase().
 */

const fs = require("fs");
const path = require("path");
const adapter = require("./deterministic-adapter");

// Load the golden output as if it were model output
const goldenPath = path.resolve(
  __dirname,
  "../flashcards/fixtures/outputs/f01-agent-memory-basics.flashcards.yaml"
);
const goldenYaml = fs.readFileSync(goldenPath, "utf-8");

// Construct the case definition (matching F01 from cases.json)
const caseDef = {
  id: "F01_explicit_dual_prompt_single_lesson",
  name: "Explicit Dual Prompt Single Lesson",
  scenario: "explicit_trigger",
  input: {
    source_lessons: [
      "evals/flashcards/fixtures/lessons/f01-agent-memory-basics.md",
    ],
    user_prompt:
      'Act as an expert study aid creator...minimum information principle...under 40 words...self-contained and atomic...focus on key terms, formulas, and relationships. Also create understanding-focused Why/How cards. Generate half from each prompt style.',
  },
  expected: {
    should_generate: true,
    target_decks: 1,
    min_cards: 8,
    max_cards: 16,
    recall_ratio_min: 0.45,
    recall_ratio_max: 0.55,
    thinking_ratio_min: 0.45,
    thinking_ratio_max: 0.55,
    thinking_front_why_how_ratio_min: 0.75,
    require_formula_focus: false,
    require_relationship_focus: true,
  },
};

async function main() {
  console.log("Testing deterministic adapter with golden output...\n");

  // Test 1: Golden output (should pass)
  console.log("=== Test 1: Golden output (expected: PASS) ===");
  const result1 = await adapter(goldenYaml, {
    vars: { _caseDef: caseDef },
  });
  console.log("Pass:", result1.pass);
  console.log("Score:", result1.score);
  console.log("Reason:", result1.reason);
  console.log();

  // Test 2: Golden output wrapped in markdown fences
  console.log("=== Test 2: Golden output in code fences (expected: PASS) ===");
  const fencedYaml = "Here is the flashcard deck:\n\n```yaml\n" + goldenYaml + "\n```\n";
  const result2 = await adapter(fencedYaml, {
    vars: { _caseDef: caseDef },
  });
  console.log("Pass:", result2.pass);
  console.log("Score:", result2.score);
  console.log("Reason:", result2.reason);
  console.log();

  // Test 3: Empty output (should fail)
  console.log("=== Test 3: Empty output (expected: FAIL) ===");
  const result3 = await adapter("", {
    vars: { _caseDef: caseDef },
  });
  console.log("Pass:", result3.pass);
  console.log("Score:", result3.score);
  console.log("Reason:", result3.reason);
  console.log();

  // Test 4: Missing caseDef (should fail gracefully)
  console.log("=== Test 4: Missing caseDef (expected: FAIL) ===");
  const result4 = await adapter(goldenYaml, {
    vars: {},
  });
  console.log("Pass:", result4.pass);
  console.log("Score:", result4.score);
  console.log("Reason:", result4.reason);
  console.log();

  // Summary
  const allPass =
    result1.pass === true &&
    result2.pass === true &&
    result3.pass === false &&
    result4.pass === false;

  console.log("=== SUMMARY ===");
  console.log(allPass ? "ALL TESTS PASSED" : "SOME TESTS FAILED");
  process.exit(allPass ? 0 : 1);
}

main().catch((err) => {
  console.error("Test runner error:", err);
  process.exit(1);
});
