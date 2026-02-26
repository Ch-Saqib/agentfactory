# Skills Eval Landscape

## 1. What Is a "Skill Eval"?

A **Skill Eval** evaluates an Agent Skill (a `SKILL.md` file + optional `scripts/`, `references/`, `assets/` directories per the [agentskills.io specification](https://agentskills.io/specification)) **in isolation**. The skill's instructions serve as the prompt, test inputs exercise that prompt, and graders score the output against defined criteria.

This is distinct from Agent Evals (multi-turn, tool-using systems) or AI Employee Evals (full personalization + governance stacks). A Skill Eval answers three questions:

1. **Does this skill produce correct output?** (quality gate)
2. **Does a new version regress?** (regression detection via baseline comparison)
3. **Does it work better with Model A or Model B?** (model comparison)

### Mapping to Anthropic's Taxonomy

Anthropic's "Demystifying Evals for AI Agents" article defines seven abstractions. Here is how they map to Skills Eval:

| Anthropic Abstraction | Skills Eval Equivalent |
|---|---|
| **Task** | A test case: skill instructions + input data + expected constraints |
| **Trial** | One execution of the skill on one task (multiple trials account for non-determinism) |
| **Grader** | Logic scoring skill output — deterministic checks, LLM-as-judge, or hybrid |
| **Transcript** | The full LLM output from skill execution (single-turn for atomic skills) |
| **Outcome** | The produced artifact (YAML file, markdown, structured data) verified against criteria |
| **Evaluation Harness** | Infrastructure orchestrating execution, grading, aggregation (`run-eval.sh`) |
| **Evaluation Suite** | Collection of tasks covering a skill's capabilities (`datasets/cases.json`) |

### Key Characteristic: Single-Turn

Skills are fundamentally **single-turn prompt executions** (input -> skill instructions -> output). This makes them significantly simpler to evaluate than multi-turn agent systems. The eval loop is:

```
for each case in dataset:
    for trial in 1..k:
        output = execute_skill(skill_instructions, case.input)
        det_score = deterministic_grader(output, case.expected)
        llm_score = llm_judge(case.input, output, rubric)
    aggregate(scores) -> pass@1, pass@k, pass^k
```

---

## 2. Framework Analysis

### Promptfoo

**Overview**: Open-source CLI and library for prompt testing, evaluation, and comparison. Node.js/TypeScript native. YAML-driven configuration. Active development with GitHub Actions integration.

**Capability for Skills Eval**:
- **Prompt-as-file**: Prompts can be loaded from files (`file://path/to/prompt.md`), which means a SKILL.md body can be treated as a prompt template directly.
- **Model comparison**: Define multiple providers (Claude, GPT, Llama, etc.) side-by-side. The matrix view shows the same skill tested across models with identical inputs.
- **Custom graders**: Supports JavaScript assertions (`type: javascript`, `value: file://grader.js:customFunction`) and Python assertions that return `GradingResult` objects with pass/fail, score, and reasoning. Also supports `llm-rubric` for model-graded evaluation with configurable judge model.
- **Deterministic assertions**: Built-in `contains`, `regex`, `json-schema`, `cost`, `latency` assertion types.
- **CI/CD**: First-class GitHub Actions integration. YAML configs version-controlled.

**Fit for Skills Eval**: **Strong**. Promptfoo's architecture — prompt file + providers + test cases + assertions — maps almost 1:1 to Skills Eval (SKILL.md + models + dataset cases + graders). The custom JavaScript grader capability means our existing `deterministic.js` logic could be wrapped as a Promptfoo assertion with minimal adaptation.

**Gaps**:
- No native understanding of SKILL.md YAML frontmatter (would need a thin loader to strip frontmatter and extract the body as prompt).
- No built-in concept of "trials" for non-determinism measurement (pass@k). Would need custom orchestration or wrapper to run k trials per test case.
- Custom graders returning a `GradingResult` are limited to (pass, score, reason) — no native support for multi-dimensional scoring (our deterministic grader returns 24+ individual checks).

### OpenAI Evals

**Overview**: Open-source framework with 17,600+ GitHub stars. Now has an API-based Evals product in the OpenAI platform alongside the open-source framework. Primarily Python-based.

**Capability for Skills Eval**:
- **Prompt evaluation**: Supports templated prompts with variable substitution, dataset-driven evaluation, and model-graded evaluation where models score outputs.
- **Grading**: Supports "model-graded" evaluation and deterministic matching. The Evals API added a Prompt Optimizer for eval-improve-re-eval loops.
- **Model comparison**: Natively designed for comparing model outputs (OpenAI models). Less ergonomic for cross-vendor comparison (Claude vs GPT).

**Fit for Skills Eval**: **Moderate**. Competent for the eval-grade loop but designed around OpenAI's ecosystem. Cross-model comparison is less natural. Python-based, which doesn't align with the project's Node.js stack (existing graders are all JavaScript).

**Gaps**:
- OpenAI-centric provider model. Testing Claude skills through OpenAI Evals adds unnecessary indirection.
- No native file-as-prompt loading that understands SKILL.md format.
- Python runtime requirement in a Node.js project adds complexity.
- The open-source repo has moved toward API-based evals on OpenAI's platform, making self-hosted usage less straightforward.

### inspect_ai (UK AI Security Institute)

**Overview**: Python framework for reproducible LLM evaluations. Opinionated primitives: `Dataset -> Task -> Solver -> Scorer`. Multi-turn agent workflows with sandboxed execution (Docker). VS Code log viewer. Used by governments and frontier labs. 50+ contributors.

**Capability for Skills Eval**:
- **Task definition**: Rich task model with datasets, solvers (prompt strategies), and scorers (grading logic).
- **Agent eval focus**: Designed primarily for evaluating agent capabilities (multi-turn, tool use, sandboxed environments). This is overkill for single-turn skill evaluation.
- **Sandboxing**: Docker-based execution sandboxing, Kubernetes adapters. Strong isolation model.
- **Model support**: Broad model support via API integrations.

**Fit for Skills Eval**: **Weak for skills, strong for agent eval**. Inspect_ai's multi-turn agent focus and Python runtime make it over-engineered for single-turn skill evaluation. However, it would be excellent for the project's Agent Eval needs (the second domain in the research brief).

**Gaps**:
- Python-only. Does not align with Node.js stack.
- Multi-turn/agent architecture adds unnecessary complexity for single-turn skills.
- No native SKILL.md format awareness.
- Sandboxed Docker execution is heavy for prompt-in/text-out skill testing.

### Others (Brief Notes)

| Framework | Relevance | Notes |
|---|---|---|
| **DeepEval** | Low | Python-first, 14+ metrics focused on RAG and fine-tuning. Not designed for prompt-template evaluation. |
| **Braintrust** | Medium | "pytest for LLMs" with offline evaluation + observability + experiment tracking. Cloud-hosted, which introduces external dependency. |
| **Langfuse** | Low | Observability/tracing platform with some eval features. More monitoring than testing. |
| **EleutherAI LM Harness** | None | Benchmark framework for model-level evaluation (MMLU, HellaSwag). Not for prompt/skill evaluation. |
| **MLflow 3.0** | Low | ML experiment tracking evolving into GenAI eval. Enterprise-focused, heavy dependency. |
| **Maxim AI** | Low | End-to-end agentic simulation. Commercial, closed-source. |

### Comparison Matrix

| Framework | Skills-Level Eval | Model Comparison | Custom Graders | Active/Maintained | Node.js Compatible |
|---|---|---|---|---|---|
| **Promptfoo** | Strong | Native (multi-provider matrix) | JS + Python + LLM-rubric | Very active | Native (npm package) |
| **OpenAI Evals** | Moderate | OpenAI models native, others awkward | Python + model-graded | Active (API pivot) | No (Python) |
| **inspect_ai** | Weak (overkill) | Good multi-model | Python scorers | Very active | No (Python) |
| **Braintrust** | Moderate | Yes | Python + custom | Active | Partial (API) |
| **Custom (current)** | Exact fit | Manual (swap `claude --model`) | Full control (JS) | Self-maintained | Native |

---

## 3. Skills-as-Graders Architecture

### The Pattern

A **Grader Skill** is an Agent Skill whose purpose is evaluating another skill's output. It follows the exact same SKILL.md format:

```
teaching-quality-grader/
  SKILL.md              # YAML frontmatter + grading rubric instructions
  scripts/
    deterministic.js    # Hard checks (word counts, format validation)
    compute-score.js    # Aggregate deterministic + LLM scores
  references/
    RUBRIC.md           # Detailed scoring dimensions
    EXAMPLES.md         # Calibration examples (score X because Y)
```

The SKILL.md body contains:
- Grading dimensions with weights
- Scoring rubric (0-10 per dimension with anchored descriptions)
- Output format specification (structured JSON)
- Calibration examples showing correct scores for reference inputs

**How it works in the eval pipeline**:

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   EVAL RUNNER    │     │   SUBJECT SKILL  │     │   GRADER SKILL   │
│   (Promptfoo /   │────>│   (e.g., generate│────>│   (e.g., teaching│
│    run-eval.sh)  │     │    flashcards)   │     │    quality grader)│
│                  │     │                  │     │                  │
│  Feeds input     │     │  Produces output │     │  Scores output   │
│  from dataset    │     │  (YAML deck)     │     │  (JSON scores)   │
└─────────────────┘     └──────────────────┘     └──────────────────┘
         │                                                │
         │           deterministic checks                 │
         ├───────────────────────────────────────────────>│
         │           (scripts/deterministic.js)           │
         │                                                │
         │           LLM judge via grader SKILL.md        │
         ├───────────────────────────────────────────────>│
         │           (model reads rubric, scores output)  │
         │                                                │
         │<───────────────────────────────────────────────┤
         │           aggregated scores                    │
         │           (pass@1, pass@k, pass^k)             │
```

The key insight: **the grader SKILL.md replaces the ad-hoc prompt currently embedded in `llm-judge.js:buildPrompt()`**. Instead of the grading rubric being hardcoded in JavaScript, it lives in a portable, versioned, independently testable skill.

### Viability Assessment

**Verdict: Viable and recommended, with constraints.**

The project already implements this pattern informally. Consider what currently exists:

1. **`evals/flashcards/graders/llm-judge.js`** — Lines 103-162 contain a `buildPrompt()` function that constructs a grading rubric inline. This IS a grader, it just isn't packaged as a Skill.
2. **`evals/assessment-architect/rubric-grader.md`** — A markdown file containing a rubric prompt template. This IS a grader skill body — it just lacks the SKILL.md frontmatter.
3. **`evals/assessment-architect/rubric.md`** — A standalone rubric document with scoring dimensions, weights, and anchored scales. This IS a `references/RUBRIC.md` file.

The existing infrastructure already separates concerns correctly (deterministic checks in JS, LLM rubric in prompt templates, aggregation in a separate module). Formalizing these as Skills adds:

- **Discoverability**: Graders become findable via the same `<available_skills>` mechanism as any other skill.
- **Portability**: Any eval runner that can load SKILL.md can use the grader.
- **Versioning**: Grader changes are tracked independently with semantic versioning.
- **Testability**: Graders can themselves be evaluated (see circularity discussion below).

### Trade-offs

**Advantages**:

1. **Portable across eval frameworks**: A grader packaged as SKILL.md can be consumed by Promptfoo (as a custom grader prompt), by our custom `run-eval.sh`, or by any future framework. The grading logic isn't locked into one harness.
2. **Versioned and independently testable**: Grader skills get their own version numbers, changelogs, and eval suites. When a grader changes, you can run its own eval to verify it still grades correctly.
3. **Follows the project's own standard**: The project teaches SKILL.md as the unit of AI work. Using Skills for grading is dogfooding — it validates the format's versatility.
4. **Progressive disclosure**: A simple grader might be just a rubric in SKILL.md body. A complex one adds `scripts/deterministic.js` for hard checks and `references/RUBRIC.md` for detailed dimensions. The format scales naturally.
5. **Reusable across domains**: A "teaching-quality-grader" can score flashcards, assessments, lesson content, or any educational output. The rubric is the constant; the subject varies.

**Disadvantages / Risks**:

1. **Bootstrapping trust**: Before a grader can grade, you need to trust the grader. This requires a one-time human calibration step — score 10-20 examples manually, then verify the grader agrees within tolerance. This is NOT unique to Skills-as-Graders; every model-based grader needs calibration (Anthropic's article emphasizes this: "LLM-based rubrics should be frequently calibrated against expert human judgment").
2. **Performance overhead**: Two LLM calls per eval trial — one to execute the subject skill, one for the grader skill to score. For k trials per case, that's 2k calls per test case. Mitigation: use a fast/cheap model for grading (Haiku), reserve expensive models for the subject.
3. **Grader drift**: If the grader skill is updated without re-calibration, scores may drift. Mitigation: anchor graders with deterministic checks (the `scripts/` layer) and calibration examples in `references/`.
4. **Added indirection**: An inline `buildPrompt()` function is simpler to debug than a separate SKILL.md file loaded by the harness. The indirection is justified only if the grader is reused across multiple contexts.

### The Circularity Question

**Is Skills-grading-Skills problematic?**

No, and here's why: the circularity is no different from model-based grading in general. When `llm-judge.js` uses Claude to score flashcard output, the grading model and the subject model are often the same model family. This is already accepted practice across the industry (Anthropic, OpenAI, and the research community all use model-based grading).

The key safeguards that prevent circularity from becoming a problem:

1. **Deterministic anchoring**: The heaviest-weighted checks in our existing harness are deterministic (24 checks in `deterministic.js` with hard gates). These don't use LLMs at all. The LLM judge layer adds subjective quality assessment on top of verified structural correctness.

2. **Human calibration baseline**: The grader is validated against human-scored golden examples. If the grader disagrees with the human baseline on known inputs, the grader is wrong — not the baseline.

3. **Separate model for grading**: Use a different model (or temperature/prompt) for grading than for generation. This breaks self-reinforcement loops.

4. **Meta-eval through golden test sets**: You CAN eval the grader — give it known-quality outputs with known-correct scores, and verify it produces those scores. The flashcard harness already does this: `baselines/baseline-v1.json` is a known-correct grading of known outputs.

**The meta-eval hierarchy**:
- **Level 0**: Deterministic checks (scripts/) — no LLM, no circularity, machine-verifiable
- **Level 1**: LLM grader with human-calibrated golden scores — validated against human judgment
- **Level 2**: Grader skill eval (eval the grader itself) — verify grader consistency on golden inputs
- **Level 3**: Human spot-checks — final arbiter when grader and baseline disagree

This is the same hierarchy used by every serious eval system. Skills-as-Graders just packages it in a portable, reusable format.

---

## 4. Concrete Example: Content Personalization Eval

### Setup

- **Subject Skill**: `content-personalization/SKILL.md` — Takes a learner profile (demographics, skill level, learning preferences) + raw lesson content, produces personalized lesson output.
- **Grader Skill**: `personalization-quality-grader/SKILL.md` — Evaluates personalized output against 5 dimensions.
- **Runner**: Promptfoo (or custom `run-eval.sh`).
- **Dataset**: Learner profiles (Fatima, Raj, Marcus) crossed with 3 lessons = 9 cases.

### Dataset Cases

```json
{
  "cases": [
    {
      "id": "CP01_fatima_lesson1",
      "input": {
        "learner_profile": "profiles/fatima.json",
        "lesson": "lessons/intro-to-agents.md"
      },
      "expected": {
        "should_personalize": true,
        "min_adaptations": 3,
        "must_reference_profile_elements": ["prior_experience", "learning_style"],
        "language_level": "intermediate"
      }
    }
  ]
}
```

### Grader Skill: `personalization-quality-grader/SKILL.md`

```yaml
---
name: personalization-quality-grader
description: >-
  Evaluate personalized lesson content against 5 quality dimensions.
  Use when scoring output from the content-personalization skill.
metadata:
  version: "1.0"
  domain: education-eval
---
```

Body contains rubric for 5 dimensions:
1. **Profile Responsiveness** (weight: 30%) — Does the output adapt to the specific learner's stated experience, goals, and preferences?
2. **Content Fidelity** (weight: 25%) — Is the core lesson content preserved accurately? No hallucinated facts?
3. **Pedagogical Appropriateness** (weight: 20%) — Is the difficulty level, example complexity, and scaffolding appropriate for the learner's stated level?
4. **Engagement Quality** (weight: 15%) — Are examples and analogies relevant to the learner's domain/context?
5. **Format Compliance** (weight: 10%) — Does output follow required format (headings, code blocks, etc.)?

Plus `scripts/deterministic.js` for:
- Format validation (YAML frontmatter present, required sections exist)
- Word count bounds (personalized output shouldn't be 5x shorter or longer than original)
- Profile element reference check (grep for learner-specific terms)

### Eval Flow (Mapped to Anthropic Abstractions)

```
TASK: CP01_fatima_lesson1
  Profile: Fatima (5 years Python, visual learner, intermediate English)
  Lesson: intro-to-agents.md

TRIAL 1:
  Execute subject skill:
    claude --model opus -p < "Given this learner profile: {fatima.json}
                               Personalize this lesson: {intro-to-agents.md}
                               Following instructions in: {content-personalization/SKILL.md}"

  TRANSCRIPT: Full Claude output (personalized lesson markdown)

  OUTCOME: The produced markdown file

  GRADING:
    Deterministic (scripts/deterministic.js):
      - format_valid: PASS (frontmatter present)
      - word_count_ratio: PASS (0.8x-1.5x of original)
      - profile_references: PASS (mentions "Python", "visual", uses diagrams)
      - language_level: PASS (Flesch-Kincaid matches "intermediate")

    LLM Judge (personalization-quality-grader/SKILL.md):
      - profile_responsiveness: 8/10 ("adapts examples to Python but doesn't leverage visual learning style enough")
      - content_fidelity: 9/10 ("all core concepts preserved, no hallucination detected")
      - pedagogical_appropriateness: 7/10 ("difficulty appropriate but scaffolding could be more gradual")
      - engagement_quality: 8/10 ("Python examples relevant, could add more domain-specific analogies")
      - format_compliance: 10/10

TRIAL 2: (repeat for non-determinism measurement)

AGGREGATE:
  pass@1: PASS (trial 1 met all hard gates)
  pass@k: PASS (at least one trial passed)
  pass^k: PASS (all trials passed — consistent)
  deterministic_mean: 92
  llm_judge_mean: 84
  consistency_score: 96
```

### Baseline Comparison

After running the initial eval, save `summary.json` as `baseline-v1.json`. When the content-personalization skill is modified:

```bash
./run-eval.sh --baseline baselines/baseline-v1.json --run-id candidate-v2
```

Output:
```
Delta deterministic_mean: +2 (94 vs 92) -- IMPROVEMENT
Delta llm_judge_mean: -1 (83 vs 84) -- WITHIN TOLERANCE
Delta pass@1: 0% -- STABLE
```

---

## 5. Dataset Requirements

Skills Evals need three types of datasets:

### 1. Functional Test Cases (Required)

Minimal viable dataset for any skill eval. Contains input-output pairs with expected constraints.

```json
{
  "cases": [
    {
      "id": "unique_case_id",
      "input": { "source_data": "path/to/input" },
      "expected": { "constraints": "..." },
      "golden_outputs": ["path/to/known-good-output"]
    }
  ]
}
```

**Minimum**: 5 cases covering happy path, edge cases, and at least one negative control.

**The flashcard harness exemplifies this well**: 5 cases covering explicit trigger, implicit trigger, negative control, formula-heavy input, and multi-lesson chapter mode.

### 2. Golden Outputs (Recommended)

Human-verified "known good" outputs that serve as:
- Baseline for regression detection
- Calibration inputs for grader validation
- Reference for LLM-as-judge comparison scoring

**Creation**: Generate output, have a domain expert review and correct it, freeze as golden.

### 3. Learner/User Profiles (For Personalization Skills)

Diverse synthetic profiles representing the target user population. Should cover:
- Experience levels (beginner, intermediate, advanced)
- Domain backgrounds (different industries/roles)
- Learning preferences (visual, textual, hands-on)
- Language levels (if applicable)

### Dataset Quality Principles

From the Anthropic article and the project's own experience:

1. **Source from real failures**: Convert actual skill failures into test cases.
2. **Ensure solvability**: If a human expert couldn't produce correct output from the input, the test case is broken.
3. **Balance positive and negative**: Include cases where the skill should NOT produce output (negative controls).
4. **Version datasets separately from skills**: Dataset changes can cause score changes even when the skill hasn't changed. Track both.

---

## 6. Recommendation

### Framework Recommendation for Skills-Level Eval

**Recommended: Hybrid approach — keep custom harness, adopt Promptfoo for model comparison.**

**Rationale**: The project already has a well-designed custom eval harness (`evals/flashcards/`) that maps precisely to Skills Eval needs. It has deterministic graders (24 checks), LLM-as-judge grading (15 criteria), aggregation (pass@1, pass@k, pass^k), and baseline comparison. Replacing this with Promptfoo would lose fidelity without gaining much.

However, Promptfoo excels at one thing the custom harness doesn't do well: **model comparison**. Testing the same skill across Claude Opus, Claude Sonnet, Claude Haiku, and GPT-4o in a matrix view is valuable for model selection decisions.

**Concrete recommendation**:

| Layer | Tool | Why |
|---|---|---|
| **Primary eval runner** | Custom harness (`run-eval.sh` pattern) | Already built, exact fit, full control |
| **Model comparison** | Promptfoo | Native multi-provider matrix, YAML config, CI/CD |
| **Deterministic graders** | Custom JS (existing `deterministic.js` pattern) | 24+ checks, hard gates, weighted scoring |
| **LLM judge graders** | **Migrate to Grader Skills** | Portable rubrics, versioned, independently testable |
| **Aggregation** | Custom JS (existing `aggregate.js` pattern) | pass@k, pass^k, baseline diff |

### Skills-as-Graders Verdict

**Yes, with a phased approach.**

**Phase 1 (immediate)**: Extract the existing flashcard LLM judge rubric from `llm-judge.js:buildPrompt()` into a proper `flashcard-quality-grader/SKILL.md`. Extract the assessment-architect rubric from `rubric-grader.md` into `assessment-quality-grader/SKILL.md`. The `scripts/` directories contain the existing deterministic grader logic. No new capabilities needed — just repackaging.

**Phase 2 (next sprint)**: Build a generic grader-skill loader that `run-eval.sh` uses instead of hardcoded `buildPrompt()`. The loader reads the grader SKILL.md, injects case context, and calls the judge model. This makes the harness grader-agnostic.

**Phase 3 (future)**: Create new grader skills for new eval domains (content personalization, agent performance). Each grader gets its own calibration dataset and meta-eval.

---

## 7. Open Questions

1. **Grader skill location**: Should grader skills live in `.claude/skills/` (alongside operational skills) or in `evals/<domain>/graders/` (alongside the eval infrastructure they serve)? The argument for `evals/` is that graders are eval infrastructure, not user-facing skills. The argument for `.claude/skills/` is that the SKILL.md format implies discoverability by agents.

2. **Calibration dataset creation**: Who creates the golden scores for grader calibration? This requires domain expertise (e.g., Sir Zia for flashcard quality). What's the process for periodic re-calibration?

3. **Model-as-grader cost**: At 2 LLM calls per trial, 5 cases, 3 trials each = 30 LLM calls per eval run. With Haiku this is cheap (~$0.05). With Opus this is significant (~$3.00). What's the budget model for CI-triggered evals?

4. **Cross-skill grader reuse**: Can a single "educational-content-grader" serve flashcards, assessments, and personalized lessons? Or does each domain need its own grader? The rubric dimensions are different enough that separate graders seem necessary, but there may be shared infrastructure (source-grounding checks, format validation).

5. **Promptfoo integration depth**: Should Promptfoo be used only for model comparison, or should we migrate the full eval pipeline to Promptfoo config? The custom harness has features Promptfoo lacks (pass^k, multi-dimensional deterministic scoring). But Promptfoo has features the custom harness lacks (web UI, CI GitHub Action, model matrix).

6. **Deterministic vs. LLM grading ratio**: The flashcard harness uses 24 deterministic checks (hard gates) + 15 LLM criteria. Is this ratio appropriate for other skills? Skills with more subjective output (personalization, teaching guides) may need to weight LLM grading more heavily.
