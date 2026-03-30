# AI Employee Eval Gap Analysis

## 1. The 4-Layer Architecture

### Layer 0: Continuous Improvement Substrate

**What it claims to be:** "The system gets better at getting better." Eval results feed back into improving the system, which generates new eval requirements. A recursive loop where running evals -> finding weaknesses -> fixing weaknesses -> generating new eval cases from production failures.

**What already exists:**

- **Braintrust** explicitly implements this loop. Their documentation describes: "production traces become eval datasets with one click, evals validate changes, validated changes deploy with confidence." They use identical scoring for offline and online, and low-scoring production examples automatically feed back into offline eval datasets. This is exactly the "continuous improvement substrate" described.
- **Langfuse** implements a three-phase strategy: online evaluation in production -> offline benchmark datasets -> feedback collection. Production traces can be annotated, flagged, and converted to test cases.
- **Arize** combines evaluation workflows with production monitoring, supporting replaying traces and iterating on prompts from production data.
- **Maxim AI** explicitly unifies "pre-release testing directly to production monitoring" as its core value proposition.
- **Galileo** "auto-tunes metrics from live feedback to create evals fit to your environments."
- **OpenAI Cookbook** describes "Self-Evolving Agents" with autonomous retraining from eval feedback.

**Gap assessment:** The loop itself (run evals -> find failures -> create new test cases -> improve -> repeat) is well-supported by Braintrust, Langfuse, and others. What's potentially novel is the *meta-level*: automatically deciding WHAT to eval next based on patterns in failures, not just feeding individual failures back. However, even that is emerging (Galileo's auto-tuning, Braintrust's Loop feature generating custom scorers from natural language).

**Classification: Process Discipline on Existing Framework Features**

The infrastructure exists. What's needed is the discipline to wire it up and run it consistently. Braintrust's production-to-eval-dataset pipeline is literally this layer. The only custom work is domain-specific: defining what "improvement" means for an AI teaching employee (better learning outcomes, not just better LLM scores).

---

### Layer 1: Component Evals (Ranking Table)

**What it claims to be:** Sir Zia's "variable x across -> ranking table" pattern. Example: Model x Student Type -> Teaching Quality Score. A matrix view showing how different models/prompts/configurations perform across different dimensions.

**What already exists:**

- **Promptfoo** is literally built for this. Its core feature is a YAML config listing multiple providers (models) and multiple test cases, producing a matrix view for side-by-side comparison. Example config:
  ```yaml
  providers:
    - openai:gpt-4.1
    - anthropic:claude-sonnet-4-20250514
  tests:
    - vars: {student_type: "beginner", topic: "loops"}
    - vars: {student_type: "advanced", topic: "recursion"}
  ```
  This produces exactly the "Model x Student Type -> Ranking Table" described.
- **Braintrust** supports experiment comparison with pre-built scorers and custom metrics, plus leaderboard-style comparison views.
- **LLM Leaderboards** (Artificial Analysis, LLM-stats.com, Onyx) already provide model ranking across dimensions, though not for custom domain tasks.

**Gap assessment:** The ranking table pattern is a direct configuration of Promptfoo's comparison feature. The custom part is:
1. Defining the test cases (student personas, teaching scenarios)
2. Defining the grading rubrics (what makes teaching "good")
3. Potentially custom aggregation (session-level scoring across multi-turn teaching interactions, not just turn-level)

Multi-turn session-level scoring is partially supported: Promptfoo has conversation relevance scoring and derived metrics for aggregation. But scoring a full *teaching session* holistically (did the student learn?) rather than turn-by-turn is a custom grader concern, not infrastructure.

**Classification: Framework Feature + Custom Grading Rubric**

Promptfoo handles the infrastructure (run models, compare, display matrix). The novel work is designing grading rubrics that measure teaching quality — but that's rubric design, not infrastructure. Session-level aggregation may need a thin custom scoring layer.

---

### Layer 2: Personalization Evals

**What it claims to be:** Evaluating two separate dimensions:
- **Content WHAT**: Was WHAT was taught adapted to the learner? (right difficulty, right examples, right progression)
- **Interaction HOW**: Was HOW it was delivered adapted? (tone, pacing, scaffolding style, encouragement patterns)

**What already exists:**

- **Adaptive learning research** measures personalization through: learning gain (pre/post test), engagement metrics, system prediction accuracy (AUC for predicting learner knowledge state), response time patterns, and recurring error analysis.
- **No existing eval framework** distinguishes between content personalization and interaction personalization as separate dimensions. All the frameworks (Promptfoo, Braintrust, Langfuse) provide infrastructure to run any eval you define, but the WHAT vs HOW distinction is purely a grading rubric concern.
- **Tau-bench/Tau2-bench** introduced persona-based evaluation with varying difficulty levels (Easy/Hard user personas), which is conceptually similar — testing whether an agent adapts to different user types. But it measures task completion, not teaching quality.

