# Promptfoo Deep-Dive: Technical Reference for Eval Architecture

**Date**: 2026-02-26
**Purpose**: Engineering reference for integrating Promptfoo into our flashcards skill eval harness and future agent eval pipelines.

---

## 1. Feature Reference

### 1.1 Simulated User Provider

**Provider ID**: `promptfoo:simulated-user`

Facilitates multi-turn conversation between a simulated user (controlled by Promptfoo) and an agent under test.

**Configuration Parameters**:

| Parameter         | Type                    | Default | Description                                                                 |
|-------------------|-------------------------|---------|-----------------------------------------------------------------------------|
| `instructions`    | string                  | —       | Persona/behavior template. Supports Nunjucks variables from test `vars`.    |
| `maxTurns`        | number                  | 10      | Max conversation turns. Counts only NEW turns after `initialMessages`.      |
| `initialMessages` | Message[] or string     | —       | Pre-seeded conversation history. Supports `file://` paths (JSON/YAML).      |

**initialMessages format** (OpenAI chat structure):
```yaml
initialMessages:
  - role: user
    content: "Message text with {{variable}} support"
  - role: assistant
    content: "Response text"
```

**Stop conditions**: (1) `maxTurns` reached, (2) agent outputs `###STOP###`, (3) error.

**Communication protocol**: Agent must accept OpenAI-compatible `Messages[]` format with `role` and `content` fields. Function-calling agents require function definitions in provider config.

**Variable access**: Test-level `vars` pass to custom providers via `context['vars']['key']`.

**Config example**:
```yaml
providers:
  - id: promptfoo:simulated-user
    config:
      instructions: |
        You are a {{student_level}} student studying {{topic}}.
        Ask follow-up questions when confused.
        Try to get help with: {{learning_goal}}.
      maxTurns: 6
      initialMessages:
        - role: user
          content: "I'm studying {{topic}} and need help understanding the basics."

tests:
  - vars:
      student_level: beginner
      topic: agent memory systems
      learning_goal: understand when to use RAG vs fine-tuning
```

**Limitations**:
- Requires OpenAI chat message format (no custom message schemas)
- Simulated user responses generated remotely by default (disable with `PROMPTFOO_DISABLE_REMOTE_GENERATION=true`)
- Your agent runs locally but the simulated user runs on Promptfoo's servers
- No built-in persona validation (persona adherence must be asserted separately)

---

### 1.2 Multi-Turn Chat Configuration

**The `_conversation` variable**: Built-in variable containing full prompt and previous turns.

**Type structure**:
```typescript
type Completion = {
  prompt: string | object;
  input: string;    // last user message
  output: string;   // assistant's response
};
type Conversation = Completion[];
```

**Conversation isolation via `conversationId`**: Each unique ID maintains separate history.
```yaml
tests:
  - vars:
      question: "Who founded Facebook?"
    metadata:
      conversationId: "conversation1"
  - vars:
      question: "Where does he live?"
    metadata:
      conversationId: "conversation1"
```

**Prompt template for multi-turn**:
```json
[
  {% for completion in _conversation %}
    {"role": "user", "content": "{{ completion.input }}"},
    {"role": "assistant", "content": "{{ completion.output }}"},
  {% endfor %}
  {"role": "user", "content": "{{ question }}"}
]
```

**State preservation with `storeOutputAs`**: Capture outputs for reuse:
```yaml
tests:
  - vars:
      message: "What's your favorite fruit?"
    options:
      storeOutputAs: favoriteFruit
  - vars:
      message: "Why do you like {{favoriteFruit}} so much?"
```

Transform before storage: `transform: output.split(' ')[0]`

**Critical concurrency caveat**: When `_conversation` is present, eval runs single-threaded (concurrency = 1). This significantly impacts performance on large test suites.

**Assertion gap**: The docs do NOT explicitly document turn-level vs session-level assertions for multi-turn conversations. Assertions appear to apply to the final output of each test case, not to intermediate turns.

---

### 1.3 Custom JavaScript Assertions

**Return types** (in order of complexity):

1. **Boolean**: Simple pass/fail
2. **Number**: Score value (use with `threshold` parameter)
3. **GradingResult object** (most powerful):
```typescript
{
  pass: boolean;
  score: number;
  reason: string;
  componentResults?: GradingResult[];  // Sub-assertions shown in UI modals
}
```

