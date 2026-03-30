# Agent Eval Landscape

## 1. What Is an "Agent Eval"?

An agent eval evaluates **multi-turn, tool-using agent systems** — not just a single prompt-response pair. Where traditional LLM evals test a function (`given input X, does output Y meet criteria Z?`), agent evals test a **system with emergent behavior**: an agent harness + model + tools + skills working together across multiple conversational turns.

Key differences from prompt-level evals:

- **Statefulness**: The agent maintains context across turns; evaluating turn 5 requires turns 1-4 to have happened correctly
- **Tool use**: The agent calls external tools; correctness means both the right tool selection AND correct parameters
- **Non-determinism**: Multiple valid paths exist to solve the same task; rigid step-checking penalizes creative but valid approaches
- **Outcome orientation**: What matters is the final state (was the database updated correctly?) not just the text output
- **Reliability**: pass@1 (can it solve once?) vs pass^k (can it solve consistently?) — agents that pass@10 but fail pass^5 are unreliable

**Why this matters for us**: TutorClaw is a multi-turn, tool-using conversational agent. A student asks a question, TutorClaw responds (potentially using tools to fetch lesson content, check knowledge state, generate exercises), the student follows up, and this continues for 5-20 turns. Traditional prompt evals cannot capture whether TutorClaw maintains pedagogical coherence across a session.

---

## 2. Framework Analysis

### Promptfoo

**What it is**: Open-source CLI for testing prompts, agents, and RAGs. Declarative YAML configuration, CI/CD integration, web UI for results.

**Multi-turn support**: Yes, via `_conversation` variable and `sessionId` + `runSerially: true` configuration. Each conversation maintains its own history. However, developers must **explicitly define each user turn** — there is no automatic simulated user. Multi-turn is sequential (concurrency 1), which slows evaluation at scale.

**Tool verification**: Yes. For coding agents, it supports `anthropic:claude-agent-sdk` provider with tool assertions. Can verify tool calls via JavaScript assertions on output or trace inspection.

**Model comparison**: **Excellent** — this is Promptfoo's strongest feature. Configuration is `prompt x model x test case` matrix. Adding a new model is one YAML line. Side-by-side comparison with `select-best` assertions. Supports OpenAI, Anthropic, Azure, Bedrock, Ollama, and custom providers.

**Simulated users**: **Not natively**. You can build a custom provider that calls another LLM to generate user turns, but it requires custom code. The framework is designed for pre-scripted test cases, not dynamic simulation.

**Gaps**: No native simulated user agent; multi-turn is explicitly scripted (not generated); limited to single-threaded execution for conversation tests; no built-in persona modeling.

**Verdict**: Best for **model comparison** and **regression testing** with pre-defined conversation scripts. Not ideal for dynamic multi-turn simulation.

---

### Braintrust

**What it is**: Commercial AI observability + evaluation platform. Combines tracing, evaluation, and production monitoring in one tool. Raised $80M Series B in Feb 2026.

**Multi-turn support**: Yes, via sessions that capture complete user journeys across multiple turns. Timeline view for replaying agent workflows, thread view for conversation-style interactions. Traces capture every tool call, decision point, latency, and cost.

**Tool verification**: Yes. Traces automatically capture tool calls with parameters, return values, and timing. Can write scorers that inspect traces for correct tool usage.

**Model comparison**: **Good**. Run experiments against datasets, compare prompts/models side-by-side. Load production traces, modify model config, rerun and compare. Built-in autoevals (factuality, helpfulness) plus custom scorers.

**Simulated users**: **Not natively**. Designed to evaluate recorded traces (production or synthetic), not to generate simulated conversations. You'd need to generate conversations externally and feed them to Braintrust for scoring.

**Cost tracking**: **Excellent**. Per-trace cost breakdown by model, aggregate cost analytics, cost per task metrics.

**Pricing**: Free tier (1M spans, 10K scores, 14-day retention), Pro at $249/month, Enterprise custom. The cost tracking and observability features justify the price for production systems.

