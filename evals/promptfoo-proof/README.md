# Promptfoo Proof-of-Concept: Flashcard Skill Evaluation

## What This Tests

Can Promptfoo serve as a universal eval runner for our flashcard skill,
replacing or complementing the custom `run-eval.sh` harness?

Specifically:
1. Load a flashcard generation prompt (derived from the skill)
2. Feed test case F01 (Agent Memory Basics) as variables
3. Run against multiple Anthropic models (Haiku 4.5, Sonnet 4)
4. Grade outputs using our existing 25 deterministic checks
5. Produce a comparison view across models

## Files

| File | Purpose |
|------|---------|
| `promptfooconfig.yaml` | Production config — Haiku 4.5 + Sonnet 4 via Anthropic API |
| `promptfooconfig.mock.yaml` | Testing config — uses golden fixture as mock provider |
| `prompt.txt` | The flashcard generation prompt (extracted from SKILL.md) |
| `deterministic-adapter.js` | Bridges our deterministic.js grader to Promptfoo assertions |
| `mock-provider.js` | Returns golden F01 output for pipeline testing without API key |
| `test-adapter.js` | Standalone unit test for the adapter (4 test cases) |

## How to Run

### Pipeline test (no API key needed)

```bash
cd evals/promptfoo-proof
npx promptfoo eval --config promptfooconfig.mock.yaml --no-cache
```

### Full model comparison (requires ANTHROPIC_API_KEY)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd evals/promptfoo-proof
npx promptfoo eval --no-cache
```

### View results in browser

```bash
npx promptfoo view
```

### Run adapter unit tests

```bash
cd evals/promptfoo-proof
node test-adapter.js
```

## Expected Output

### Mock run (golden fixture)
```
Results: 1 passed, 0 failed, 0 errors (100%)
```
The golden fixture scores 100/100 on all 25 deterministic checks.

### Live run (Haiku + Sonnet)
Each model generates a YAML flashcard deck. The deterministic adapter grades
each output against the F01 case expectations:
- 8-16 cards total
- 45-55% recall / thinking balance
- Recall backs under 15 words
- Thinking cards have Why/How fronts
- Valid YAML schema, card IDs, difficulty distribution
- ...and 20 more checks

Results show pass/fail with a 0-1 score and detailed breakdown of which
checks passed or failed.

## What Success Means

**Pipeline works**: Promptfoo can orchestrate prompt + providers + custom
assertions, and our deterministic grading logic runs correctly inside the
Promptfoo assertion format.

**Model comparison works**: Side-by-side results show which model produces
better flashcard decks, with granular check-level detail.

## What Failure Means

If the pipeline itself fails (config parsing, assertion loading, etc.),
Promptfoo is not viable as a runner. If models fail the checks, that's
expected variation — the interesting signal is the comparison.

## Architecture Decision

See `specs/eval-architecture/research/promptfoo-proof-results.md` for the
full analysis and recommendation.

## Blockers and Workarounds

### ANTHROPIC_API_KEY not set
The production config requires the API key. The mock config proves the full
pipeline works without it. Set the env var to run the real comparison.

### yaml npm module not available globally
The deterministic.js grader requires a YAML parser. We install it locally
in this directory (`npm install yaml`). The adapter patches the grader's
`loadYamlModule()` to use this local copy.

### deterministic.js is a CLI script, not a module
The grader defines `evaluateCase()` locally and calls `main()` on load.
The adapter loads the source, strips the shebang and main() call, patches
the YAML loader, and evaluates it in a VM sandbox to extract the function.

### Promptfoo assertion contract
Promptfoo custom JS assertions receive `(output, context)` and must return
`{pass, score, reason}`. Our grader expects `(caseDef, trialDef, repoRoot)`
with deck files on disk. The adapter bridges this by writing model output
to a temp file and constructing the expected objects.

### _caseDef passed through vars
The full case definition (expected card counts, ratio ranges, etc.) is
embedded as a `_caseDef` variable in the test config. This is verbose but
keeps everything self-contained — no external file reads at assertion time.