**Available context variables** (the `context` parameter):

| Property           | Type                              | Description                          |
|--------------------|-----------------------------------|--------------------------------------|
| `prompt`           | string                            | Raw prompt sent to LLM              |
| `vars`             | Record<string, string \| object>  | Test case variables                  |
| `test`             | TestCase                          | Complete test case info              |
| `logProbs`         | number[]                          | Log probabilities (if available)     |
| `config`           | object                            | Config passed to assertion           |
| `provider`         | object                            | Provider that generated response     |
| `providerResponse` | object                            | Complete provider response           |
| `trace`            | object                            | OpenTelemetry trace data             |

**Implementation methods**:

```yaml
# Inline single-line
assert:
  - type: javascript
    value: "output.includes('Hello')"

# Multiline
assert:
  - type: javascript
    value: |
      if (output === 'Expected') return { pass: true, score: 1.0 };
      return { pass: false, score: 0, reason: 'Mismatch' };

# External file (CommonJS)
assert:
  - type: javascript
    value: file://path/to/grader.js

# External file with named export
assert:
  - type: javascript
    value: file://path/to/grader.js:customFunction
```

**External file signature**:
```javascript
module.exports = (output, context) => {
  // output: string (the LLM response)
  // context: { prompt, vars, test, config, provider, providerResponse, ... }
  return { pass: true, score: 0.95, reason: 'Looks good' };
};
```

**Async supported**: External files can use `async` functions for external validation.

**Scoring with threshold**:
```yaml
assert:
  - type: javascript
    value: "Math.log(output.length) * 10"
    threshold: 0.5  # score must exceed this to pass
```

---

### 1.4 Custom Providers

**Provider interface** (minimum requirements):
```javascript
module.exports = class MyProvider {
  constructor(options) {
    this.providerId = options.id;
    this.config = options.config;
  }

  id() { return this.providerId; }

  async callApi(prompt, context, options) {
    // prompt: string — the rendered prompt
    // context: { vars, prompt config, test metadata }
    // Returns ProviderResponse
    return {
      output: "response text",          // required
      error: undefined,                  // optional
      tokenUsage: { total: 100, prompt: 40, completion: 60 }, // optional
      cost: 0.002,                       // optional
      cached: false,                     // optional
      metadata: {},                      // optional
    };
  }
};
```

**Supported file formats**: `.js` (CommonJS), `.cjs`, `.mjs` (ESM), `.ts` (TypeScript).

**Configuration**:
```yaml
providers:
  - id: file://./providers/tutorclaw.js
    label: "TutorClaw Agent"
    config:
      model: "claude-sonnet-4-6"
      apiEndpoint: "http://localhost:8000"
      systemPrompt: "You are a tutor..."
```

**Multiple instances**: Same file path with different configs creates separate provider instances.

**Caching utility**: `promptfoo.cache.fetchWithCache(url, options, timeout)` wraps HTTP calls with built-in caching, returns `{data, cached}`.

**Actual prompt reporting**: Return `prompt` in response to show what was actually sent to the LLM (useful for agents that build multi-turn conversations internally).

---

### 1.5 Anthropic Provider Configuration

**Model IDs** (Messages API):
- `anthropic:messages:claude-opus-4-6`
- `anthropic:messages:claude-sonnet-4-6`
- `anthropic:messages:claude-haiku-4-5-20251001`
- `anthropic:messages:claude-3-5-sonnet-20241022`
- `anthropic:messages:claude-3-haiku-20240307`

**Key config parameters**:

| Parameter      | Default | Notes                                                      |
|----------------|---------|-------------------------------------------------------------|
| `temperature`  | 0       | Controls randomness                                         |
| `max_tokens`   | 1024    | Maximum response length                                     |
| `top_p`        | —       | Nucleus sampling                                            |
| `top_k`        | —       | Token sampling limit                                        |
| `tools`        | —       | Function/tool definitions                                   |
| `tool_choice`  | —       | Specific tool invocation                                    |
| `thinking`     | —       | Extended thinking: `adaptive`, `enabled`, or `disabled`     |
| `showThinking` | true    | Include reasoning in output                                 |

