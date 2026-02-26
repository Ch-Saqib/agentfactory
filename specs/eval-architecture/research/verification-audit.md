# Verification Audit — Eval Architecture Research

**Date**: 2026-02-26
**Auditor**: Team Lead (post-research verification)
**Method**: Cross-referenced all researcher claims against codebase reality and live web sources

---

## CRITICAL ERROR: Promptfoo Has Native Simulated Users

### What the agent-eval-researcher claimed

> "**Simulated users**: **Not natively**. You can build a custom provider that calls another LLM to generate user turns, but it requires custom code. The framework is designed for pre-scripted test cases, not dynamic simulation."

This claim appears in the framework analysis (Section 2) and was a KEY factor in recommending LangWatch/Scenario as a separate simulation tool, leading to a 5-tool stack recommendation.

### What's actually true

Promptfoo has a **first-class Simulated User Provider** (`promptfoo:simulated-user`) documented at https://www.promptfoo.dev/docs/providers/simulated-user/

Features:
- **Native multi-turn conversation simulation** between AI agent and simulated user
- **Custom persona support** via `instructions` parameter with Nunjucks templating
- **`maxTurns`** configuration (default: 10)
- **`initialMessages`** for starting conversations mid-flow
- **Detailed persona specification** — documentation shows a full persona example ("mia_li_3668" with travel preferences, constraints, behavioral instructions)
- Works with both simple text-based agents and function-calling agents

### Impact on Recommendations

This error cascades through the entire architecture:

| Claim | Before (with error) | After (corrected) |
|---|---|---|
| Promptfoo simulation | "Not natively" | First-class support |
| Need for LangWatch/Scenario | "Required for simulation" | Optional — Promptfoo covers it |
| Minimal stack size | 5 tools | Potentially 2-3 tools |
| Python/Node.js split | "Accept Python for inspect_ai" | Avoidable — Promptfoo is Node.js native |
| Agent researcher's primary recommendation | inspect_ai + LangWatch/Scenario + Langfuse | Promptfoo alone may suffice |

### What this means for Q1 (three systems or one?)

The QA enforcer's recommendation to use **Promptfoo as the single primary framework** is significantly strengthened. Promptfoo covers:
- Skills eval (prompt testing — its core strength)
- Model comparison (matrix view — best-in-class)
- Multi-turn agent eval (via `_conversation` variable + `sessionId`)
- Simulated users (via `promptfoo:simulated-user` provider with personas)
- CI/CD integration (GitHub Actions, YAML configs)
- Node.js native (no runtime split)

The only remaining gap: **no cost tracking** (addressed by optional Langfuse) and **no sandboxed execution** (addressed by inspect_ai IF agents execute code).

---

## Codebase Verification Results

### Deterministic Checks Count

**Researcher claim**: "24 deterministic checks" / "24+ checks"
**Actual**: **25 unique check IDs** in `evals/flashcards/graders/deterministic.js`

Enumerated checks:
1. `generation_expectation_match` (hard, weight 8)
2. `deck_count_matches_target` (hard, weight 5)
3. `yaml_parse_success` (hard, weight 10)
4. `deck_schema_valid` (hard, weight 8)
5. `card_required_fields_present` (hard, weight 8)
6. `card_id_pattern_full_prefix` (hard, weight 8)
7. `card_id_unique_within_deck` (hard, weight 6)
8. `card_id_unique_across_trial` (hard, weight 6)
9. `tags_present_each_card` (hard, weight 4)
10. `difficulty_values_valid` (hard, weight 4)
11. `back_not_yes_no` (hard, weight 6)
12. `fronts_end_with_question_mark` (soft, weight 3)
13. `recall_thinking_balance` (soft, weight 8)
14. `recall_front_under_40_words` (hard, weight 6)
15. `thinking_cards_have_why` (hard, weight 6)
16. `recall_cards_without_why` (hard, weight 6)
17. `thinking_fronts_why_or_how` (soft, weight 5)
18. `no_duplicate_front_back_pairs` (soft, weight 4)
19. `formula_focus_coverage` (conditional hard/soft, weight 6/2)
20. `relationship_focus_coverage` (conditional soft, weight 4/2)
21. `recall_back_max_15_words` (hard, weight 6) — v2
22. `thinking_back_20_40_words` (soft, weight 5) — v2
23. `no_compound_questions` (soft, weight 4) — v2
24. `source_argue_template_max_2` (soft, weight 3) — v2
25. `difficulty_distribution` (soft, weight 5) — v2