**Gaps**: No conversation simulation; more of an observability+eval platform than an agent testing framework; commercial (no self-hosting option).

**Verdict**: Best for **production monitoring + evaluation** of deployed agents. Strongest when you already have conversations to score. Weak for pre-deployment simulation testing.

---

### Langfuse

**What it is**: Open-source (MIT license, acquired by ClickHouse) LLM observability platform. Tracing, prompt management, evaluations, and cost tracking. Self-hostable.

**Multi-turn support**: Yes, traces capture full conversation flows with nested spans for each turn/tool call. Integrates with LangGraph, OpenAI Agents, Pydantic AI, CrewAI.

**Tool verification**: Via trace inspection — captures tool calls, parameters, and results as spans within traces.

**Model comparison**: Limited to comparing traces from different runs. No built-in experiment comparison like Promptfoo or Braintrust. You can filter by tags/metadata to compare model variants.

**Simulated users**: **No**. Pure observability platform — captures and scores existing conversations, does not generate them.

**Cost tracking**: **Excellent**. Token-level cost tracking, Daily Metrics API for aggregate usage by application/user/tag.

**Pricing**: Open source, self-hostable (MIT). Cloud hosting available.

**Gaps**: More observability than eval; no experiment comparison workflow; no conversation simulation; evaluation capabilities are secondary to tracing.

**Verdict**: Best as an **observability layer** to complement an eval framework. Self-hosting + open source makes it attractive for data-sensitive environments. Use it to **capture traces**, score elsewhere.

---

### inspect_ai (UK AISI)

**What it is**: Open-source Python framework from the UK AI Security Institute for reproducible LLM evaluations. Purpose-built for agent evaluation. 100+ pre-built eval tasks.

**Multi-turn support**: **Excellent**. Core architecture is `Dataset -> Task -> Solver -> Scorer`, where solvers can implement arbitrary multi-turn agent loops. Custom solver functions can loop `generate()` calls with tool use for multi-turn dialog. Message history is maintained in `state.messages`.

**Tool verification**: **Built-in**. Tools are first-class in the solver pipeline. Agent solvers (ReAct, custom) can call tools, and scorers can inspect the full transcript including all tool calls.

**Model comparison**: **Good**. Tasks are model-agnostic — swap the model parameter and rerun. The `inspect_eval` platform provides multi-model comparison views. However, comparison is per-run rather than native side-by-side.

**Simulated users**: **Not natively built-in, but architecturally natural**. A custom solver can call a second model to generate user turns within the evaluation loop. The solver/generate architecture makes this straightforward to implement — it's ~20 lines of Python. The framework doesn't provide pre-built user simulators, but the composable architecture makes building one easier than any other framework.

**Sandboxing**: **Excellent**. Docker built-in, optional Kubernetes and Proxmox adapters. Agents run in isolated containers. This is critical for agentic evals where agents execute code.

**Multi-agent**: Supports composing agents in multi-agent architectures where conversation history is shared across agents. Can run external agents (Claude Code, Codex CLI, Gemini CLI).

**Gaps**: No pre-built simulated user agent; no built-in cost tracking; no production monitoring (eval-only, not observability); Python-only.

**Verdict**: **Most architecturally suited for our agent eval use case**. The solver/tool/scorer pipeline directly maps to TutorClaw evaluation. Building a simulated student as a custom solver is natural. The sandboxing story is strong for agents that execute code.

---

### Harbor (Laude Institute / Stanford)

**What it is**: Framework for evaluating agents in containerized environments. Grew out of Terminal-Bench benchmark. Focused on coding agents and RL training.

**Multi-turn support**: Via container-based interactions — the agent operates in a Docker container, and the eval captures the full session.

**Simulated users**: No — designed for task-based agent evaluation (complete this coding task), not conversational evaluation.

**Model comparison**: Supports running different models in the same container setup. Infrastructure for large-scale parallel runs (thousands of containers on Modal/Daytona).

