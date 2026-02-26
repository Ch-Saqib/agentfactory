# Anthropic "Demystifying Evals for AI Agents" -- Deep-Dive Technical Reference

**Source**: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (Published 2026-01-09)
**Extracted**: 2026-02-26
**Purpose**: Exhaustive reference for building eval infrastructure. Every concrete pattern, technique, recommendation, and architectural decision from the article, plus gap analysis against our existing flashcards eval harness.

---

## Table of Contents

1. [Complete Taxonomy](#1-complete-taxonomy)
2. [Grading Patterns](#2-grading-patterns)
3. [Aggregation Methods](#3-aggregation-methods)
4. [Architecture Recommendations](#4-architecture-recommendations)
5. [Anti-Patterns](#5-anti-patterns)
6. [Agent-Specific Guidance](#6-agent-specific-guidance)
7. [Concrete Examples](#7-concrete-examples)
8. [Operational Advice](#8-operational-advice)
9. [Comparison to Our System](#9-comparison-to-our-system)

---

## 1. Complete Taxonomy

### Core Terms

| Term | Definition (from article) | Relationships |
|------|--------------------------|---------------|
| **Evaluation (eval)** | "A test for an AI system: give an AI an input, then apply grading logic to its output to measure success" | Contains tasks; run by a harness |
| **Automated eval** | Tests "that can be run during development without real users" | Subset of all evals; excludes human-only methods |
| **Task** (aka problem, test case) | "A single test with defined inputs and success criteria" | Lives in an eval suite; has multiple trials; scored by graders |
| **Trial** | "Each attempt at a task. Because model outputs vary between runs, we run multiple trials to produce more consistent results" | One task has many trials; each trial produces a transcript and outcome |
| **Grader** | "Logic that scores some aspect of the agent's performance. A task can have multiple graders, each containing multiple assertions" | Applied to trials; produces scores; three types (code, model, human) |
| **Transcript** (aka trace, trajectory) | "The complete record of a trial, including outputs, tool calls, reasoning, intermediate results" | Produced by a trial; input to graders; should be read by humans regularly |
| **Outcome** | "The final state in the environment at the end of the trial" | Part of what graders evaluate; distinct from the path taken |
| **Evaluation harness** | Infrastructure that "runs evals end-to-end. It provides instructions and tools, runs tasks concurrently, records all the steps, grades outputs, and aggregates results" | Orchestrates everything; must provide environment isolation |
| **Agent harness** (aka scaffold) | "The system that enables a model to act as an agent: it processes inputs, orchestrates tool calls, and returns results" | Distinct from the eval harness; should match production as closely as possible |
| **Evaluation suite** | "A collection of tasks designed to measure specific capabilities or behaviors" | Groups related tasks; can saturate over time |

### Eval Type Terms

| Term | Definition | Key Property |
|------|-----------|--------------|
| **Capability eval** (aka "quality" eval) | "Asks 'What can this agent do well?' Should start at a low pass rate, targeting tasks the agent struggles with" | Gives teams "a hill to climb"; saturates when too easy |
| **Regression eval** | "Asks 'Does the agent still handle all the tasks it used to?' Should have a nearly 100% pass rate" | Guards against breakage; complementary to capability evals |
| **Saturation** | "Occurs when an agent passes all of the solvable tasks, leaving no room for improvement" | An eval at 100% tracks regressions only; needs replacement with harder tasks |

### Scoring Terms

| Term | Definition |
|------|-----------|
| **Hard gate** | A binary pass/fail check where failure marks the entire trial as failed |
| **Weighted scoring** | "Combined grader scores must hit a threshold" |
| **Binary scoring** | "All graders must pass" |
| **Hybrid scoring** | Combination of weighted and binary approaches |
| **Partial credit** | "For tasks with multiple components, build in partial credit" -- an agent that gets 3 of 4 steps right scores higher than one that fails immediately |

---

## 2. Grading Patterns

### 2.1 Code-Based / Deterministic Graders

**When to use**: Whenever you can express success as a computable predicate. Anthropic says to "choose deterministic graders where possible."

**Specific methods identified**:

| Method | Description | Example |
|--------|-------------|---------|
| **String match** | Exact, regex, or fuzzy matching on output text | Check for specific answer |
| **Binary tests** | Fail-to-pass and pass-to-pass test suites | Run unit tests, verify pass count changes |
| **Static analysis** | Lint, type check, security scanning | ruff, mypy, bandit on generated code |
| **Outcome verification** | Check the resulting state of the environment | File system state, DB contents, API responses |
| **Tool calls verification** | Check which tools were called and with what parameters | `required: [{tool: read_file, params: {path: "src/auth/*"}}]` |
| **Transcript analysis** | Measure properties of the agent's trace | Turns taken, token usage, tool call count |

**Strengths**: Fast, cheap, objective, reproducible, easy to debug, verify specific conditions.

**Weaknesses**: "Brittle to valid variations that don't match expected patterns exactly; lacking in nuance; limited for evaluating some more subjective tasks."

**Critical pitfall -- rigid thresholds**: Anthropic warns about "rigid grading that penalized '96.12' when expecting '96.124991...'." The CORE-Bench example showed Opus 4.5 initially scoring 42% due to brittle grading, jumping to 95% after fixing grader bugs.

### 2.2 Model-Based / LLM-as-Judge Graders

**When to use**: "Where necessary or for additional flexibility." Use when deterministic graders cannot capture the quality dimension.

**Specific methods identified**:

| Method | Description | When to Use |
|--------|-------------|-------------|
| **Rubric-based scoring** | Structured rubric with explicit criteria, scored per dimension | Primary method; most recommended |
| **Natural language assertions** | Free-form assertions the LLM evaluates as true/false | Quick checks for specific properties |
| **Pairwise comparison** | Compare two outputs and pick the better one | A/B testing between agent versions |
| **Reference-based evaluation** | Grade against a known-good reference output | When golden outputs exist |
| **Multi-judge consensus** | Multiple LLM judges, aggregate their scores | High-stakes decisions; reduces single-judge variance |

**Strengths**: Flexible, scalable, captures nuance, handles open-ended tasks, handles freeform output.

**Weaknesses**: "Non-deterministic; more expensive than code; requires calibration with human graders for accuracy."

**Best practices for LLM graders**:

1. **Isolate dimensions**: "Create clear, structured rubrics to grade each dimension of a task, and then grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions."
2. **Provide escape hatches**: "To avoid hallucinations, give the LLM a way out, like providing an instruction to return 'Unknown' when it doesn't have enough information."
3. **Calibrate against humans**: "LLM-as-judge graders should be closely calibrated with human experts to gain confidence that there is little divergence between the human grading and model grading."
4. **Iterate**: "Model grading often takes careful iteration to validate accuracy."

### 2.3 Human Graders

**When to use**: "Judiciously for additional validation." Not as primary grading method for automated evals.

**Specific methods identified**:

| Method | Description |
|--------|-------------|
| **SME review** | Subject matter experts grade outputs |
| **Crowdsourced judgment** | Multiple non-expert raters |
| **Spot-check sampling** | Randomly sample and review subset |
| **A/B testing** | Structured comparison by humans |
| **Inter-annotator agreement** | Multiple raters, measure agreement |

**Strengths**: "Gold standard quality; matches expert user judgment; used to calibrate model-based graders."

**Weaknesses**: "Expensive; slow; often requires access to human experts at scale."

**Key role**: Human grading is the calibration standard for LLM graders, not a replacement for automation. Anthropic explicitly positions human grading as periodic validation, not routine execution.

### 2.4 Grader Design Principles (Across All Types)

1. **Grade outcomes, not paths**: "There is a common instinct to check that agents followed very specific steps like a sequence of tool calls in the right order. We've found this approach too rigid and results in overly brittle tests, as agents regularly find valid approaches that eval designers didn't anticipate." **Recommendation**: "It's often better to grade what the agent produced, not the path it took."

2. **Build partial credit**: "A support agent that correctly identifies the problem and verifies the customer but fails to process a refund is meaningfully better than one that fails immediately."

3. **Make graders bypass-resistant**: "The agent shouldn't be able to easily 'cheat' the eval. Tasks and graders should be designed so that passing genuinely requires solving the problem."

4. **Read transcripts regularly**: "At Anthropic, we invested in tooling for viewing eval transcripts and we regularly take the time to read them."

5. **Verify fairness**: "Failures should seem fair: it's clear what the agent got wrong and why."

---

## 3. Aggregation Methods

### 3.1 pass@k

**Definition**: "Measures the likelihood that an agent gets at least one correct solution in k attempts."

**Behavior**: As k increases, pass@k score rises (more chances = more likely to get at least one success).

**Formula** (implicit): pass@k = 1 - (1 - p)^k where p is per-trial success rate.

**Interpretation**: "A score of 50% pass@1 means that a model succeeds at half the tasks in the eval on its first try."

**Use case**: "When one success matters" -- e.g., exploring solution spaces, creative tasks, one-shot queries.

### 3.2 pass^k

**Definition**: "Measures the probability that all k trials succeed."

**Behavior**: As k increases, pass^k falls (demanding consistency across more trials is harder).

**Formula**: pass^k = p^k where p is per-trial success rate.

**Worked example from article**: "If your agent has a 75% per-trial success rate and you run 3 trials, the probability of passing all three is (0.75)^3 = 42%."

**Use case**: "For agents where consistency is essential" -- e.g., production reliability, customer-facing agents, safety-critical systems.

### 3.3 Relationship Between pass@k and pass^k

**At k=1**: "They're identical (both equal the per-trial success rate)."

**At k=10**: "They tell opposite stories: pass@k approaches 100% while pass^k falls to 0%."

This is a crucial insight for interpretation: the same underlying agent performance tells very different stories depending on which metric you report.

### 3.4 Additional Metrics Mentioned

| Metric | Purpose | Notes |
|--------|---------|-------|
| **Per-trial success rate** | Base metric from which pass@k and pass^k derive | The fundamental unit |
| **Latency** | Operational performance tracking | Tracked on static task bank |
| **Token usage** | Cost proxy | Per-trial and per-task |
| **Cost per task** | Direct cost measurement | For budgeting and optimization |
| **Error rates** | Failure categorization | By type, by severity |
| **Consistency** | Cross-trial variance | Low variance = reliable agent |

---

## 4. Architecture Recommendations

### 4.1 Evaluation Harness Design

**Core responsibilities** of an eval harness:
1. Provide instructions and tools to the agent
2. Run tasks concurrently
3. Record all steps (produce transcripts)
4. Grade outputs
5. Aggregate results

**Environment isolation** (critical): "Each trial should be 'isolated' by starting from a clean environment. Unnecessary shared state between runs (leftover files, cached data, resource exhaustion) can cause correlated failures due to infrastructure flakiness."

**Warning on shared state inflating performance**: "In some internal evals we observed Claude gaining an unfair advantage on some tasks by examining the git history from previous trials."

**Independence requirement**: "If multiple distinct trials fail because of the same limitation in the environment (like limited CPU memory), these trials are not independent because they're affected by the same factor, and the eval results become unreliable."

### 4.2 Agent Harness vs. Eval Harness Separation

Anthropic explicitly distinguishes between:
- **Agent harness (scaffold)**: The production system that enables the model to act as an agent
- **Eval harness**: The testing infrastructure that runs the agent harness in controlled conditions

**Critical principle**: "It's essential that the agent in the eval functions roughly the same as the agent used in production, and that the environment itself doesn't introduce further noise." The agent harness used in evals should mirror production.

### 4.3 Task Design Principles

1. **Unambiguous specifications**: "A good task is one where two domain experts would independently reach the same pass/fail verdict."
2. **Reference solutions**: "For each task, it's useful to create a reference solution: a known working output that passes all graders. This proves that the task is solvable and verifies graders are correctly configured."
3. **Grader alignment**: "Everything the grader checks should be clear from the task description; agents shouldn't fail due to ambiguous specs."
4. **Balanced test sets**: "Test both the cases where a behavior should occur and where it shouldn't. One-sided evals create one-sided optimization."
5. **Zero-pass diagnostic**: "With frontier models, a 0% pass rate across many trials (i.e 0% pass@100) is most often a signal of a broken task, not an incapable agent."

### 4.4 Organizational Model

**Recommended structure**: "Establishing dedicated evals teams to own the core infrastructure, while domain experts and product teams contribute most eval tasks and run the evaluations themselves."

**Contribution model**: "The people closest to product requirements and users are best positioned to define success. With current model capabilities, product managers, customer success managers, or salespeople can use Claude Code to contribute an eval task as a PR."

### 4.5 Eval Frameworks Mentioned

| Framework | Focus | Notes |
|-----------|-------|-------|
| **Harbor** | Running agents in containerized environments | Infrastructure for trials at scale; standardized task/grader format; benchmark registry |
| **Promptfoo** | Lightweight prompt testing | YAML configuration; assertion types from string match to LLM-as-judge |
| **Braintrust** | Offline eval + production observability | Experiment tracking included |
| **LangSmith** | Tracing + evaluations + dataset management | Tight LangChain integration |
| **Langfuse** | Self-hosted open-source alternative | For data residency requirements |

**Anthropic's advice**: "While frameworks can be a valuable way to accelerate progress and standardize, they're only as good as the eval tasks you run through them. It's often best to quickly pick a framework that fits your workflow, then invest your energy in the evals themselves."

---

## 5. Anti-Patterns

### 5.1 Explicitly Warned Against

| Anti-Pattern | Quote / Evidence | Severity |
|-------------|------------------|----------|
| **Overly rigid step-checking** | "There is a common instinct to check that agents followed very specific steps like a sequence of tool calls in the right order. We've found this approach too rigid" | High -- causes false failures on valid solutions |
| **One-sided eval optimization** | "One-sided evals create one-sided optimization" -- only testing when behavior should trigger, not when it shouldn't | High -- creates agents that over-trigger |
| **Shared state pollution** | "Unnecessary shared state between runs (leftover files, cached data, resource exhaustion) can cause correlated failures" | High -- invalidates statistical independence |
| **Delayed eval creation** | "Evals get harder to build the longer you wait. Early on, product requirements naturally translate into test cases. Wait too long and you're reverse-engineering success criteria from a live system" | Medium -- compounds over time |
| **Trusting saturated evals** | "An eval at 100% tracks regressions but provides no signal for improvement" | Medium -- gives false confidence |
| **Ignoring transcripts** | "You won't know if your graders are working well unless you read the transcripts" | High -- grader bugs go undetected |
| **Taking scores at face value** | "We do not take eval scores at face value until someone digs into the details of the eval" | High -- misleading metrics |
| **Brittle numeric thresholds** | CORE-Bench penalized "96.12" when expecting "96.124991..." | High -- false failures |
| **Task/grading mismatch** | METR tasks asked agents to "optimize to a stated score threshold" but grading "required exceeding that threshold" | High -- penalizes correct behavior |
| **Ambiguous task specs** | "If a task asks the agent to write a script but doesn't specify a filepath, and the tests assume a particular filepath, the agent might fail through no fault of its own" | High -- noise in metrics |
| **Class-imbalanced eval sets** | "Try to avoid class-imbalanced evals" | Medium -- biased optimization |

### 5.2 Subtle Anti-Patterns (Inferred)

| Anti-Pattern | Evidence |
|-------------|----------|
| **Eval without golden outputs** | Article emphasizes reference solutions for every task |
| **Single-judge LLM grading** | Article recommends isolated dimension grading and multi-judge consensus |
| **No human calibration** | "LLM-as-judge graders should be closely calibrated with human experts" |
| **Monolithic rubric** | "Grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions" |

---

## 6. Agent-Specific Guidance

### 6.1 What Makes Agent Evals Different from Prompt Evals

| Dimension | Prompt Eval | Agent Eval |
|-----------|-------------|------------|
| **Turns** | Single-turn: prompt -> response -> grade | Multi-turn: many steps, tool calls, state changes |
| **State** | Stateless | Agents "modify state in the environment and adapt as they go" |
| **Paths** | Usually one path to answer | "Agents regularly find valid approaches that eval designers didn't anticipate" |
| **Grading surface** | Output text | Outcome state, transcript, tool calls, intermediate results |
| **Environment** | None needed | Must provision and isolate environments per trial |
| **Determinism** | Low variance | High variance -- same task can take very different paths |
| **Cost** | Low per eval | Higher -- multiple tool calls, API calls, environment setup |

### 6.2 Multi-Turn Considerations

- Transcripts capture the full interaction history including all tool calls and intermediate reasoning
- Turn count is itself a metric worth tracking (efficiency)
- Token usage across turns measures cost
- State changes between turns must be recorded for debugging

### 6.3 Tool-Use Evaluation

Two approaches identified:

1. **Required tools check**: Verify that specific tools were called (e.g., `verify_identity` before `process_refund`)
2. **Tool parameter validation**: Verify parameters were correct (e.g., `refund amount <= 100`)

**Warning**: Don't over-specify tool ordering. Check that required tools were used, not that they were used in a specific sequence.

### 6.4 Trajectory Analysis

- Track `n_turns`, `n_toolcalls`, `n_total_tokens` as transcript metrics
- Use transcript analysis to understand failure modes, not just grade pass/fail
- "When a task fails, the transcript tells you whether the agent made a genuine mistake or whether your graders rejected a valid solution"

### 6.5 Agent-Type Patterns

| Agent Type | Primary Grading Strategy | Secondary Strategy | Key Challenge |
|-----------|-------------------------|-------------------|---------------|
| **Coding** | Unit tests (pass/fail) | LLM rubric for code quality; static analysis | Well-specified tasks with binary correctness |
| **Conversational** | State checks + LLM rubric | Transcript constraints (max turns) | "Quality of interaction itself is part of what you're evaluating"; requires simulated user |
| **Research** | Groundedness + coverage + source quality | LLM rubric calibrated against expert judgment | "Experts may disagree"; ground truth shifts; open-ended outputs |
| **Computer Use** | Environment state verification | URL/page state checks | Requires real or sandboxed environment; DOM vs screenshot tradeoff |

### 6.6 Simulated Users

For conversational agent evals: "Unlike most other evals, they often require a second LLM to simulate the user." This introduces a second source of non-determinism and must be accounted for in variance analysis.

---

## 7. Concrete Examples

### 7.1 Coding Agent Eval Task (YAML)

From the article -- illustrative example showing full grader range:

```yaml
task:
  id: "fix-auth-bypass_1"
  desc: "Fix authentication bypass when password field is empty..."
  graders:
    - type: deterministic_tests
      required: [test_empty_pw_rejected.py, test_null_pw_rejected.py]
    - type: llm_rubric
      rubric: prompts/code_quality.md
    - type: static_analysis
      commands: [ruff, mypy, bandit]
    - type: state_check
      expect:
        security_logs: {event_type: "auth_blocked"}
    - type: tool_calls
      required:
        - {tool: read_file, params: {path: "src/auth/*"}}
        - {tool: edit_file}
        - {tool: run_tests}
  tracked_metrics:
    - type: transcript
      metrics:
        - n_turns
        - n_toolcalls
        - n_total_tokens
```

**Article's caveat**: "This example showcases the full range of available graders for illustration. In practice, coding evaluations typically rely on unit tests for correctness verification and an LLM rubric for assessing overall code quality."

### 7.2 Conversational Agent Eval Task (YAML)

```yaml
graders:
  - type: llm_rubric
    rubric: prompts/support_quality.md
    assertions:
      - "Agent showed empathy for customer's frustration"
      - "Resolution was clearly explained"
      - "Agent's response grounded in fetch_policy tool results"
  - type: state_check
    expect:
      tickets: {status: resolved}
      refunds: {status: processed}
  - type: tool_calls
    required:
      - {tool: verify_identity}
      - {tool: process_refund, params: {amount: "<=100"}}
      - {tool: send_confirmation}
  - type: transcript
    max_turns: 10
```

### 7.3 pass^k Worked Example

Per-trial success rate: 75%
Trials (k): 3
pass^k = (0.75)^3 = 42.2%

Interpretation: Even a 75% reliable agent only achieves ~42% consistency across 3 runs. This is why pass^k matters for production reliability assessment.

---

## 8. Operational Advice

### 8.1 Getting Started (Zero-to-One Roadmap)

Anthropic prescribes 8 explicit steps:

| Step | Action | Key Insight |
|------|--------|-------------|
| **0** | Start early | "20-50 simple tasks drawn from real failures is a great start" |
| **1** | Convert manual tests | "Begin with the manual checks you run during development"; mine bug tracker and support queue |
| **2** | Write unambiguous tasks with reference solutions | "Two domain experts would independently reach the same pass/fail verdict"; create golden outputs |
| **3** | Build balanced problem sets | Test both positive and negative cases; avoid class imbalance |
| **4** | Build robust harness with stable environment | Environment isolation; match production agent harness |
| **5** | Design graders thoughtfully | Deterministic where possible, LLM where necessary, human for calibration |
| **6** | Check the transcripts | "We invested in tooling for viewing eval transcripts and we regularly take the time to read them" |
| **7** | Monitor for saturation | Replace saturated evals with harder tasks; "large capability improvements appear as small increases in scores" |
| **8** | Maintain through ownership | Dedicated evals team for infra; domain experts contribute tasks; "as routine as maintaining unit tests" |

### 8.2 CI/CD Integration

- "Evals can be run on every commit"
- Baselines provide automatic regression detection
- Track latency, token usage, cost per task, error rates on a static bank of tasks

### 8.3 Cost Management

- Deterministic graders are free (compute only)
- LLM graders cost per invocation -- use the cheapest model that maintains calibration
- Trade off trial count (k) against cost: more trials = better statistics but higher cost
- Use LLM grading "where necessary" -- not on every dimension if deterministic checks suffice

### 8.4 Model Upgrade Testing

"When more powerful models come out, teams without evals face weeks of testing while competitors with evals can quickly determine the model's strengths, tune their prompts, and upgrade in days."

### 8.5 Eval-Driven Development

"Build evals to define planned capabilities before agents can fulfill them, then iterate until the agent performs well. Internally, we often build features that work 'well enough' today but are bets on what models can do in a few months. Capability evals that start at a low pass rate make this visible."

### 8.6 Complementary Methods (Beyond Automated Evals)

| Method | Strength | Weakness |
|--------|----------|----------|
| **Production monitoring** | Real user behavior at scale; ground truth | Reactive -- problems reach users first |
| **A/B testing** | Measures actual user outcomes; controls confounds | Slow (days/weeks); needs traffic |
| **User feedback** | Surfaces unanticipated problems | Sparse, self-selected, skews to severe issues |
| **Manual transcript review** | Builds intuition for failure modes | Time-intensive, inconsistent coverage |
| **Systematic human studies** | Gold-standard quality judgments | Expensive, slow, needs expert raters |

**Anthropic's integration pattern**: "The most effective teams combine these methods: automated evals for fast iteration, production monitoring for ground truth, and periodic human review for calibration."

---

## 9. Comparison to Our System

Our flashcards eval harness lives at `evals/flashcards/` and consists of:
- `graders/deterministic.js` -- 25 deterministic checks
- `graders/llm-judge.js` -- 15 LLM criteria with `buildPrompt()` rubric
- `graders/aggregate.js` -- pass@k, pass^k, baseline diff, consistency scoring
- `run-eval.sh` -- shell orchestrator
- `datasets/cases.json` -- 5 test cases

### 9.1 Alignment with Anthropic's Guidance

| Anthropic Recommendation | Our Implementation | Status |
|-------------------------|-------------------|--------|
| **Deterministic graders where possible** | 25 deterministic checks in `deterministic.js` covering schema, ID patterns, word counts, difficulty distribution, duplicate detection | ALIGNED -- strong deterministic layer |
| **LLM graders where necessary** | 15-criterion rubric-based LLM judge in `llm-judge.js` | ALIGNED -- structured rubric with per-criterion scoring |
| **Multiple graders per task** | Deterministic + LLM judge run sequentially per trial | ALIGNED -- two grader types |
| **pass@k aggregation** | Implemented in `aggregate.js` (line 217: `passAtK = hardPassFlags.some(Boolean)`) | ALIGNED |
| **pass^k aggregation** | Implemented in `aggregate.js` (line 218: `passPowK = hardPassFlags.every(Boolean)`) | ALIGNED |
| **Baseline comparison** | `--baseline` flag, delta computation in `aggregate.js` | ALIGNED |
| **Reference solutions / golden outputs** | `golden_outputs` field in `cases.json` for each case | ALIGNED |
| **Negative control cases** | F03 is a negative control ("Do not generate flashcards") | ALIGNED -- balanced positive/negative testing |
| **Hard vs soft gates** | `hard` boolean on each check; `hard_pass` requires all hard checks pass | ALIGNED |
| **Weighted scoring** | `weight` field on each check; `deterministic_score_100` is weighted average | ALIGNED |
| **Critical criteria threshold** | 6 critical LLM criteria must score >= 8; overall >= 82 | ALIGNED |
| **Shell orchestrator** | `run-eval.sh` handles all orchestration | ALIGNED |
| **Structured JSON output** | All graders output JSON with consistent schema | ALIGNED |
| **Run ID tracking** | `--run-id` flag, timestamped directories | ALIGNED |
| **Case filtering** | `--only-case` and `--case-filter` flags | ALIGNED |
| **Report generation** | JSON + Markdown summary per run | ALIGNED |

### 9.2 Divergences and Gaps

| Anthropic Recommendation | Our Current State | Gap Severity | Recommended Action |
|-------------------------|-------------------|-------------|-------------------|
| **Environment isolation per trial** | No environment isolation; all trials share the same filesystem and state | **HIGH** | Our flashcard eval is stateless by design (grading pre-generated YAML files), so this is low-risk for our current use case. But if we expand to agentic evals that modify state, we need containerized trial environments. |
| **Isolated dimension grading** | LLM judge grades all 15 criteria in a single prompt call | **MEDIUM** | Anthropic recommends "grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions." Our single-prompt approach risks cross-criterion contamination. Consider splitting into per-criterion judge calls for critical criteria. |
| **Human calibration of LLM graders** | No human calibration process documented | **MEDIUM** | We have no systematic process for comparing LLM judge scores against human expert judgment. Should establish periodic spot-check reviews where a human grades a sample and we measure LLM-human agreement. |
| **Transcript viewing tooling** | No transcript viewer; raw JSON only | **LOW** | Anthropic "invested in tooling for viewing eval transcripts." Our eval grades pre-existing outputs rather than running an agent, so transcripts are less relevant. If we add agentic evals, we need transcript viewing. |
| **Escape hatch in LLM prompt** | `buildPrompt()` does not include "return Unknown if unsure" instruction | **LOW** | Add a line like "If you cannot determine a score for a criterion due to insufficient information, return score_10: -1 with rationale explaining why." This prevents hallucinated scores. |
| **Bypass resistance** | Not explicitly tested | **LOW** | Our graders check structural properties that are hard to "cheat" (YAML schema, ID patterns, word counts). The LLM judge checks semantic quality. Moderate bypass resistance by design, but not explicitly validated. |
| **Task count (20-50 recommended)** | 5 test cases | **MEDIUM** | Anthropic recommends starting with "20-50 simple tasks drawn from real failures." We have 5 cases. Should expand the dataset with real failure cases from live runs. The `--grade-live` mode suggests this pipeline exists but the live dataset may be small. |
| **Eval-driven development** | Evals built after feature; not used to define planned capabilities | **LOW** | Our harness evaluates an existing skill. Anthropic recommends building capability evals first, then iterating. Consider adding aspirational test cases that define quality targets before the skill can achieve them. |
| **Class balance validation** | No explicit check that positive/negative cases are balanced | **LOW** | We have 4 positive + 1 negative case. Anthropic warns about class imbalance. Should add more negative/edge cases. |
| **Consistency score** | Custom formula: `100 - detStddevAvg * 2 - recallStddevAvg * 100` | **NONE** | Not directly addressed by Anthropic, but reasonable. Our custom consistency metric fills a gap not explicitly covered in the article. |
| **Multi-trial execution** | Manifest-based (pre-generated trials); no live trial execution in harness | **NONE** | This is a design choice, not a gap. Our harness grades pre-existing output rather than executing the agent. This is valid for our use case (evaluating a skill's output quality). |

### 9.3 Strengths of Our System Not Mentioned by Anthropic

| Our Feature | Notes |
|-------------|-------|
| **Recall vs. Thinking card type taxonomy** | Domain-specific card type classification with separate quality criteria for each type. More nuanced than generic grading. |
| **Difficulty distribution enforcement** | 20-40% basic / 40-60% intermediate / 10-30% advanced. An example of domain-specific structural grading. |
| **Anti-pattern detection** | Compound question detection, "source argue" template limiting, yes/no answer rejection. These are content-quality-specific anti-patterns our grader catches that go beyond generic eval guidance. |
| **Dual dataset mode** | Fixture-based evaluation (reproducible) + live evaluation (real outputs) via `--grade-live`. This separation lets us do both regression testing and production monitoring with the same harness. |
| **Incremental live trial recording** | `upsert-live-trial.js` lets us record real production outputs into the evaluation pipeline incrementally. |

### 9.4 Priority Action Items

Ranked by impact and effort:

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P1** | Expand dataset from 5 to 20+ cases, mining real failures from live eval runs | Medium | High -- more cases = better signal, less overfitting to 5 cases |
| **P2** | Add more negative/edge cases (ambiguous requests, empty lessons, very short lessons, very long lessons, non-English content) | Low | Medium -- prevents one-sided optimization |
| **P3** | Split LLM judge into isolated per-criterion calls for the 6 critical criteria | Medium | Medium -- reduces cross-criterion contamination; more expensive but more accurate |
| **P4** | Add escape hatch to LLM prompt ("Unknown" option) | Trivial | Low -- prevents hallucinated scores on edge cases |
| **P5** | Establish human calibration process: monthly spot-check of 5 random trials, compare human vs LLM scores | Low (process) | Medium -- validates LLM grader accuracy over time |
| **P6** | Add aspirational capability test cases that start at 0% pass rate, defining quality targets before the skill can hit them | Low | Medium -- enables eval-driven development |
| **P7** | Build simple transcript/result viewer (even a CLI pretty-printer) | Low | Low -- improves debugging efficiency |

---

## Appendix A: Key Quotes for Team Reference

> "Good evaluations help teams ship AI agents more confidently. Without them, it's easy to get stuck in reactive loops -- catching issues only in production, where fixing one failure creates others."

> "Their value compounds over the lifecycle of an agent."

> "We do not take eval scores at face value until someone digs into the details of the eval and reads some transcripts."

> "Defining eval tasks is one of the best ways to stress-test whether the product requirements are concrete enough to start building."

> "It's often better to grade what the agent produced, not the path it took."

> "With frontier models, a 0% pass rate across many trials (i.e 0% pass@100) is most often a signal of a broken task, not an incapable agent."

> "The most effective teams combine these methods: automated evals for fast iteration, production monitoring for ground truth, and periodic human review for calibration."

> "While frameworks can be a valuable way to accelerate progress and standardize, they're only as good as the eval tasks you run through them."

---

## Appendix B: Benchmark Reference

| Benchmark | Agent Type | What It Tests | Grading Method |
|-----------|-----------|---------------|----------------|
| **SWE-bench Verified** | Coding | GitHub issues from Python repos | Run test suite; fail-to-pass + pass-to-pass |
| **Terminal-Bench** | Coding | End-to-end technical tasks (build kernel, train ML model) | Task-specific outcome verification |
| **tau-Bench / tau2-Bench** | Conversational | Multi-turn interactions (retail, airline) | Simulated user + state checks |
| **BrowseComp** | Research | "Needles in haystacks across the open web" | Easy to verify, hard to solve |
| **WebArena** | Computer Use | Browser-based tasks | URL/page state + backend state verification |
| **OSWorld** | Computer Use | Full OS control tasks | File system, app config, DB, UI inspection |
| **CORE-Bench** | Coding/Research | Scientific code reproduction | Numeric output matching (with precision issues) |