**Gap assessment:** The content-vs-interaction split is a conceptual framework for WHAT to measure, not HOW to measure it. Any eval framework can run these evals once you define the graders. The graders themselves are the innovation:
- Content grader: "Given this learner profile, was the content appropriately adapted?" (LLM-as-judge with rubric)
- Interaction grader: "Given this learner profile, was the delivery style appropriately adapted?" (LLM-as-judge with rubric)

These are two different LLM judge rubrics, not two different pieces of infrastructure.

**Classification: Grading Rubric Design (not infrastructure)**

The insight that content and interaction should be evaluated separately is valuable pedagogical thinking. But it translates to "write two different grading rubrics" not "build two different systems." Any LLM-as-judge framework can host these rubrics. The novelty is in the rubric content, not the eval machinery.

---

### Layer 3: Dual-Mode Engine

**What it claims to be:** Two evaluation modes running in parallel with a bridge between them:
- **Simulation mode** (offline): Synthetic students, controlled scenarios, rapid iteration
- **Production mode** (online): Real users, real data, real outcomes
- **Bridge loop**: Findings from production inform new simulation test cases; simulation results predict production behavior

**What already exists:**

- **Braintrust** explicitly bridges offline and online: "online scoring monitors live requests, feeds low-scoring examples back into offline evals, and creates systematic quality improvements over time." Production traces become eval datasets with one click. This is the bridge loop.
- **Maxim AI** explicitly unifies "simulation, evaluation, and observability across the complete AI agent lifecycle" — connecting pre-release testing to production monitoring.
- **Arize** combines evaluation workflows with production monitoring, supporting dataset creation from production traces.
- **Langfuse** provides both online evaluation (auto-scoring production traces) and offline evaluation (benchmark datasets), with annotation workflows bridging them.
- **Label Studio** describes a framework: "Use offline evaluation as your default engine for iteration and use online evaluation as your reality check."
- **Capital One** published an offline evaluation framework that enables "new algorithms to be simulated and tested in a pseudo production environment."

**Gap assessment:** The dual-mode pattern is well-established in ML ops and now in LLM ops. Braintrust and Maxim AI have this as a core feature. The "bridge loop" (production failures -> new simulation cases) is Braintrust's one-click trace-to-dataset feature.

What might be custom: the *simulation side* specifically. Using LLMs to simulate different student types interacting with the AI Employee requires:
1. Persona definitions (student types with learning profiles)
2. Multi-turn simulation (not just single-turn)
3. Session-level outcome measurement (did the simulated student "learn"?)

This is where tau-bench's approach is relevant — LLM-simulated users with personas. Promptfoo also has a "Simulated User Provider" for multi-turn conversation testing.

**Classification: Framework Feature (bridge) + Custom Simulation Layer (student personas)**

The bridge between offline and online evaluation is a solved problem (Braintrust, Maxim). The custom work is building domain-specific simulated students that behave like real learners — persona definitions, learning progression modeling, and outcome measurement. This is closer to "custom grading + test fixture design" than "novel infrastructure."

---

## 2. The Simulator Pattern

### What It Requires

Sir Zia's signature: Model x Student Type -> Ranking Table. Technically this requires:

1. **Persona management**: Definitions of different student types (beginner, intermediate, expert; fast learner, struggling; different backgrounds; different learning styles)
2. **Multi-turn simulation**: An LLM playing each student persona through a full teaching session (not just one exchange)
3. **Session-level scoring**: Grading the entire teaching session holistically (did the student achieve the learning objective?) not just individual turns
4. **Matrix aggregation**: Combining scores across persona x model x scenario into ranking tables
5. **Statistical significance**: Determining whether Model A is genuinely better than Model B for a given student type, accounting for LLM non-determinism

### What Exists

- **Promptfoo's Simulated User Provider**: Enables multi-turn conversation testing with configurable simulated users. Supports custom system prompts for personas. Provides conversation-level relevance scoring and derived metrics for aggregation. This covers requirements 1-4 partially.
- **Tau-bench / Tau2-bench**: Demonstrates the LLM-simulated-user pattern at scale with persona support (Easy/Hard users). Proves the pattern works. Uses gpt-4 as user simulator.
- **Promptfoo's comparison matrix**: Handles requirement 4 natively — multiple providers x multiple test cases -> matrix view.
- **pass@k and pass^k metrics**: From Anthropic's eval taxonomy, these handle requirement 5 for statistical reliability measurement.

### What's Missing

The gap is primarily in **domain-specific test fixture design**, not infrastructure:

1. **Student persona library**: Defining realistic student archetypes for AI agent education. This is content creation, not engineering.
2. **Learning outcome measurement**: How do you evaluate whether a simulated student "learned"? This requires custom grading logic — perhaps a post-session quiz for the simulated student, or rubric-based assessment of whether key concepts were communicated.
3. **Session coherence scoring**: Existing tools score turn-by-turn or with sliding windows. Scoring an entire 15-turn teaching session for pedagogical coherence (scaffolding, appropriate difficulty progression, misconception handling) needs a custom LLM judge rubric.
4. **Cross-run aggregation into ranking tables**: Promptfoo handles basic comparison. But producing a clean "Model x Student Type -> Score" ranking table with confidence intervals may need a thin reporting layer on top.

**Effort estimate**: ~2-3 weeks of configuration + rubric design on Promptfoo. Not a new system — a configured system with custom graders.

---

## 3. Progressive Personalization Eval

### The Challenge

Sir Zia's Q3: "Is the system's model of the learner improving over time?"

This is longitudinal evaluation — tracking whether the AI Employee gets better at teaching a specific student across multiple sessions. It requires:

1. A persistent learner model that accumulates across sessions
2. Evaluation at time T that compares to evaluation at time T-1
3. Metrics that capture "knows this student better" (e.g., fewer clarification questions needed, better difficulty calibration, more accurate prerequisite assessment)

### What Exists

- **No eval framework supports cross-session longitudinal evaluation natively.** All frameworks (Promptfoo, Braintrust, Langfuse) evaluate individual sessions or individual completions. They can track *trends* across experiments (is the system improving overall?) but not "is it improving for THIS specific user?"
- **Academic research** acknowledges this gap: "capturing these dynamics requires longer-term studies, though challenges in deployment, evaluation design, and data collection have made such longitudinal research difficult to implement."
- **Adaptive learning platforms** (like those reviewed in Springer research) measure longitudinal outcomes through pre/post testing and retention testing, but this is educational measurement methodology, not eval infrastructure.

### What's Missing

This is the most genuinely novel requirement:

1. **Session-chaining in eval**: Running eval session 1 -> saving learner state -> running eval session 2 with that state -> comparing outcomes. No framework supports this out of the box.
2. **Learner model accuracy metrics**: Defining what "knows the student better" means quantitatively. Possible proxies:
   - Prediction accuracy: Can the system predict what the student will struggle with? (Measurable)
   - Calibration speed: How quickly does the system adjust to a new student? (Measurable with session count)
   - Unnecessary scaffolding reduction: Does it stop over-explaining things the student already knows? (Measurable via transcript analysis)
3. **Temporal dataset design**: Test cases that span multiple sessions with evolving student state.

**However**, this can be decomposed:
- The *eval harness* part (running sessions, recording results, comparing over time) is just "run eval, store results, diff." Braintrust's experiment comparison can do temporal tracking.
- The *learner model assessment* is a custom grading rubric applied at each time point.
- The *session chaining* is the only piece requiring custom scripting — a wrapper that maintains state across eval runs.

**Effort estimate**: The infrastructure need is modest — a script that chains eval sessions and diffs results over time. The hard part is defining WHAT to measure, which is rubric/metric design. ~1-2 weeks of custom scripting on top of an existing framework + ongoing rubric refinement.

---

## 4. The Honest Assessment

| Layer | Classification | Effort to Build | Existing Coverage |
|---|---|---|---|
| L0: Continuous Improvement | **Process Discipline** | Low (setup + habit) | Braintrust's prod-to-eval pipeline covers 90%+ |
| L1: Component Evals (Ranking) | **Framework Feature + Rubric** | Low-Medium (config + rubrics) | Promptfoo comparison matrix covers infrastructure; rubrics are custom |
| L2: Personalization Evals | **Grading Rubric Design** | Medium (rubric design + validation) | Any LLM-as-judge framework; innovation is in WHAT we grade |
| L3: Dual-Mode Engine | **Framework Feature + Custom Sim** | Medium (student personas + session scoring) | Braintrust/Maxim bridge loop; Promptfoo simulated users |

### What's Genuinely Novel

Almost nothing at the infrastructure level. The genuine novelty is in:

1. **Student persona library for AI agent education** — No one has built archetypes for "students learning to build AI agents." This is content/domain expertise, not engineering.
2. **Teaching quality grading rubrics** — The specific rubrics for evaluating "did this AI teach well?" with the content-WHAT / interaction-HOW split. This is pedagogical expertise encoded as LLM judge prompts.
3. **Session-chaining for longitudinal eval** — A thin scripting layer (~200-500 lines) that chains eval sessions and tracks learner model accuracy over time. This is the only piece that requires custom code, and it's modest.