**Cost tracking**: Automatic per-request cost calculation based on model-specific pricing and token consumption. Token usage metrics include prompt, completion, and total counts.

**Multi-model comparison config**:
```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: "Sonnet 4.6"
    config:
      temperature: 0
      max_tokens: 4096
  - id: anthropic:messages:claude-haiku-4-5-20251001
    label: "Haiku 4.5"
    config:
      temperature: 0
      max_tokens: 4096
```

---

### 1.6 Assertion Composition and Scoring

**Weighted averaging**: Final test score = `sum(score * weight) / sum(weights)` across all assertions.

**Test-level threshold**: Optional `threshold` on test case determines pass/fail based on combined weighted score.

**Assertion sets** (grouped assertions with collective threshold):
```yaml
assert:
  - type: assert-set
    threshold: 0.5  # 50% of grouped assertions must pass
    assert:
      - type: cost
        threshold: 0.001
      - type: latency
        threshold: 200
```

**Named metrics** (for aggregation in UI):
```yaml
assert:
  - type: javascript
    value: "output.length > 100"
    metric: "ContentLength"
  - type: llm-rubric
    value: "Is factually accurate"
    metric: "Accuracy"
```

**Derived metrics** (post-evaluation composites):
```yaml
derivedMetrics:
  - name: f1_score
    value: "2 * precision * recall / (precision + recall)"
  - name: weighted_quality
    value: "deterministic_score * 0.4 + llm_score * 0.6"
```

**Custom scoring function** (override weighted averaging):
```yaml
defaultTest:
  options:
    scoring: file://scoring.js
```
```javascript
// scoring.js
module.exports = (namedScores, context) => ({
  pass: namedScores.Accuracy >= 0.8 && namedScores.Format >= 0.9,
  score: namedScores.Accuracy * 0.6 + namedScores.Format * 0.4,
  reason: "Custom composite scoring"
});
```

**Negation**: Prepend `not-` to any assertion type (e.g., `not-contains`, `not-regex`).

**Weight zero**: `weight: 0` auto-passes assertion without affecting composite score (tracking only).

---

### 1.7 YAML Configuration Reference

**Full config schema** (top-level keys):
```yaml
description: "What the eval tests"
tags:
  env: production
  team: flashcards

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    config: { temperature: 0, max_tokens: 4096 }

prompts:
  - file://prompts/flashcard-generator.txt
  - file://prompts/flashcard-generator-v2.txt

defaultTest:
  assert:
    - type: javascript
      value: file://graders/deterministic-adapter.js
  options:
    provider: anthropic:messages:claude-haiku-4-5-20251001  # grading provider

tests: file://datasets/cases.yaml

evaluateOptions:
  maxConcurrency: 4
  repeat: 3           # run each test 3 times
  delay: 100          # ms between calls
  cache: true         # disk cache (default)
  timeoutMs: 60000    # per-test timeout

outputPath: results.json

extensions:
  - file://hooks.js:extensionHook
```

**Extension hooks** (lifecycle):
- `beforeAll(context: { suite })` — before evaluation starts
- `afterAll(context: { results, suite })` — after all tests complete
- `beforeEach(context: { test })` — before each test case
- `afterEach(context: { test, result })` — after each test case

**File protocol**: `file://path/to/file.json` for loading vars, tests, assertions, prompts, providers, transforms.

**Variable substitution**: Nunjucks templating: `{{variable}}`, `{{var | filter}}`.

---

### 1.8 GitHub Actions Integration

**Workflow setup**:
```yaml
name: Prompt Evaluation
on:
  pull_request:
    paths: ["prompts/**", "evals/**"]
permissions:
  pull-requests: write

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: ${{ runner.os }}-promptfoo-v1
      - uses: promptfoo/promptfoo-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config: evals/promptfooconfig.yaml
```

**Cost management in CI**:
- Disk caching (`~/.cache/promptfoo`) persists LLM responses across runs
- Use `--no-cache` to force fresh responses when needed
- `PROMPTFOO_CACHE_PATH` environment variable controls cache location
- The action automatically posts results as PR comments with a web viewer link

