# Promptfoo Proof-of-Concept Results

**Date**: 2026-02-26
**Promptfoo version**: 0.120.25
**Status**: Pipeline proven, API run blocked by missing ANTHROPIC_API_KEY

## Executive Summary

The proof-of-concept demonstrates that Promptfoo can serve as a **complement**
to our custom eval harness. The full pipeline works: prompt template loading,
variable injection, custom JavaScript assertions running our 25 deterministic
checks, and structured output with pass/fail/score. However, replacing the
custom harness entirely would require significant adaptation work that is not
justified by the benefits.

**Verdict**: Complement (Promptfoo for model comparison, custom harness for
regression testing and CI).

---

## What Was Built

### Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `promptfooconfig.yaml` | 80 | Production config: Haiku 4.5 + Sonnet 4 |
| `promptfooconfig.mock.yaml` | 70 | Mock config for pipeline testing |
| `prompt.txt` | 75 | Flashcard generation prompt |
| `deterministic-adapter.js` | 175 | Bridges deterministic.js to Promptfoo |
| `mock-provider.js` | 35 | Returns golden fixture for testing |
| `test-adapter.js` | 105 | 4 unit tests for the adapter |

### Pipeline Architecture

```
prompt.txt + test vars
        |
        v
  Promptfoo Engine
        |
        v
  Anthropic API (or mock provider)
        |
        v
  Model output (YAML flashcard deck)
        |
        v
  deterministic-adapter.js
    - Extracts YAML from output (handles code fences, preamble)
    - Writes to temp file
    - Calls evaluateCase() from deterministic.js
    - Translates check results to {pass, score, reason}
        |
        v
  Promptfoo results table + JSON output
```

## Test Results

### Pipeline Test (Mock Provider, Golden Fixture)

```
Results: 1 passed, 0 failed, 0 errors (100%)
Duration: 0s
```

The golden fixture from `f01-agent-memory-basics.flashcards.yaml` scored:
- **deterministic_score_100**: 100/100
- **hard_pass**: true
- **All 25 checks passed**, including:
  - generation_expectation_match
  - deck_count_matches_target (1 deck)
  - yaml_parse_success
  - deck_schema_valid
  - card_required_fields_present
  - card_id_pattern_full_prefix
  - recall_thinking_balance (0.50 / 0.50)
  - recall_back_max_15_words
  - thinking_back_20_40_words
  - difficulty_distribution (37.5% basic, 50% intermediate, 12.5% advanced)
  - ...and 15 more

### Adapter Unit Tests

```
Test 1: Golden output (raw YAML)     -> PASS, score=1.0
Test 2: Golden output (code fences)  -> PASS, score=1.0
Test 3: Empty output                 -> FAIL, score=0 (graceful)
Test 4: Missing caseDef              -> FAIL, score=0 (graceful)
ALL TESTS PASSED
```

### API Run (Haiku + Sonnet)

**Blocked**: ANTHROPIC_API_KEY not set in environment. Promptfoo correctly
reports the error:

```
Provider call failed during eval
  "error": "Anthropic API key is not set. Set the ANTHROPIC_API_KEY
  environment variable or add `apiKey` to the provider config."
```

The config parses correctly, prompts render correctly with variables, and
the framework correctly identifies the error as a provider-level issue
(not a config or assertion issue).

---

## Analysis: What Works Well

### 1. Custom JavaScript Assertions
Promptfoo's `type: javascript` assertions with `file://` loading work
exactly as needed. The adapter receives `(output, context)` with full
access to test variables, and returns the `{pass, score, reason}` triple.
The assertion runner is Node.js-native, so our CommonJS grader code works
without any transpilation.

### 2. Variable Injection
The `{{user_prompt}}` and `{{lesson_content}}` template variables in the
prompt file are correctly populated from the test config. Complex nested
objects (the `_caseDef` variable) pass through to the assertion handler
intact as parsed JavaScript objects.