### What's Just Process

- **Layer 0 entirely** — "Run evals regularly, feed failures back, track trends." Braintrust does this with clicks, not code. The discipline to actually do it consistently is the challenge.
- **The bridge loop in Layer 3** — Production traces becoming test cases is a Braintrust feature. Using it is process discipline.
- **Running evals before and after changes** — CI/CD integration with eval frameworks. Promptfoo and Braintrust both support this natively.

### What's Just Rubric Design

- **Layer 2 entirely** — Content personalization vs interaction personalization is a distinction in what your LLM judge looks for, not in what system runs the eval. Write two rubrics, run them on the same framework.
- **Most of Layer 1** — The ranking table is Promptfoo's matrix view. The custom part is defining "Teaching Quality Score" — which is a grading rubric.
- **Teaching quality metrics** — What makes a teaching session "good"? Scaffolding? Difficulty progression? Misconception handling? These are rubric specifications, not infrastructure.

---

## 5. Framework Coverage Map

| Framework | L0 (Continuous) | L1 (Ranking) | L2 (Personalization) | L3 (Dual-Mode) | Notes |
|---|---|---|---|---|---|
| **Promptfoo** | Partial (no prod monitoring) | Strong (matrix comparison) | Supports any grader | Partial (simulation yes, prod no) | Best for offline ranking/comparison |
| **Braintrust** | Strong (full loop) | Good (experiment comparison) | Supports any grader | Strong (bridge loop native) | Best unified offline+online |
| **Langfuse** | Good (3-phase strategy) | Basic (needs custom) | Supports any grader | Good (online+offline) | Best for self-hosted/open-source |
| **Maxim AI** | Good (unified platform) | Good (comparison views) | Supports any grader | Strong (simulation+monitoring) | Best full-lifecycle platform |
| **Arize** | Good (monitoring+eval) | Basic | Supports any grader | Good (trace replay) | Best for enterprise ML ops |

**Key insight**: All frameworks can host any grading rubric. The differentiator is operational workflow (how easily production feeds into eval), not grading capability. No framework is missing the ability to run custom rubrics — they're all extensible.

---

## 6. Recommendation

### What Needs Building (Custom Code)

1. **Session-chaining eval wrapper** (~200-500 lines): Script that runs eval session N, saves state, runs session N+1 with accumulated state, diffs improvement metrics. Sits on top of any framework.
2. **Student persona definitions** (content, not code): 5-10 student archetypes for AI agent education domain with behavioral descriptions for LLM simulation.
3. **Teaching quality grading rubrics** (prompts, not code): LLM-as-judge rubrics for content adaptation, interaction adaptation, scaffolding quality, and misconception handling.

### What Needs Configuring (Framework Setup)

1. **Promptfoo config** for Model x Student Type ranking matrix with simulated users
2. **Braintrust integration** for production monitoring -> eval dataset feedback loop
3. **CI/CD hooks** to run eval suites on prompt/skill changes

### What Needs Process (Habit, Not Technology)

1. **Regular eval cadence** — weekly runs, trend tracking, threshold alerts
2. **Production trace review** — flagging low-quality sessions for eval dataset inclusion
3. **Rubric refinement** — updating grading rubrics based on what production reveals

### Bottom Line

The 4-layer vision is approximately 70% existing framework features, 20% grading rubric design (pedagogical expertise), and 10% custom scripting. The risk is over-engineering infrastructure when the real challenge is defining what "good teaching" means in measurable terms. Start with Promptfoo for ranking + Braintrust for production loop, invest heavily in rubric design, and add the thin longitudinal layer only when the base evals are running.

---

## 7. Open Questions

1. **Framework selection**: Promptfoo (best ranking, open-source, lightweight) vs Braintrust (best production bridge, hosted) vs combining both? This is a build-vs-buy and ops maturity decision.
2. **Simulated student fidelity**: How realistic do simulated students need to be? Simple personas (beginner/advanced) or rich behavioral models (learning style, prior knowledge, common misconceptions)? Fidelity affects effort significantly.
3. **Learning outcome ground truth**: How do we know a simulated student "learned"? Post-session quiz? Rubric-based transcript analysis? This is the hardest measurement problem and it's pedagogical, not technical.
4. **Longitudinal eval priority**: Is cross-session improvement measurement a launch requirement or a Phase 2 feature? It's the most custom piece and could be deferred.
5. **Existing eval infrastructure integration**: The project already has `evals/flashcards/` with deterministic and LLM judge graders. How much of this can be reused vs needs to be migrated to a framework?
6. **Who designs the rubrics?**: Teaching quality rubrics require pedagogical expertise, not just engineering. Does the team have access to learning science input, or will rubrics be designed empirically through iteration?