**Environment variables**: `ANTHROPIC_API_KEY`, `PROMPTFOO_CONFIG_DIR`, `PROMPTFOO_CACHE_PATH`.

---

### 1.9 Repeat / pass@k Behavior

**The `--repeat` flag**: `promptfoo eval --repeat 3` runs each test case N times.

**`evaluateOptions.repeat`**: Same behavior in YAML config.

**Aggregation across repeats**: The documentation does NOT specify a built-in pass@k aggregation mechanism. Results from repeated runs appear as separate rows in the output. There is no native `pass@k` or `pass^k` computation.

---

## 2. Integration Assessment

### 2.1 deterministic.js (25 checks) --> Promptfoo Custom Assertion

**Current interface**: `evaluateCase(caseDef, trialDef, repoRoot)` returns:
```javascript
{
  hard_pass: boolean,
  deterministic_score_100: number,
  checks: Array<{ id, pass, hard, weight, details }>,
  stats: { deck_count, card_count_total, recall_count, ... }
}
```

**Can it be used AS-IS?** No. It needs an adapter. Here is why:

1. **Input mismatch**: `deterministic.js` reads from filesystem (manifest paths, YAML deck files). Promptfoo passes `(output, context)` where `output` is the LLM's text response.

2. **Output mismatch**: Promptfoo expects `{ pass, score, reason, componentResults? }`. Our grader returns `{ hard_pass, deterministic_score_100, checks, stats }`.

3. **Filesystem dependency**: Our grader reads YAML deck files from disk. In a Promptfoo flow, the output IS the generated content (either raw text or structured output). The grader would need to parse the output directly rather than reading files.

**Adapter requirements** (see Section 3.1 for full adapter code pattern).

### 2.2 llm-judge.js (15 criteria) --> Promptfoo LLM-Rubric

**Current interface**: Builds a prompt via `buildPrompt()`, spawns `claude -p`, parses JSON response with 15 scored criteria.

**Promptfoo equivalent**: The `llm-rubric` assertion type with a custom `rubricPrompt` covers this use case. However, our LLM judge has specific behavior:
- Inline rubric with 15 named criteria each scored 0-10
- Critical keys subset with a threshold (all >= 8.0 AND overall >= 82)
- Custom JSON schema enforcement

**Integration path**: Use `llm-rubric` with our existing prompt as the `rubricPrompt`, then use a JavaScript assertion to parse and validate the structured response against our critical thresholds.

### 2.3 Simulated User for Student Conversations

**Can Promptfoo replicate student conversations?** Yes, with caveats.

The `promptfoo:simulated-user` provider supports:
- Persona constraints via `instructions` (Nunjucks-templated)
- Multi-turn conversation with configurable `maxTurns`
- Pre-seeded conversations via `initialMessages`

**What it CANNOT do natively**:
- Validate that the simulated user stays in persona (need a separate assertion)
- Enforce specific pedagogical patterns (e.g., "ask a misconception question on turn 3")
- Control turn-by-turn behavior granularly (instructions are global, not per-turn)

### 2.4 Multi-Model Comparison

**Fully supported**. Multiple providers run the same test suite:
```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: "Sonnet 4.6"
  - id: anthropic:messages:claude-haiku-4-5-20251001
    label: "Haiku 4.5"
```

Results displayed in a comparison matrix with per-provider columns. Cost tracking is automatic per model.

### 2.5 Skills Eval + Agent Eval Unified Config

**Can we use Promptfoo for both?** Yes, with different config files sharing common patterns.

- **Skills eval** (flashcards): Standard prompt-in/structured-output eval with custom assertions
- **Agent eval** (TutorClaw): Custom provider wrapping our agent + simulated user for multi-turn

Both use the same assertion framework, scoring, and reporting. The difference is the provider layer.

---

## 3. Adapter Requirements

### 3.1 Deterministic Grader Adapter

Our `deterministic.js` expects filesystem-based inputs. For Promptfoo, we need an adapter that:

1. Takes `output` (the LLM's raw response) and `context` (test vars)
2. Parses the output as YAML deck(s) in-memory
3. Runs the same 25 checks against the parsed structure
4. Returns a Promptfoo-compatible `GradingResult`

**Adapter pattern**:
```javascript
// evals/flashcards/graders/promptfoo-deterministic-adapter.js
const yaml = require('yaml');

/**
 * Adapter: wraps our 25 deterministic checks for Promptfoo's assertion interface.
 *
 * Expects:
 *   output: string — raw YAML output from the LLM
 *   context.vars: { case_id, expected, ... } — test case metadata from cases.json
 *   context.config: {} — optional adapter config
 */
module.exports = (output, context) => {
  const { vars } = context;
  const expected = vars.expected || {};

  // Parse the LLM output as YAML deck(s)
  let parsedDecks;
  try {
    parsedDecks = parseDecksFromOutput(output);
  } catch (err) {
    return {
      pass: false,
      score: 0,
      reason: `Failed to parse output as YAML: ${err.message}`,
    };
  }

  // Run all 25 checks against parsed decks (reuse evaluateCase logic)
  const result = evaluateInMemory(expected, parsedDecks);

  // Map to Promptfoo GradingResult
  return {
    pass: result.hard_pass,
    score: result.deterministic_score_100 / 100,
    reason: result.hard_pass
      ? `All hard gates passed. Score: ${result.deterministic_score_100}/100`
      : `Hard gate failure. Score: ${result.deterministic_score_100}/100`,
    componentResults: result.checks.map(chk => ({
      pass: chk.pass,
      score: chk.pass ? 1 : 0,
      reason: `[${chk.id}] ${chk.details}`,
    })),
  };
};
```

**Effort estimate**: Medium. The core `evaluateCase` logic needs refactoring to accept in-memory parsed decks instead of filesystem paths. ~200 lines of adapter code, plus refactoring `evaluateCase` to decouple from `fs.readFileSync`.

### 3.2 LLM Judge Adapter

Two options:

**Option A: Use Promptfoo's llm-rubric with custom rubricPrompt**
```yaml
assert:
  - type: llm-rubric
    provider: anthropic:messages:claude-haiku-4-5-20251001
    value: file://graders/llm-rubric-criteria.txt
    config:
      rubricPrompt: file://graders/llm-judge-prompt-template.txt
```

This is simpler but loses our custom JSON schema enforcement and critical-key threshold logic.

**Option B: Use a JavaScript assertion that invokes our LLM judge internally**
```javascript
// evals/flashcards/graders/promptfoo-llm-judge-adapter.js
module.exports = async (output, context) => {
  const prompt = buildPrompt(context.vars, output);
  const response = await callLLMJudge(prompt, context.config.model);
  const criteria = normalizeCriteria(response.criteria);
  const criticalPass = CRITICAL_KEYS.every(k => criteria[k].score_10 >= 8.0);

  return {
    pass: criticalPass && overallScore >= 82,
    score: overallScore / 100,
    reason: criticalPass ? 'All critical criteria met' : 'Critical criteria failed',
    componentResults: Object.entries(criteria).map(([key, val]) => ({
      pass: val.score_10 >= 8.0,
      score: val.score_10 / 10,
      reason: `[${key}] ${val.rationale}`,
    })),
  };
};
```

**Recommendation**: Option B. It preserves our exact grading semantics and lets us display all 15 criteria as `componentResults` in Promptfoo's UI.

### 3.3 TutorClaw Custom Provider

To evaluate TutorClaw as an agent, wrap it as a Promptfoo provider:

```javascript
// evals/agent/providers/tutorclaw-provider.js
module.exports = class TutorClawProvider {
  constructor(options) {
    this.id = () => options.id || 'tutorclaw';
    this.config = options.config || {};
    this.apiEndpoint = this.config.apiEndpoint || 'http://localhost:8000';
  }

  async callApi(prompt, context) {
    // prompt contains the full conversation history in OpenAI format
    const messages = JSON.parse(prompt);
    const response = await fetch(`${this.apiEndpoint}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        model: this.config.model || 'claude-sonnet-4-6',
      }),
    });
    const data = await response.json();

    return {
      output: data.content,
      tokenUsage: {
        total: data.usage?.total_tokens || 0,
        prompt: data.usage?.prompt_tokens || 0,
        completion: data.usage?.completion_tokens || 0,
      },
      cost: data.usage?.cost || 0,
    };
  }
};
```

### 3.4 Test Cases Adapter

Our `cases.json` needs transformation to Promptfoo's test format:

```yaml
# promptfooconfig.yaml
tests:
  - description: "F01: Explicit dual prompt, single lesson"
    vars:
      case_id: F01_explicit_dual_prompt_single_lesson
      source_lessons:
        - evals/flashcards/fixtures/lessons/f01-agent-memory-basics.md
      user_prompt: "Act as an expert study aid creator..."
      expected:
        should_generate: true
        target_decks: 1
        min_cards: 8
        max_cards: 16
        recall_ratio_min: 0.45
        recall_ratio_max: 0.55
    assert:
      - type: javascript
        value: file://graders/promptfoo-deterministic-adapter.js
        metric: DeterministicScore
      - type: javascript
        value: file://graders/promptfoo-llm-judge-adapter.js
        metric: LLMJudgeScore