**Gaps**: Focused on coding agent evaluation (SWE-bench style); not designed for conversational agents; too infrastructure-heavy for our current needs.

**Verdict**: **Not relevant for TutorClaw eval**. Great for evaluating coding agents at scale, but our domain is conversational teaching, not containerized task completion.

---

### LangWatch + Scenario Framework

**What it is**: LangWatch is an AI agent testing and LLM evaluation platform. **Scenario** is its open-source (MIT) agent testing framework, available in Python, TypeScript, and Go.

**Multi-turn support**: **Excellent** — this is its primary design goal. Simulation-based testing where agents interact in multi-turn conversations.

**Simulated users**: **NATIVE AND FIRST-CLASS**. `UserSimulatorAgent` automatically generates realistic user messages based on scenario descriptions. Can operate independently or within a scripted flow. The simulated user uses LLMs to generate contextually appropriate, varied responses.

**Judge agent**: **Built-in**. `JudgeAgent` evaluates conversations against specified criteria **in real-time** — can stop a simulation early if criteria are met or violated. Supports custom evaluation logic.

**Scenario definition**: Define a test by name, description, agent adapter (wrapping your agent), user simulator, and optional judge. Can be fully automated (let simulation play out) or scripted (control specific turns).

**Integration**: Agent-agnostic via a simple `AgentAdapter` with a single `call()` method. Works with any agent framework.

**Model comparison**: Not built-in as a first-class feature — you'd run scenarios with different model configs and compare results externally.

**Gaps**: No built-in model comparison matrix; no cost tracking; relatively new (less battle-tested than Promptfoo/inspect_ai); evaluation is simulation-focused (less coverage for deterministic grading).

**Verdict**: **Strongest simulated user support of any framework reviewed**. The Scenario framework is exactly the pattern TutorClaw eval needs: simulated student + agent under test + real-time judge. MIT licensed, multi-language support. Main gap is model comparison, which could be layered on top.

---

### Others Noted

- **Maxim AI**: Commercial platform with strong multi-turn simulation, persona modeling, and evaluation. Supports "complex tool use patterns, diverse user persona modeling, and multi-agent interaction testing." Most feature-complete commercial option but proprietary.
- **LangSmith**: LangChain-native with Insights Agent that categorizes failure modes across traces. Strong multi-turn eval, but tightly coupled to LangChain ecosystem.
- **Evidently AI**: Open-source monitoring focused on data/ML observability. Has agent benchmarking compendium but not a primary agent eval framework.

---

### Comparison Matrix

| Framework | Multi-Turn | Simulated Users | Tool Verification | Model Comparison | Cost Tracking | Open Source | Agent Eval Design | Active Dev |
|---|---|---|---|---|---|---|---|---|
| **Promptfoo** | Yes (scripted) | No (custom only) | Yes (assertions) | Excellent | No | Yes (MIT) | Adapted, not native | Very active |
| **Braintrust** | Yes (traces) | No | Yes (traces) | Good | Excellent | No | Adapted | Very active |
| **Langfuse** | Yes (traces) | No | Via traces | Limited | Excellent | Yes (MIT) | Observability focus | Very active |
| **inspect_ai** | Excellent (solvers) | Architecturally easy | Built-in | Good | No | Yes (MIT) | Purpose-built | Very active |
| **Harbor** | Container-based | No | Container-level | Infrastructure | No | Yes | Coding agents | Active |
| **LangWatch/Scenario** | Excellent (native) | **Yes (native)** | Via judge | Not built-in | No | Yes (MIT) | Purpose-built | Active |
| **Maxim AI** | Excellent | Yes (native) | Yes | Yes | Yes | No | Purpose-built | Active |

---

## 3. The Simulated User Problem

### Current State of the Art

Evaluating conversational agents like TutorClaw requires a **second LLM playing the user role**. This is the "simulated user" pattern, and it is both essential and deeply problematic.