**Verdict**: Minor error (25 not 24). Not consequential.

### LLM Judge Criteria Count

**Researcher claim**: "15 criteria"
**Actual**: **15 criteria** (from `CRITERIA_KEYS` array in `llm-judge.js:56-72`)

**Verdict**: Correct. ✓

### pass@k / pass^k Implementation

**Researcher claim**: "pass@k, pass^k aggregation"
**Actual**: `aggregate.js:215-218` implements:
- `pass_at_1`: First trial passes hard gates
- `pass_at_k`: At least one trial passes
- `pass_pow_k`: ALL trials pass (and at least one trial exists)

**Verdict**: Correct. ✓ Implementation matches Anthropic's definitions exactly.

### Baseline Comparison

**Researcher claim**: "baseline comparison with baselines/baseline-v1.json"
**Actual**: `aggregate.js:277-291` loads baseline JSON and computes deltas for det_mean, llm_judge_mean, pass@1, pass@k, pass^k. Two baselines exist: `baseline-v1.json` and `baseline-v2.json`.

**Verdict**: Correct. ✓

### buildPrompt() as Inline Rubric

**Researcher claim**: "llm-judge.js:buildPrompt() contains a grading rubric inline"
**Actual**: `llm-judge.js:100-163` — `buildPrompt()` constructs a 60-line rubric prompt including case metadata, source lessons, generated decks, and scoring instructions. The rubric IS inline, not loaded from a file.

**Verdict**: Correct. ✓ This IS the rubric that could be extracted into a Grader Skill.

### rubric-grader.md as Standalone Rubric

**Researcher claim**: "rubric-grader.md IS a grader skill body lacking frontmatter"
**Actual**: `evals/assessment-architect/rubric-grader.md` — 141 lines. Contains a full rubric with 4 dimensions (Domain Relevance 40%, Practical Competence 30%, Question Quality 20%, Coverage 10%), scoring criteria, and JSON output schema. Uses `{TEMPLATE_VARIABLES}` for substitution.

**Verdict**: Correct. ✓ This IS a rubric that could be packaged as SKILL.md with minimal changes.

### Dataset Cases

**Researcher claim**: "5 test cases"
**Actual**: `datasets/cases.json` has exactly 5 cases:
- F01: Explicit dual prompt single lesson
- F02: Implicit flashcard request
- F03: Negative control (no flashcards)
- F04: Formula-heavy lesson
- F05: Chapter mode multi-lesson (2 decks)

**Verdict**: Correct. ✓ Good coverage: explicit, implicit, negative, formula-focused, and multi-output.

---

## External Source Verification

### "Lost in Simulation" Paper

**Researcher claim**: "January 2026 paper showing up to 9pp variance"
**Verified**: arxiv.org/abs/2601.17087 — "Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations" by Preethi Seshadri et al. Published January 2026.
- 9pp variance: ✓
- Systematic miscalibration: ✓
- AAVE disparities: ✓
**Verdict**: Correct. ✓

### LangWatch/Scenario

**Researcher claim**: "MIT-licensed, native UserSimulatorAgent, multi-language"
**Verified**: https://github.com/langwatch/scenario — MIT license ✓. v0.7.14 (Jan 15, 2026) ✓. Python, TypeScript, Go ✓. UserSimulatorAgent + JudgeAgent ✓.
**Verdict**: Correct, but the framework is LESS mature than claimed — v0.7.x is pre-1.0.

### inspect_ai

**Researcher claim**: "UK AISI, MIT-licensed, Python, solver/scorer architecture"
**Verified**: https://github.com/UKGovernmentBEIS/inspect_ai — MIT license ✓. Python 3.10+ ✓. v0.3.130 (Sep 2025) ✓. Adopted by Anthropic, DeepMind ✓.
**Verdict**: Correct. ✓ Note: also pre-1.0 (v0.3.x).

### Promptfoo

**Researcher claim (Skills)**: "Node.js native, YAML-driven, MIT licensed, CI/CD integration"
**Verified**: https://github.com/promptfoo/promptfoo — MIT license ✓. Node.js/TypeScript ✓. YAML configs ✓. GitHub Actions ✓.
**Additional**: Has 6.4k+ GitHub stars, very active development, backed by a commercial entity (promptfoo.dev).
**Verdict**: Correct. ✓