```

**Effort**: A script to convert `cases.json` to Promptfoo test YAML. ~50 lines.

---

## 4. Limitations and Gaps

### 4.1 No Native pass@k / pass^k

**Gap**: Promptfoo has `--repeat` to run tests multiple times but does NOT compute pass@k or pass^k natively. Our `aggregate.js` computes:
- `pass@1`: First trial passes hard gates
- `pass@k`: ANY trial passes hard gates
- `pass^k`: ALL trials pass hard gates

**Workaround**: Use `evaluateOptions.repeat: N` to generate N results per test, then use an `afterAll` extension hook to compute pass@k/pass^k from raw results.

```javascript
// extensions/pass-at-k.js
module.exports = {
  afterAll: (context) => {
    const { results } = context;
    // Group results by test description
    // Compute pass@1, pass@k, pass^k per group
    // Write to custom summary file
  }
};
```

**Alternative**: Keep our `aggregate.js` as a post-processing step that reads Promptfoo's JSON output.

### 4.2 Multi-Turn Assertion Granularity

**Gap**: No documented support for turn-level assertions in multi-turn conversations. Assertions apply to the final output of each test case. You cannot assert "turn 3 should contain X and turn 5 should contain Y."

**Workaround**: Use the simulated user provider and write a JavaScript assertion that receives the full conversation history (accessible via `context.providerResponse`) and validates per-turn expectations.

### 4.3 Filesystem-Dependent Graders

**Gap**: Our graders read deck YAML files from disk. In Promptfoo, the LLM output is passed as a string. If the skill under test writes files to disk (as our flashcard generator does), we need either:
- A custom provider that runs the skill, captures file outputs, and returns them as the provider's `output`
- A post-processing step that reads generated files

### 4.4 Single-Threaded Multi-Turn

**Limitation**: When using `_conversation`, eval runs at concurrency 1. For large multi-turn test suites, this is a significant performance bottleneck. The simulated user provider inherently uses multi-turn, so all simulated user evals will be sequential.

### 4.5 Remote Simulated User

**Privacy concern**: By default, the simulated user's responses are generated on Promptfoo's servers. Our lesson content and test scenarios would be sent to their API. Set `PROMPTFOO_DISABLE_REMOTE_GENERATION=true` to disable, but this may limit simulated user capabilities.

### 4.6 No Built-In Consistency Score

**Gap**: Our `aggregate.js` computes a `consistency_score` based on stddev of deterministic scores and recall ratios across trials. Promptfoo has no native equivalent. This must remain a post-processing step.

### 4.7 No Baseline Comparison

**Gap**: Our harness supports `--baseline <summary.json>` to compute deltas against a previous run. Promptfoo does not have native baseline diff functionality. The GitHub Action does show before/after for prompt changes, but not structured score regression tracking.

**Workaround**: Keep our `aggregate.js` as the aggregation layer, feeding it Promptfoo's raw JSON output.

---

## 5. Recommended Configuration Patterns

### 5.1 Flashcard Skills Eval (Drop-In Replacement)

```yaml
# evals/flashcards/promptfooconfig.yaml
description: "Flashcard Skill Quality Eval"

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: "Sonnet 4.6"
    config:
      temperature: 0
      max_tokens: 8192
  - id: anthropic:messages:claude-haiku-4-5-20251001
    label: "Haiku 4.5"
    config:
      temperature: 0
      max_tokens: 8192