**The pattern works like this**:
1. Define a user persona and scenario (e.g., "Fatima, a motivated beginner, asks about Python loops")
2. A "user simulator" LLM generates the first user message based on the persona
3. The agent under test (TutorClaw) responds
4. The user simulator generates the next user message based on the agent's response and the persona
5. This continues for N turns or until a completion criterion is met
6. A grader (code-based, model-based, or human) scores the full conversation

**Frameworks with native support**: LangWatch/Scenario (first-class `UserSimulatorAgent`), Maxim AI (commercial, full persona modeling)

**Frameworks requiring custom work**: inspect_ai (natural to build as custom solver, ~20-50 lines Python), Promptfoo (possible via custom provider, more work), Braintrust/Langfuse (no simulation, only scoring)

**Anthropic's guidance**: Their evals article explicitly states that "effective evals for conversational agents usually require a second LLM to simulate the user" and references tau-bench as the canonical example. They recommend combining graders: LLM rubrics assess communication quality while code-based graders verify state outcomes.

### Quality of Simulation

**Critical research finding**: The January 2026 paper "Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations" (Seshadri et al.) demonstrates that:

1. **Lack of robustness**: Agent success rates vary up to **9 percentage points** depending on which LLM is used as the user simulator
2. **Systematic miscalibration**: Simulated users **underestimate** agent performance on hard tasks and **overestimate** on moderate ones
3. **Demographic bias**: AAVE speakers experience worse success rates than SAE speakers, with disparities compounding with age
4. **Behavioral artifacts**: Simulated users exhibit "increased question-asking and politeness" compared to real users