---

## Research Quality Assessment

### Skills Eval Researcher
- **Accuracy**: High. Minor error on check count (25 not 24). All other claims verified.
- **Bias**: Slight sunk-cost bias toward keeping custom harness. However, the harness IS genuinely well-built.
- **Gap**: Did not investigate Promptfoo's simulated user capability (would have been out of scope, but the capability was unknown to the team).

### Agent Eval Researcher
- **Accuracy**: Mixed. **Critical error** on Promptfoo simulated user capability. All other claims verified (inspect_ai, LangWatch/Scenario, "Lost in Simulation" paper).
- **Bias**: Strong bias toward inspect_ai (Python ecosystem). Did not adequately weight the operational cost of introducing Python into a Node.js project.
- **Gap**: Failed to discover Promptfoo's simulated user provider, which invalidates the primary justification for a 3-tool stack.

### AI Employee Eval Researcher
- **Accuracy**: High. The "70/20/10" assessment is well-argued and supported. Framework coverage claims verified.
- **Bias**: None detected. Most balanced of the three researchers.
- **Gap**: Did not do hands-on testing of any framework. Assessment is documentation-based.

### Integration Architect
- **Accuracy**: Inherited the agent researcher's error about Promptfoo lacking simulated users. Otherwise thorough.
- **Impact**: The 5-tool stack recommendation was built on a false premise. With corrected information, a 2-3 tool stack is viable.

### QA Scope Enforcer
- **Accuracy**: Highest quality deliverable. Correctly identified the framework sprawl risk and pushed for consolidation.
- **Missed**: Did not independently verify the Promptfoo simulated user claim — but this was a factual error from a researcher, not an architectural concern.
- **Strength**: The "honest questions" section (who runs evals? where are the first 5 test cases?) is the most valuable contribution.

---

## Revised Recommendations Based on Verification

### Revised Minimal Stack: 2 tools (+ optional 3rd)

| Tool | Role | Domains |
|---|---|---|
| **Custom harness** (keep) | Skills eval runner | Skills |
| **Promptfoo** (adopt) | Model comparison + multi-turn agent eval + simulated users | All three |
| **Langfuse** (adopt later) | Cost tracking + production monitoring | Agent, AI Employee (when needed) |

**Dropped**: inspect_ai (Python, not needed if Promptfoo covers agent eval), LangWatch/Scenario (Promptfoo has native simulation), Braintrust (commercial, deferred).

### What Still Needs Validation

1. **Promptfoo's simulated user quality**: Can it produce realistic student personas with scripted+simulated hybrid behavior? The documentation shows it can, but hands-on testing is needed.
2. **Promptfoo's multi-turn grading**: Can Promptfoo's assertion system handle session-level grading (not just turn-level)? It supports custom JavaScript assertions, so likely yes.
3. **Promptfoo at scale**: How does single-threaded multi-turn execution perform with 100+ eval cases?

### The Minimum Viable Next Step

Write a **single Promptfoo YAML config** that:
1. Loads the `generate-flashcards/SKILL.md` as a prompt
2. Feeds one test case from `datasets/cases.json`
3. Runs against 2 models (Haiku, Sonnet)
4. Uses the existing `deterministic.js` logic as a custom assertion
5. Compares results in Promptfoo's matrix view

This proves/disproves whether Promptfoo can replace the custom harness for skills eval. If it can, the custom harness becomes optional. If it can't (likely for pass^k and 25-check deterministic scoring), keep both.

---

## Summary of Errors Found

| # | Error | Severity | Source | Impact |
|---|---|---|---|---|
| 1 | Promptfoo claimed to lack native simulated users | **CRITICAL** | Agent Eval Researcher | Invalidates 3-tool recommendation, inflated stack to 5 tools |
| 2 | Deterministic check count "24" should be 25 | Minor | Skills Eval Researcher | No architectural impact |
| 3 | LangWatch/Scenario maturity understated (pre-1.0 v0.7.x) | Minor | Agent Eval Researcher | Strengthens concern about adopting it |
| 4 | inspect_ai also pre-1.0 (v0.3.x) — not mentioned | Minor | Agent Eval Researcher | Both alternatives are immature |
| 5 | No researcher verified Promptfoo's simulated user docs | Moderate | All researchers | Nobody cross-checked the claim that drove the architecture |