prompts:
  - file://prompts/flashcard-generator.txt

defaultTest:
  options:
    provider: anthropic:messages:claude-haiku-4-5-20251001  # grading LLM
  assert:
    - type: javascript
      value: file://graders/promptfoo-deterministic-adapter.js
      metric: DeterministicScore
      weight: 1
    - type: javascript
      value: file://graders/promptfoo-llm-judge-adapter.js
      metric: LLMJudgeScore
      weight: 1

tests: file://datasets/promptfoo-cases.yaml

evaluateOptions:
  maxConcurrency: 4
  repeat: 3
  cache: true
  timeoutMs: 120000

extensions:
  - file://extensions/pass-at-k.js

outputPath: reports/latest.json

derivedMetrics:
  - name: composite_quality
    value: "DeterministicScore * 0.4 + LLMJudgeScore * 0.6"
```

### 5.2 Agent Eval (TutorClaw Multi-Turn)

```yaml
# evals/agent/promptfooconfig.yaml
description: "TutorClaw Agent Conversation Eval"

providers:
  - id: file://providers/tutorclaw-provider.js
    label: "TutorClaw"
    config:
      apiEndpoint: http://localhost:8000
      model: claude-sonnet-4-6

  - id: promptfoo:simulated-user
    config:
      instructions: |
        You are a {{student_level}} student learning about {{topic}}.
        Your goal: {{learning_goal}}.
        If the tutor's explanation is unclear, ask for clarification.
        If you receive a good explanation, acknowledge it and ask a follow-up.
        Stay in character. Don't break the student persona.
      maxTurns: 8

prompts:
  - file://prompts/tutor-system.txt

tests:
  - description: "Beginner asks about agent memory"
    vars:
      student_level: beginner
      topic: agent memory systems
      learning_goal: understand when to use RAG vs fine-tuning
    assert:
      - type: javascript
        value: |
          // Conversation quality checks
          const turns = JSON.parse(context.providerResponse.raw || '[]');
          const tutorResponses = turns.filter(t => t.role === 'assistant');
          const allHaveContent = tutorResponses.every(t => t.content.length > 50);
          const noHallucination = !tutorResponses.some(t =>
            t.content.includes('I made that up')
          );
          return {
            pass: allHaveContent && noHallucination,
            score: allHaveContent && noHallucination ? 1 : 0,
            reason: allHaveContent ? 'All responses substantive' : 'Some responses too short'
          };
        metric: ConversationQuality
      - type: llm-rubric
        value: |
          The tutor should:
          1. Explain concepts at a beginner level
          2. Use analogies or examples
          3. Not use jargon without defining it
          4. Answer follow-up questions appropriately
        metric: PedagogicalQuality

evaluateOptions:
  maxConcurrency: 1  # forced by multi-turn anyway
  repeat: 2
  timeoutMs: 300000  # 5 min for multi-turn conversations
```

### 5.3 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/eval.yml
name: Eval Suite
on:
  pull_request:
    paths: ["evals/**", "apps/study-mode-api/**"]
  workflow_dispatch:

permissions:
  pull-requests: write

jobs:
  flashcard-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: ${{ runner.os }}-promptfoo-v1

      - name: Install promptfoo
        run: npm install -g promptfoo

      - name: Run flashcard eval
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd evals/flashcards
          promptfoo eval -c promptfooconfig.yaml \
            --output reports/ci-${{ github.sha }}.json \
            --no-progress-bar

      - name: Post-process (pass@k, baseline diff)
        run: |
          node evals/flashcards/graders/aggregate.js \
            --promptfoo-results reports/ci-${{ github.sha }}.json \
            --baseline evals/flashcards/baselines/baseline-v2.json \
            --output-json reports/ci-summary.json \
            --output-md reports/ci-summary.md

      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          path: evals/flashcards/reports/ci-summary.md
```

### 5.4 Hybrid Architecture (Recommended)

Given the gaps identified, the recommended architecture uses Promptfoo for what it does well and retains our custom tooling for what it does not:

```
                    promptfooconfig.yaml
                           |
                    promptfoo eval
                    /              \
          [providers]           [assertions]
          /         \           /           \
   Anthropic API   Custom    JS Adapter    llm-rubric
   (direct model)  Provider  (25 checks)   (15 criteria)
                   (TutorClaw)
                           |
                    raw results JSON
                           |
                    aggregate.js (post-process)
                    /              \
              pass@k/pass^k    baseline diff
              consistency       summary.md
```

**What Promptfoo handles**:
- Provider orchestration (model comparison, API management)
- Test case management (YAML datasets, variable substitution)
- Assertion framework (hosting our custom JS + built-in assertions)
- Cost tracking (automatic per-model)
- Caching (avoid redundant API calls)
- CI integration (GitHub Action, PR comments)
- UI/reporting (web viewer, HTML reports)

**What we keep custom**:
- `aggregate.js` for pass@k/pass^k/pass^k computation
- Baseline diffing
- Consistency scoring
- The 25+15 grading logic (wrapped in Promptfoo-compatible adapters)

---

## 6. Answers to Specific Questions

### Q1: Can our deterministic.js be used as a Promptfoo custom assertion AS-IS?

**No.** It needs an adapter because:
- It reads files from disk; Promptfoo passes output as a string
- It returns `{ hard_pass, deterministic_score_100, checks }` not `{ pass, score, reason }`
- It expects `caseDef` and `trialDef` objects; Promptfoo provides `(output, context)`

The adapter is ~200 lines. The core `evaluateCase` function can be refactored to accept parsed data instead of file paths, then the adapter wraps it with Promptfoo's interface.

### Q2: Can Promptfoo's simulated user replicate a student conversation with persona constraints?

**Yes, partially.** The `instructions` field supports persona definition with Nunjucks variables. It can simulate a student with a specific knowledge level, topic interest, and learning goal. However:
- No per-turn behavior control (e.g., "ask a misconception on turn 3")
- No validation that the simulated user stays in persona (needs separate assertion)
- Simulated user responses generated remotely by default (privacy concern for lesson content)
- No built-in pedagogical patterns (Socratic questioning, scaffolding)

### Q3: How does Promptfoo handle pass@k / pass^k?

**It does not have native support.** The `--repeat N` / `evaluateOptions.repeat: N` flag runs tests multiple times, but results appear as separate rows. There is no built-in pass@k or pass^k aggregation.

**Our solution**: Use an `afterAll` extension hook or keep our `aggregate.js` as a post-processing step that reads Promptfoo's JSON output and computes pass@1, pass@k, pass^k.

### Q4: Maximum assertion complexity?

**No documented limit.** Promptfoo supports an arbitrary number of assertions per test case. You can run all 25 deterministic checks + 15 LLM criteria in one eval using two JavaScript assertions (one for deterministic, one for LLM judge), each returning `componentResults` arrays that display all individual checks in the UI.

The `componentResults` field on `GradingResult` supports nested sub-assertions, so all 40 checks can be surfaced individually.

### Q5: Cost tracking per model?

**Yes, automatic.** Promptfoo tracks token usage and computes cost per request based on model-specific pricing. When comparing multiple models, the UI shows per-provider cost columns. The `cost` assertion type can enforce cost thresholds:
```yaml
assert:
  - type: cost
    threshold: 0.01  # fail if request costs more than $0.01
```

Custom providers can also report cost via the `cost` field in `ProviderResponse`.

### Q6: Skills eval + agent eval with same config patterns?

**Yes.** Both use the same YAML config structure, assertion framework, and reporting. The difference is:

| Dimension        | Skills Eval (Flashcards)         | Agent Eval (TutorClaw)               |
|------------------|----------------------------------|--------------------------------------|
| Provider         | `anthropic:messages:claude-*`    | `file://providers/tutorclaw.js`      |
| Prompt           | Static template                  | System prompt + conversation history |
| Multi-turn       | No (single generation)           | Yes (simulated-user provider)        |
| Assertions       | Custom JS (deterministic + LLM)  | Custom JS + llm-rubric               |
| Concurrency      | Parallel (maxConcurrency: 4+)    | Sequential (concurrency: 1)          |
| Repeat           | 3+ trials for pass@k             | 2 trials (multi-turn is expensive)   |

Shared patterns: assertion framework, file:// references, YAML config structure, scoring, named metrics, derived metrics, extension hooks, GitHub Action integration.