**Implications for TutorClaw**:
- We cannot treat simulated student scores as ground truth for how TutorClaw performs with real students
- Simulated evals are useful for **regression detection** and **model comparison** (relative performance), not absolute quality measurement
- Human calibration (Anthropic's Step 6: read transcripts regularly) is non-negotiable
- The choice of user simulator model matters — we should test with multiple simulator models and look for consistency

### The Persona Problem

Different student types need different simulated behaviors:

| Persona | Behavior Pattern | Simulation Challenge |
|---|---|---|
| **Fatima** (motivated beginner) | Eager questions, tries before asking, follows instructions | Easiest to simulate — default LLM politeness maps well |
| **Raj** (busy professional) | Terse, wants direct answers, gets frustrated with Socratic questioning | Hard — LLMs default to patience and politeness |
| **Marcus** (career changer) | Brings wrong mental models from previous domain, needs explicit correction | Very hard — requires the simulator to make specific wrong assumptions |

**Approaches to persona modeling**:

1. **System prompt personas**: Define each persona in a system prompt for the user simulator. Cheapest, least reliable. LLMs struggle to maintain consistent "wrong knowledge" or frustration.

2. **Scripted + simulated hybrid** (recommended): Pre-script the key persona-defining turns (Marcus's wrong mental model, Raj's terse frustration) and let the simulator fill in the gaps. LangWatch/Scenario supports this via its scripted+automated mode.

3. **Persona-calibrated with human reference**: Record real conversations with each persona type, use them as few-shot examples for the simulator. Most expensive but most realistic.

4. **Diverse simulator ensemble**: Run the same scenario with different simulator models (GPT-4, Claude, Gemini as students) — if TutorClaw performs well across all three, it's likely robust to user variation.

---

## 4. Model Comparison

### The Core Question

Can we run: **Same agent architecture + same eval suite + swap model A for model B -> get comparison scores**?

### Framework Capabilities

**Trivial model swap (built-in)**:
- **Promptfoo**: Best-in-class. Add a provider line to YAML, get side-by-side. `prompt x model x test case` matrix is the core abstraction.
- **inspect_ai**: Change the `model` parameter on task invocation. One-line change, then compare run results.

**Requires orchestration but supported**:
- **Braintrust**: Run experiments with different model configs, compare in dashboard. Requires running the eval twice with different configs.
- **LangWatch/Scenario**: Run scenarios with different agent configs, compare results externally. No built-in comparison view.

**Limited**:
- **Langfuse**: Compare traces with different tags, but no experiment comparison workflow.

### Cost Tracking Per Model During Eval

| Framework | Cost Per Run | Cost Breakdown by Model | Aggregate Cost Analytics |
|---|---|---|---|
| Braintrust | Yes | Yes | Yes (dashboard) |
| Langfuse | Yes | Yes (per-trace) | Yes (Daily Metrics API) |
| Promptfoo | No native | No | No |
| inspect_ai | No native | No | No |
| LangWatch | No native | No | No |

**Gap**: The two frameworks best for agent eval (inspect_ai, LangWatch) lack cost tracking. The two with best cost tracking (Braintrust, Langfuse) are primarily observability tools. This suggests a **layered approach**: use an eval framework for running evals + an observability tool for cost/performance tracking.

---

## 5. Mapping to Anthropic's Abstractions

### Task -> TutorClaw Eval Task

A "task" is a specific teaching scenario with defined inputs and success criteria.

**Example**: "Student asks about Python for loops. Agent should: (1) not give the answer directly, (2) use Socratic method, (3) lead student to understanding within 8 turns, (4) correctly adapt if student is confused."

**Dataset fields**:
- `student_persona`: Which persona the simulated student embodies
- `topic`: The concept being taught (maps to a lesson/skill)
- `student_starting_knowledge`: What the student already knows
- `expected_teaching_approach`: Socratic, direct instruction, scaffolded, etc.
- `success_criteria`: What "good teaching" looks like for this specific scenario

### Trial -> One Complete Teaching Session

A trial is one attempt at the task — a full multi-turn conversation from first student message to resolution. Multiple trials per task are essential because:
- Model outputs are non-deterministic
- Different simulated student responses create different conversation paths
- pass^k matters more than pass@k for teaching (we need consistent quality, not occasional brilliance)

**Recommended**: Run 5-10 trials per task to compute reliable pass^k metrics.

### Grader -> Teaching Quality Scorer

**Code-based graders** (fast, cheap, deterministic):
- Turn count: Did the agent resolve the question within N turns?
- Tool call verification: Did TutorClaw fetch the right lesson content?
- Forbidden patterns: Did the agent give away the answer directly? (regex/string matching)
- Session state: Is the student's knowledge state updated correctly?

**Model-based graders** (nuanced, expensive):
- Socratic quality: Did the agent ask good leading questions? (rubric scoring)
- Concept accuracy: Were the agent's explanations factually correct?
- Adaptation: Did the agent adjust its approach when the student was confused?
- Encouragement: Was the tone appropriate and motivating?
- Pedagogy: Did the teaching follow sound pedagogical principles?

**Human graders** (gold standard, slow):
- Calibration sessions: Domain experts score 50-100 conversations to calibrate model graders
- Spot checks: Weekly sampling of 10-20 transcripts to detect grader drift
- Novel scenarios: First evaluation of new teaching domains where no rubric exists yet

### Transcript -> Conversation Record

What we capture from each trial:
- Full message history (student + agent turns)
- All tool calls with parameters and results
- Timestamps and latencies per turn
- Token counts per turn (for cost tracking)
- Agent's internal reasoning (if available via chain-of-thought)
- Student persona and scenario metadata

### Outcome -> Final Teaching State

- Did the student reach understanding? (assessed by grader)
- How many turns did it take?
- Did the agent use appropriate teaching strategies?
- Were there any harmful or incorrect statements?
- Total cost of the session

### Eval Suite -> Organized Test Collections

**By teaching domain**: Python loops, data types, recursion, agent architecture
**By difficulty**: Basic concept introduction, misconception correction, advanced application
**By persona**: Beginner, professional, career-changer
**By strategy**: Socratic, direct instruction, scaffolded, exercise-based

### pass@k vs pass^k -> pass^k Matters More

For teaching quality, **pass^k is essential**. A tutor that gives brilliant explanations 60% of the time and confused nonsense 40% of the time is worse than one that gives consistently good (not brilliant) explanations 95% of the time. Students need reliable quality.

**Recommended**: Track both, but optimize for pass^5 at minimum. A teaching agent needs to pass the same teaching task consistently across 5 trials to be considered reliable.

---

## 6. Concrete Example: TutorClaw Eval

### Full Walkthrough

**Task definition**:
```yaml
task: teach_python_for_loop
persona: fatima_motivated_beginner
topic: python_for_loops
starting_knowledge: "Knows variables and if/else, no loops yet"
max_turns: 10
success_criteria:
  - student_reaches_understanding: true
  - no_direct_answer_given: true
  - socratic_questions_used: >= 2
  - explanation_accuracy: >= 0.9
```

**Turn 1 — Simulated Student (Fatima)**:
> "I understand if/else but I keep hearing about 'loops' in Python. What are they and why would I need one?"

**Turn 2 — TutorClaw (Model A: Claude Sonnet)**:
> "Great question! Let me ask you this — imagine you want to print 'Hello' 100 times. How would you do it with what you know now?"

**Turn 3 — Simulated Student**:
> "I guess I'd write print('Hello') 100 times? That sounds terrible."

**Turn 4 — TutorClaw**:
> "Exactly! That's the problem loops solve. What if I told you there's a way to say 'do this thing N times' in one line?"

*(continues for 4-6 more turns until the student demonstrates understanding)*

**Grading (all three types applied)**:

| Grader Type | What It Checks | Score |
|---|---|---|
| Code-based | Turn count <= 10? | PASS (8 turns) |
| Code-based | Direct answer regex? | PASS (no `for x in range()` in first 4 turns) |
| Code-based | Tool calls correct? | PASS (fetched python_for_loops lesson) |
| Model-based | Socratic quality (rubric 1-5) | 4/5 |
| Model-based | Concept accuracy | 5/5 |
| Model-based | Adaptation to confusion | 4/5 |
| Model-based | Tone/encouragement | 5/5 |

**Repeat with Model B (GPT-4o)**:

Same task, same simulated student, same graders. Compare aggregate scores across 5 trials each.

**Result**:
| Metric | Claude Sonnet (5 trials) | GPT-4o (5 trials) |
|---|---|---|
| pass^5 | 0.80 | 0.60 |
| Avg Socratic quality | 4.2 | 3.6 |
| Avg turns to resolution | 7.4 | 9.2 |
| Cost per session | $0.08 | $0.12 |

### Which Framework Handles This With Least Custom Work?

**Tier 1 — Least custom work**:

**LangWatch/Scenario** handles Steps 1-5 natively:
- `AgentAdapter` wraps TutorClaw (5 lines)
- `UserSimulatorAgent` plays Fatima (configure persona in scenario description)
- `JudgeAgent` does real-time evaluation (define criteria)
- Multi-turn simulation runs automatically
- BUT: Model comparison requires running scenarios twice and comparing externally
- BUT: No cost tracking

**Tier 2 — Moderate custom work**:

**inspect_ai** handles the eval pipeline well:
- Dataset defines tasks
- Custom solver wraps TutorClaw + simulated student loop (~30 lines Python)
- Scorers grade transcripts (code-based + model-based)
- Sandboxed execution if agent runs code
- Model swap is one parameter change
- BUT: Simulated user requires custom solver (natural but not pre-built)
- BUT: No cost tracking

**Tier 3 — More custom work**:

**Promptfoo** for model comparison + custom simulation:
- YAML config for model matrix is unmatched
- Multi-turn via `_conversation` variable
- BUT: Each turn must be explicitly scripted or requires custom provider for simulation
- Best combined with another tool for the simulation layer

---

## 7. Recommendation

### Primary Recommendation: inspect_ai + LangWatch/Scenario + Langfuse

A three-layer stack that uses each tool for what it does best:

| Layer | Tool | Role |
|---|---|---|
| **Simulation** | LangWatch/Scenario | Generate multi-turn conversations with simulated students |
| **Evaluation** | inspect_ai | Run eval pipelines, grade transcripts, track results |
| **Observability** | Langfuse | Cost tracking, production monitoring, trace storage |

**Why this combination**:

1. **LangWatch/Scenario** has the best simulated user support and is MIT-licensed. Use it to generate conversations with different student personas.

2. **inspect_ai** has the most principled eval architecture (solver/tool/scorer maps directly to Anthropic's abstractions) and is purpose-built for agent evaluation. Use it as the evaluation harness.

3. **Langfuse** fills the cost tracking and production monitoring gap. Self-hostable, MIT-licensed, captures traces for later analysis.

### Alternative: inspect_ai Only (Simpler, More Custom Work)

If the three-tool stack feels too complex, **inspect_ai alone** can handle everything with custom code:
- Custom solver for simulated user (~30 lines)
- Built-in scorers + custom scorers for teaching quality
- Model comparison via parameter swap
- Sandboxing for code-executing agents
- Missing: cost tracking (add Langfuse later if needed)

This is the "start simple, add layers as needed" approach.

### Key Capabilities to Prioritize

1. **Simulated user quality** — The make-or-break capability. Without realistic student simulation, agent evals are meaningless.
2. **Multi-turn transcript capture** — Every turn, tool call, and reasoning step must be recorded for grading.
3. **Composable graders** — Code-based for deterministic checks + model-based for pedagogical quality, applied to the same transcript.
4. **Model comparison workflow** — Swap model, rerun, compare. Must be low-friction.
5. **Human calibration loop** — Regular transcript review to calibrate automated graders against human judgment.

### What NOT to Build

- **Custom eval harness** — inspect_ai already does this well
- **Custom conversation simulation engine** — LangWatch/Scenario does this
- **Custom observability/tracing** — Langfuse/Braintrust do this
- **Custom model comparison UI** — Promptfoo or inspect_ai do this

### Build Only the "Thin Layer"

Per the research brief, the thin layer we build on top is:
1. **TutorClaw AgentAdapter** — wraps TutorClaw for evaluation (5-10 lines per framework)
2. **Teaching quality rubrics** — domain-specific grading criteria for Socratic method, concept accuracy, adaptation
3. **Student persona definitions** — persona descriptions + scripted key turns for each student type
4. **Eval datasets** — specific teaching scenarios with success criteria
5. **Orchestration scripts** — run eval suite, compare models, generate reports

---

## 8. Open Questions

1. **Simulated user model choice**: Which model should play the student? Using Claude to evaluate Claude creates circularity. Using GPT-4 to simulate students for Claude-based TutorClaw adds cost but removes bias. Should we use an ensemble?

2. **Grader calibration timeline**: How many human-graded transcripts do we need before we can trust model-based graders for teaching quality? Anthropic suggests starting with 50-100.

3. **pass^k threshold**: What pass^k value constitutes "production ready" for TutorClaw? pass^3? pass^5? This is a product decision, not a technical one.

4. **Cost budget**: Running 5 trials x 10 turns x model-based grading per task gets expensive quickly. What's the acceptable cost per eval run? This determines how many tasks we can include in the regression suite.

5. **Integration with existing eval infrastructure**: The project already has `evals/flashcards/` with deterministic + LLM judge graders. Should agent evals use the same grader patterns or adopt inspect_ai's scorer architecture? Migration path matters.

6. **Persona validation**: How do we validate that simulated Fatima behaves like real Fatima? Do we need a human study (expensive, slow) or can we bootstrap from recorded conversations?

7. **LangWatch/Scenario maturity**: It's newer and less battle-tested than inspect_ai or Promptfoo. Is the team comfortable adopting a newer tool, or should we build the simulated user layer ourselves within inspect_ai?

8. **Promptfoo for model comparison only?**: Promptfoo's model comparison is unmatched. Worth using it solely for the model comparison workflow, even if inspect_ai handles the rest?