### 3. Multi-Provider Comparison
The config cleanly defines two providers with different models and
configurations. Each test case runs against all providers, producing a
side-by-side comparison table. This is the primary use case Promptfoo
was designed for.

### 4. Output Formats
Results are available as:
- CLI table (immediate feedback)
- JSON file (`-o output.json`)
- Web UI (`promptfoo view`)
- Shareable links (cloud)

### 5. Error Handling
Provider errors (missing API key) are reported per-provider without
crashing the runner. The framework distinguishes errors from failures.

## Analysis: What Requires Adaptation

### 1. Case Definition Embedding (Medium Friction)
Our custom harness reads `cases.json` and `manifest.json` to get case
definitions. Promptfoo expects everything in the config YAML. The workaround
is embedding `_caseDef` as a test variable, which works but is verbose and
duplicates data. A production setup would need a script to generate
promptfoo configs from cases.json.

### 2. Deck File I/O (Medium Friction)
Our deterministic.js reads YAML decks from disk (via `deck_paths` in the
manifest). Promptfoo assertions receive the model output as a string. The
adapter bridges this by writing to a temp file and constructing a synthetic
trialDef. This works but adds complexity.

### 3. Multi-Deck Cases (High Friction)
F01 is a single-lesson/single-deck case. F05 (chapter mode) produces 2
decks from 2 lessons. Promptfoo's model produces a single output string
per test. Handling multi-deck output would require either:
- The model outputs multiple YAML documents in one response
- Multiple test cases per lesson
- A custom provider that splits the work

### 4. LLM Judge Integration (Not Tested)
Our harness runs a second-pass LLM judge (15 criteria, scored 0-10).
Promptfoo has built-in LLM grading via `llm-rubric`, but mapping our
custom criteria prompt would need investigation.

### 5. Aggregation and Reporting (Not Covered)
Our harness has `aggregate.js` that produces summary statistics across
all cases, trials, and models. Promptfoo has its own aggregation but
it's structured differently (per-provider, per-test).

## Architecture Decision

### Options Considered

| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| A: Replace harness with Promptfoo | Single tool, better UI, model comparison built-in | Multi-deck, aggregation, LLM judge need rework | High (2-3 weeks) |
| B: Complement (comparison + regression) | Best of both: Promptfoo for new model eval, harness for CI | Two systems to maintain | Low (1-2 days) |
| C: Keep custom harness only | No new dependencies, full control | No model comparison UI, no caching | Zero |

### Recommendation: Option B (Complement)

**Rationale**: Promptfoo excels at its core use case — comparing model outputs
side-by-side with custom grading. Our custom harness excels at its core use
case — regression testing with manifest-based trial tracking and multi-pass
grading. Using both gives us:

1. **Promptfoo for model selection**: When evaluating a new model (e.g.,
   Haiku 4.5 vs Sonnet 4 for flashcard generation), run the promptfoo config
   to get a comparison view. One-time use, interactive.

2. **Custom harness for CI/regression**: When validating that a skill update
   doesn't degrade quality, run the existing harness with the full test suite.
   Automated, manifest-tracked, aggregated.

3. **Shared grading logic**: The deterministic-adapter.js proves that our
   grading functions work in both contexts. The grader is the source of truth;
   the runners are just orchestration.

### What Would Make "Replace" Viable

If Promptfoo adds:
- Native support for multi-output assertions (one prompt, multiple graded outputs)
- Better test suite generation from external data files
- Built-in trial/run tracking with manifest files
- Custom aggregation hooks

...then full replacement becomes more attractive. Monitor Promptfoo releases.

---

## Next Steps

1. Set `ANTHROPIC_API_KEY` and run the full comparison
2. If comparison is valuable, add F02 and F04 test cases
3. Consider a `generate-promptfoo-config.js` script that reads cases.json
   and generates the YAML config automatically
4. Evaluate Promptfoo's `llm-rubric` against our custom LLM judge
