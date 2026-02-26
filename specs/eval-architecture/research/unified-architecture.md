# Unified Eval Architecture

## 1. Cross-Domain Synthesis

### Shared Foundations

All three domains share these core capabilities:

1. **Dataset-driven evaluation**: Every domain follows the pattern: dataset of cases -> execute subject -> grade output -> aggregate scores. The dataset schemas differ (single input for skills, multi-turn scenarios for agents, session-chained scenarios for AI Employee) but the runner pattern is identical.

2. **Dual grading architecture**: All three domains require deterministic code-based checks (format validation, constraint enforcement, forbidden patterns) AND model-based quality assessment (LLM-as-judge with rubrics). The ratio shifts — skills lean heavily deterministic (24 hard checks), agents lean model-based (pedagogical quality), AI Employee evals are almost entirely rubric-based — but the two-layer grading pattern is universal.

3. **Model comparison**: All three domains need "same task, swap model, compare scores." This is the ranking table pattern that runs across every scope level.

4. **Baseline regression detection**: All three domains need "run eval, save scores, run again later, diff." The flashcard harness already implements this with `baselines/baseline-v1.json`. The pattern generalizes directly.

5. **Skills-as-Graders**: The Skills researcher's proposal to package grading rubrics as SKILL.md files is endorsed by the other two domains implicitly — both the Agent and AI Employee researchers identify "grading rubric design" as the primary custom work. Packaging rubrics as portable, versioned Skills makes them reusable across all three domains.

### Resolved Contradictions

**Contradiction 1: Framework recommendations diverge**

| Domain | Recommended Stack |
|---|---|
| Skills | Custom harness + Promptfoo (for model comparison) |
| Agent | inspect_ai + LangWatch/Scenario + Langfuse |
| AI Employee | Promptfoo + Braintrust |

**Resolution**: These recommendations optimize for different scopes and are actually complementary, not conflicting:

- **Promptfoo** appears in 2/3 recommendations because it is genuinely best-in-class for model comparison (the ranking table). It is a universal comparison layer, not a domain-specific tool.
- **inspect_ai** appears only for Agent eval because it is purpose-built for multi-turn, tool-using agent systems with sandboxed execution. Skills don't need this complexity. AI Employee evals don't need sandboxing.
- **LangWatch/Scenario** appears for Agent eval as the simulated user layer. This capability is also needed for AI Employee eval (simulated students across sessions).
- **Braintrust** appears for AI Employee eval because of its production-to-eval bridge loop. This is an operational workflow concern, not an eval runner concern.
- **Langfuse** appears for Agent eval as observability/cost tracking. Open-source alternative to Braintrust for the monitoring layer.
- **The custom harness** (`evals/flashcards/`) is recommended to keep for Skills because it already works and has exact-fit features (pass^k, 24-check deterministic scoring) that would require recreation in any framework.

The contradiction dissolves when you recognize these tools operate at different layers (see Section 2).

**Contradiction 2: Custom harness vs. inspect_ai**

The Skills researcher says "keep the custom harness." The Agent researcher says "use inspect_ai." Are these in conflict?

**Resolution**: No. They serve different scopes:
- The custom harness is a single-turn eval runner optimized for SKILL.md evaluation. It does one thing well.
- inspect_ai is a multi-turn agent eval framework. It can do single-turn (it's a superset), but the overhead isn't justified when the custom harness already exists and works.

**Decision**: Keep the custom harness for Skills eval. Use inspect_ai (or LangWatch/Scenario) for Agent and AI Employee eval. Promptfoo sits alongside both as the model comparison layer. These are parallel tracks, not competing choices.

**Contradiction 3: Braintrust vs. Langfuse for observability**

Agent researcher recommends Langfuse (open-source, self-hostable). AI Employee researcher recommends Braintrust (best production bridge loop).

**Resolution**: This is a build-vs-buy decision, not a technical incompatibility:
- Langfuse: MIT licensed, self-hostable, cheaper, but the production-to-eval pipeline requires more manual setup.
- Braintrust: Commercial ($249/mo Pro), strongest one-click production-to-eval dataset conversion, but vendor lock-in risk.

**Recommendation**: Start with Langfuse (open-source, aligns with project values). The production-to-eval bridge can be built as a thin script on Langfuse's annotation API. Migrate to Braintrust only if the manual bridge proves too friction-heavy at scale.

### Domain-Specific Requirements

| Requirement | Skills | Agent | AI Employee |
|---|---|---|---|
| **Turn structure** | Single-turn | Multi-turn (5-20 turns) | Multi-turn + multi-session |
| **Simulated users** | Not needed | Required (student personas) | Required (persistent student personas) |
| **Tool verification** | Not needed (prompt in/text out) | Required (tool calls must be correct) | Required + channel verification |
| **Session state** | Stateless | Stateful within session | Stateful across sessions |
| **Cost tracking** | Nice to have | Important (multi-turn = expensive) | Critical (longitudinal = very expensive) |
| **Sandboxing** | Not needed | Needed if agent executes code | Needed if agent executes code |
| **Production monitoring** | Not needed (offline only) | Important (deployed TutorClaw) | Critical (production AI Employee) |
| **Grading emphasis** | 70% deterministic / 30% LLM | 40% deterministic / 60% LLM | 20% deterministic / 80% LLM |
| **Key metric** | pass@k, model comparison | pass^k (consistency) | Longitudinal improvement |
| **Eval frequency** | Per skill change (CI) | Per agent change + weekly regression | Continuous + periodic deep eval |

### The Nesting Verdict

**Does Skills -> Agent -> AI Employee compose? Yes, with caveats.**

The nesting is real but not strict containment:

```
Skills Eval ⊂ Agent Eval ⊂ AI Employee Eval
   (mostly)      (mostly)

Skills Eval: single-turn prompt evaluation
  + Multi-turn orchestration = Agent Eval
  + Personalization + longitudinal tracking = AI Employee Eval
```

**Where nesting holds cleanly**:
- An Agent Eval CAN invoke Skills Eval as a component (test each skill in isolation, then test the agent using those skills together).
- An AI Employee Eval CAN invoke Agent Eval as a component (test the agent's teaching ability, then test whether it improves over time for a specific learner).
- Grading rubrics compose: Skills-level rubrics (format, accuracy) are a subset of Agent-level rubrics (format, accuracy + pedagogy + tool use), which are a subset of AI Employee rubrics (all of the above + personalization + longitudinal improvement).

**Where nesting breaks down**:
- The eval RUNNERS don't nest. The custom harness (skills) can't orchestrate multi-turn evaluation. inspect_ai (agents) doesn't natively chain sessions. Each scope level needs its own orchestration, even if they share grading components.
- Datasets don't nest. Skills datasets are input/output pairs. Agent datasets are scenario descriptions. AI Employee datasets are multi-session scenario chains. They share the learner profile schema but not the case structure.

**Practical implication**: Build shared components (graders, profiles, Promptfoo comparison configs) that are consumed by scope-specific runners. Don't try to build one runner that handles all three scopes.

---

## 2. Recommended Minimal Stack

### The Tools

The three researchers collectively reference 6+ tools. Here is the consolidated minimal stack:

| Tool | Role | Domains | License | Why This One |
|---|---|---|---|---|
| **Custom harness** (`run-eval.sh`) | Skills eval runner | Skills | Ours | Already built, exact fit, full control |
| **Promptfoo** | Model comparison layer | All three | MIT | Best-in-class model matrix, YAML config, CI/CD |
| **inspect_ai** | Agent/AI Employee eval runner | Agent, AI Employee | MIT | Purpose-built for multi-turn agent eval, solver/scorer architecture |
| **LangWatch/Scenario** | Simulated user generation | Agent, AI Employee | MIT | Only framework with native simulated users, multi-language |
| **Langfuse** | Observability + cost tracking | Agent, AI Employee | MIT | Open-source, self-hostable, trace storage, cost per run |

**Total: 5 tools** (down from 6+ across the three reports). One is already built.

### Why These (And Not Those)

**Dropped: Braintrust**
- The AI Employee researcher recommends it for the production-to-eval bridge loop. However, Langfuse covers 80% of this functionality (trace capture, annotation, dataset creation) and is open-source. The remaining 20% (one-click trace-to-dataset) can be built as a thin script (~50 lines). Dropping Braintrust eliminates a $249/mo commercial dependency and vendor lock-in risk.

**Dropped: OpenAI Evals**
- OpenAI-centric, Python-only, pivoting to hosted API. No unique capability not covered by Promptfoo or inspect_ai.

**Kept: Both custom harness AND inspect_ai**
- The Skills researcher makes a convincing case that the existing harness has features (pass^k, 24-check deterministic scoring, exact SKILL.md integration) that would need recreation. inspect_ai is overkill for single-turn skills but essential for multi-turn agents. Maintaining both is lower effort than migrating and recreating.

**Kept: Both Promptfoo AND inspect_ai**
- Promptfoo excels at model comparison (provider matrix is its core abstraction). inspect_ai excels at agent evaluation (solver/scorer pipeline). They serve different purposes. Promptfoo handles "which model is best for this skill/task?" while inspect_ai handles "does this agent system work end-to-end?"

**LangWatch/Scenario as simulation layer, not eval runner**
- Use Scenario specifically for generating simulated multi-turn conversations. Feed those conversations into inspect_ai for scoring. This avoids using Scenario's less mature evaluation features while leveraging its best-in-class simulated user capability.

### Architecture Layers

```
Layer 4: Reporting & Comparison
  └── Promptfoo (ranking tables, model matrix, CI reports)

Layer 3: Observability & Production
  └── Langfuse (traces, cost tracking, production monitoring)

Layer 2: Eval Runners (domain-specific)
  ├── Custom harness (Skills: single-turn, SKILL.md native)
  └── inspect_ai (Agent + AI Employee: multi-turn, tool use, sandboxing)

Layer 1: Simulation & Generation
  └── LangWatch/Scenario (simulated students, multi-turn conversation generation)

Layer 0: Shared Components
  ├── Grader Skills (SKILL.md-packaged rubrics, reusable across runners)
  ├── Learner Profiles (JSON schemas, consumed by simulation + personalization)
  ├── Datasets (per-domain case definitions)
  └── Deterministic Graders (JS modules, shared across harness + inspect_ai)
```

---

## 3. Build-vs-Adopt Matrix

| # | Component | Recommendation | Tool/Approach | Domain(s) | Effort |
|---|---|---|---|---|---|
| 1 | **Eval runner (single-turn)** | Keep | Custom harness (`run-eval.sh`) | Skills | None (exists) |
| 2 | **Eval runner (multi-turn)** | Adopt | inspect_ai (solver/scorer pipeline) | Agent, AI Employee | Medium (learn framework, write solvers) |
| 3 | **Simulation engine** | Adopt | LangWatch/Scenario (`UserSimulatorAgent`) | Agent, AI Employee | Low-Medium (integrate with inspect_ai) |
| 4 | **Deterministic graders** | Keep | Custom JS (`deterministic.js` pattern) | All three | None (exists, extend per domain) |
| 5 | **LLM graders** | Extend | Grader Skills (SKILL.md rubrics) | All three | Medium (extract existing rubrics into SKILL.md, build loader) |
| 6 | **Model comparison** | Adopt | Promptfoo (provider matrix, YAML config) | All three | Low (YAML configuration) |
| 7 | **Cost tracking** | Adopt | Langfuse (per-trace token/cost tracking) | Agent, AI Employee | Low (SDK integration) |
| 8 | **Result storage** | Extend | Langfuse (traces) + filesystem (baselines/) | All three | Low (existing baseline pattern + Langfuse traces) |
| 9 | **Baseline comparison** | Keep | Custom (`baselines/baseline-v1.json` diff pattern) | All three | None (exists, generalize to new domains) |
| 10 | **Production monitoring** | Adopt | Langfuse (online scoring, trace annotation) | Agent, AI Employee | Medium (instrument production agents) |
| 11 | **Ranking/reporting** | Adopt + Extend | Promptfoo web UI + thin custom reporting script | All three | Low-Medium (Promptfoo native + script for cross-domain rollup) |
| 12 | **Student personas** | Build | JSON persona definitions + LangWatch/Scenario config | Agent, AI Employee | Medium (content creation, behavioral descriptions) |
| 13 | **Teaching rubrics** | Build | Grader Skill SKILL.md files (LLM judge prompts) | Agent, AI Employee | Medium-High (pedagogical expertise needed) |
| 14 | **Session chaining** | Build | Thin wrapper script (~200-500 lines) on inspect_ai | AI Employee | Low-Medium (script + state serialization) |

**Summary**: 4 Keep, 5 Adopt, 2 Extend, 3 Build. The "Build" items are all content/rubric work, not infrastructure.

---

## 4. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROMPTFOO (Model Comparison)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │
│  │ Claude Opus  │  │Claude Sonnet│  │  GPT-4o     │  ... (provider matrix) │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                        │
│         └────────────────┼────────────────┘                                │
│                    Ranking Tables                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                              ▲ scores
                              │
┌─────────────────────────────┴───────────────────────────────────────────────┐
│                          EVAL RUNNERS (Domain-Specific)                      │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────────────────────┐   │
│  │  CUSTOM HARNESS      │    │  INSPECT_AI                              │   │
│  │  (Skills Eval)       │    │  (Agent + AI Employee Eval)              │   │
│  │                      │    │                                          │   │
│  │  run-eval.sh         │    │  Dataset -> Solver -> Scorer             │   │
│  │  Single-turn loop    │    │  Multi-turn loop with tool use           │   │
│  │  pass@k, pass^k      │    │  Sandboxed execution (Docker)           │   │
│  │  24+ deterministic    │    │  Session chaining wrapper (AI Employee) │   │
│  │  checks              │    │                                          │   │
│  └──────────┬───────────┘    └──────────────────┬───────────────────────┘   │
│             │                                    │                           │
└─────────────┼────────────────────────────────────┼───────────────────────────┘
              │                                    │
              ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SHARED GRADING LAYER                                │
│                                                                              │
│  ┌───────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  Deterministic     │  │  Grader Skills    │  │  Calibration           │  │
│  │  Graders (JS)      │  │  (SKILL.md)       │  │  Baselines             │  │
│  │                    │  │                    │  │                        │  │
│  │  format checks     │  │  teaching-quality  │  │  golden outputs        │  │
│  │  constraint gates  │  │  personalization   │  │  human-scored refs     │  │
│  │  forbidden patterns│  │  content-fidelity  │  │  baseline-v1.json      │  │
│  │  word count bounds │  │  socratic-method   │  │  regression diffs      │  │
│  └───────────────────┘  └───────────────────┘  └────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
              ▲                                    ▲
              │                                    │
┌─────────────┼────────────────────────────────────┼───────────────────────────┐
│             │      SIMULATION LAYER              │                           │
│             │                                    │                           │
│   ┌─────────────────────────┐    ┌──────────────────────────────────┐       │
│   │  Test Datasets          │    │  LangWatch/Scenario              │       │
│   │                         │    │                                  │       │
│   │  skills: cases.json     │    │  UserSimulatorAgent              │       │
│   │  agent: scenarios.yaml  │    │  Student personas (Fatima, Raj)  │       │
│   │  employee: chains.yaml  │    │  Scripted + simulated hybrid     │       │
│   └─────────────────────────┘    │  JudgeAgent (real-time stopping) │       │
│                                  └──────────────────────────────────┘       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
              ▲                                    ▲
              │                                    │
┌─────────────┼────────────────────────────────────┼───────────────────────────┐
│             │      SHARED FOUNDATIONS            │                           │
│   ┌─────────────────────────┐    ┌──────────────────────────────────┐       │
│   │  Learner Profiles       │    │  Langfuse (Observability)        │       │
│   │  (JSON Schema)          │    │                                  │       │
│   │                         │    │  Trace capture + storage         │       │
│   │  fatima.json            │    │  Cost per run/model              │       │
│   │  raj.json               │    │  Production monitoring           │       │
│   │  marcus.json            │    │  Annotation -> eval dataset      │       │
│   │                         │    │  (bridge loop)                   │       │
│   └─────────────────────────┘    └──────────────────────────────────┘       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Data flow**:
1. Datasets + Learner Profiles define WHAT to test
2. LangWatch/Scenario generates multi-turn conversations (Agent, AI Employee)
3. Eval Runners orchestrate execution and invoke graders
4. Shared Grading Layer scores outputs (deterministic + LLM rubrics)
5. Langfuse captures traces, costs, and production data
6. Promptfoo presents model comparison and ranking tables
7. Bridge loop: Langfuse annotations -> new dataset cases -> re-eval

---

## 5. Connection Points

### Learner Profiles as Shared Schema

Learner profiles (Fatima, Raj, Marcus) serve TWO purposes across the architecture:

**1. Personalization target** (consumed by content personalization skills):
```json
{
  "id": "fatima",
  "name": "Fatima Al-Rahman",
  "experience_level": "beginner",
  "prior_knowledge": ["python_basics", "if_else"],
  "learning_style": "visual",
  "language_level": "intermediate_english",
  "domain_background": "data_science",
  "goals": ["build_ai_agents", "automate_workflows"]
}
```

**2. Simulator persona** (consumed by LangWatch/Scenario for simulated students):
```json
{
  "id": "fatima",
  "...base profile fields above...",
  "simulation_config": {
    "behavior_pattern": "eager, asks follow-ups, tries before asking",
    "frustration_threshold": "high (patient)",
    "common_misconceptions": ["loops are only for numbers", "functions must return values"],
    "scripted_turns": {
      "turn_3_if_confused": "I think I understand but can you show me an example?",
      "turn_5_wrong_mental_model": "So a for loop is like an if statement that repeats?"
    },
    "termination_signal": "I think I get it now, let me try..."
  }
}
```

**Recommendation**: Use a SINGLE JSON schema with an optional `simulation_config` extension. The base profile is shared across personalization and simulation. The simulation config adds behavioral specifications only needed by the simulator. This avoids schema drift between the two use cases.

**Schema location**: `evals/shared/schemas/learner-profile.schema.json`
**Profile instances**: `evals/shared/profiles/{persona-name}.json`

### AgentFactory Pedagogy -> Grader Specifications

The book's teaching methodology defines explicit success criteria that map directly to grader rubrics:

| Pedagogical Framework | Grading Dimension | Grader Type |
|---|---|---|
| **4-Layer Teaching Method** | Did the lesson follow the appropriate layer (Manual -> Collaboration -> Intelligence -> Spec-Driven)? | LLM rubric: check lesson progression against layer criteria |
| **Constitutional Framework** | Does the AI agent's behavior conform to its constitution? | Deterministic: check output against constitutional constraints; LLM rubric: assess spirit vs letter |
| **Persona + Questions + Principles** | Does the agent maintain its persona? Ask appropriate questions? Follow principles? | LLM rubric: persona consistency scoring; Deterministic: question count, principle reference check |
| **Socratic Method** (TutorClaw) | Does the tutor ask leading questions before giving answers? | Deterministic: regex for direct answers in early turns; LLM rubric: question quality scoring |
| **Scaffolding Progression** | Does difficulty increase appropriately across the session? | LLM rubric: difficulty progression analysis; Deterministic: concept prerequisite ordering |
| **Content WHAT vs Interaction HOW** (from AI Employee research) | Is WHAT was taught adapted? Is HOW it was delivered adapted? | Two separate LLM rubrics sharing the same learner profile input |

**Mapping to Grader Skills**:

Each row above becomes a Grader Skill (SKILL.md):
- `constitutional-compliance-grader/SKILL.md` — Checks agent behavior against constitutional constraints
- `teaching-quality-grader/SKILL.md` — Scores Socratic method, scaffolding, adaptation
- `personalization-content-grader/SKILL.md` — Scores content adaptation (the WHAT)
- `personalization-interaction-grader/SKILL.md` — Scores delivery adaptation (the HOW)
- `persona-consistency-grader/SKILL.md` — Scores persona maintenance across turns

These grader skills are the "thin layer" the research brief asks about. They encode pedagogical expertise as portable, versioned, testable evaluation logic.

### Migration from Existing Infrastructure

The project has `evals/flashcards/` with:
- `run-eval.sh` — Shell-based eval runner
- `graders/deterministic.js` — 24+ hard checks
- `graders/llm-judge.js` — LLM-as-judge with inline rubric
- `graders/aggregate.js` — pass@k, pass^k aggregation
- `datasets/cases.json` — 5 test cases
- `baselines/baseline-v1.json` — Regression baseline

**Migration path** (coexistence, not replacement):

**Phase 1: Extract, don't migrate**
- Extract `llm-judge.js:buildPrompt()` rubric into `flashcard-quality-grader/SKILL.md`
- Extract `evals/assessment-architect/rubric-grader.md` into `assessment-quality-grader/SKILL.md`
- The custom harness continues to work exactly as-is. The grader skills are loaded by a thin adapter.
- Result: Existing infrastructure untouched, grading logic now portable.

**Phase 2: Add Promptfoo alongside**
- Create `promptfoo.yaml` configs that reference the same datasets and grader skills
- Use Promptfoo specifically for model comparison (which model produces best flashcards?)
- The custom harness handles regression testing; Promptfoo handles model selection
- Result: Two tools, complementary purposes, shared grading logic.

**Phase 3: Add inspect_ai for Agent eval (new track)**
- Build TutorClaw eval as a NEW eval domain (`evals/tutorclaw/`)
- Uses inspect_ai as runner, LangWatch/Scenario for simulation
- Shares grader skill patterns established in Phase 1
- Does NOT replace flashcard eval — coexists as a separate domain
- Result: Skills eval and Agent eval running in parallel, sharing grading architecture.

**Phase 4: Add session chaining for AI Employee eval**
- Build thin wrapper on inspect_ai for multi-session evaluation
- Shares learner profiles, grader skills, and Langfuse observability with Agent eval
- Result: Full three-domain eval architecture, each with appropriate runner, sharing grading components.

---

## 6. Three Immediate Deliverables

### Deliverable 1: Sir Zia's Simulator (Model x Student -> Ranking Table)

**What it is**: Run the same teaching scenario across multiple models with simulated student personas. Produce a ranking table showing which model teaches best for each student type.

**Architecture mapping**:
- **Runner**: Promptfoo (model comparison matrix is its core strength)
- **Simulation**: LangWatch/Scenario `UserSimulatorAgent` with persona configs
- **Grading**: Teaching quality grader skill (Socratic method, adaptation, accuracy)
- **Output**: Promptfoo matrix view: Model x Persona -> Teaching Quality Score

**Implementation approach**:
1. Define 3 student personas (Fatima, Raj, Marcus) as LangWatch/Scenario persona configs
2. Define 3 teaching scenarios (intro concept, misconception correction, advanced application)
3. Create `teaching-quality-grader/SKILL.md` with rubric dimensions
4. Configure Promptfoo with 3+ model providers
5. Run: 3 models x 3 personas x 3 scenarios x 3 trials = 81 eval runs
6. Output: Ranking table with pass^3, mean teaching quality, mean cost per session

**Effort**: 2-3 weeks (persona design + rubric design + integration)

### Deliverable 2: TutorClaw Eval

**What it is**: End-to-end evaluation of TutorClaw's teaching ability across multiple scenarios and student types, with regression detection.

**Architecture mapping**:
- **Runner**: inspect_ai (multi-turn solver/scorer pipeline)
- **Simulation**: LangWatch/Scenario for simulated students
- **Grading**: Code-based (turn count, tool call verification, forbidden patterns) + Teaching quality grader skill
- **Observability**: Langfuse for trace capture and cost tracking
- **Output**: pass^5 scores per scenario, regression diffs against baseline

**Implementation approach**:
1. Create `AgentAdapter` wrapping TutorClaw for LangWatch/Scenario (~10 lines)
2. Create inspect_ai custom solver that uses Scenario-generated conversations
3. Implement code-based scorers: turn count, tool calls, forbidden answer patterns
4. Implement model-based scorers: load teaching quality grader skill
5. Define 10 teaching scenarios covering different topics, difficulty levels, and persona types
6. Run 5 trials per scenario, compute pass^5
7. Save baseline, run in CI on agent changes

**Effort**: 3-4 weeks (framework integration + scorer development + dataset creation)

### Deliverable 3: Content Personalization Eval

**What it is**: Evaluate whether the content personalization skill adapts lesson content appropriately for different learner profiles.

**Architecture mapping**:
- **Runner**: Custom harness (single-turn: profile + lesson -> personalized output)
- **Grading**: Deterministic (format, word count, profile references) + Two grader skills (content-WHAT, interaction-HOW)
- **Model comparison**: Promptfoo (which model personalizes best?)
- **Output**: Per-profile scores, model comparison, regression baseline

**Implementation approach**:
1. Create learner profile JSON files (Fatima, Raj, Marcus) using shared schema
2. Create `personalization-content-grader/SKILL.md` (scores content adaptation)
3. Create `personalization-interaction-grader/SKILL.md` (scores delivery adaptation)
4. Define 9 test cases: 3 profiles x 3 lessons
5. Extend `run-eval.sh` pattern for personalization eval
6. Add Promptfoo config for model comparison
7. Run eval, establish baseline

**Effort**: 2 weeks (profile creation + rubric design + harness extension). This is the simplest deliverable because it uses the existing custom harness pattern (single-turn) and the Skills-as-Graders pattern already proven in flashcard eval.

---

## 7. Phased Rollout

### Phase 1: Foundation (Weeks 1-3)

**Goal**: Establish shared components and deliver the simplest end-to-end eval.

**Deliverables**:
1. Learner profile shared schema + 3 profile instances (Fatima, Raj, Marcus)
2. Extract existing flashcard LLM rubric into `flashcard-quality-grader/SKILL.md`
3. Content Personalization Eval (Deliverable 3) — uses existing harness pattern
4. Promptfoo config for flashcard model comparison
5. Grader skill loader for the custom harness

**Why this first**: Lowest risk, uses existing infrastructure, proves Skills-as-Graders pattern, produces immediately useful results (which model personalizes best?).

### Phase 2: Multi-Turn (Weeks 4-7)

**Goal**: Stand up the Agent eval stack and deliver the simulator.

**Deliverables**:
1. inspect_ai integration — custom solver for TutorClaw
2. LangWatch/Scenario integration — simulated student generation
3. Teaching quality grader skill
4. Sir Zia's Simulator (Deliverable 1) — model x persona ranking tables
5. TutorClaw Eval v1 (Deliverable 2) — basic scenarios, pass^5 tracking
6. Langfuse integration for cost tracking

**Why this second**: Builds on Phase 1 grading patterns, adds the multi-turn capability, produces the highest-visibility deliverable (ranking tables).

### Phase 3: Production Loop (Weeks 8-10)

**Goal**: Close the production-to-eval feedback loop.

**Deliverables**:
1. Langfuse production monitoring for TutorClaw
2. Annotation workflow: flag low-quality production sessions
3. Script to convert annotated traces to eval dataset cases
4. CI integration: run eval suite on agent/skill changes
5. Automated regression alerting

**Why this third**: Requires a deployed, evaluated agent (from Phase 2) before production monitoring makes sense.

### Phase 4: Longitudinal (Weeks 11-14)

**Goal**: Add session-chaining for AI Employee longitudinal evaluation.

**Deliverables**:
1. Session-chaining wrapper on inspect_ai (~200-500 lines)
2. Longitudinal metrics: calibration speed, unnecessary scaffolding reduction, prediction accuracy
3. Multi-session test scenarios (3+ sessions per learner)
4. Learner model improvement tracking dashboard

**Why last**: Most novel, most custom, least urgent. Requires all previous phases to be stable. Can be deferred without blocking the other deliverables.

---

## 8. Open Decisions

These require stakeholder input before implementation begins:

### 1. Langfuse vs Braintrust for Observability

**Options**:
- (A) Langfuse: Open-source, self-hostable, MIT license, requires more manual setup for production-to-eval bridge
- (B) Braintrust: Commercial ($249/mo), best one-click production bridge, but vendor lock-in
- (C) Start with Langfuse, add Braintrust later if needed

**Recommendation**: (C) — start lean, avoid early vendor commitment. The production bridge can be a thin script.

### 2. LangWatch/Scenario Maturity Risk

LangWatch/Scenario is newer and less battle-tested than inspect_ai or Promptfoo. **If it proves too immature**, the fallback is building the simulated user as a custom inspect_ai solver (~30-50 lines Python). This is more work but eliminates the dependency. Do we adopt Scenario now or build custom from the start?

**Recommendation**: Adopt Scenario. The risk is low (MIT license, multi-language, simple integration), and the simulated user capability is too valuable to build from scratch. Have the custom solver as a documented fallback.

### 3. Grader Skill Location

Should grader skills live in:
- (A) `.claude/skills/` — alongside operational skills, discoverable by agents
- (B) `evals/{domain}/graders/` — alongside eval infrastructure they serve
- (C) `evals/shared/grader-skills/` — shared graders in a neutral location, domain-specific graders in `evals/{domain}/`

**Recommendation**: (C) — shared graders (teaching quality, personalization) in `evals/shared/grader-skills/`. Domain-specific graders (flashcard format, assessment rubric) in `evals/{domain}/graders/`. This prevents namespace pollution in `.claude/skills/` while keeping graders discoverable within the eval tree.

### 4. Simulated User Model Choice

Which model plays the simulated student?
- (A) Same model family as the agent (Claude simulating students for Claude-based TutorClaw) — cheapest, but potential bias
- (B) Different model (GPT-4o simulating students for Claude-based TutorClaw) — removes self-reinforcement, adds cost
- (C) Ensemble (run with 2-3 different simulator models, look for consistency) — most robust, most expensive

**Recommendation**: (B) for development and regression testing. (C) for model comparison eval runs (where you're already paying for multiple runs). Never (A) for high-stakes evaluation.

### 5. pass^k Threshold for Production Readiness

What pass^k value means "production ready" for TutorClaw?
- pass^3 = 3 consecutive successes (lower bar)
- pass^5 = 5 consecutive successes (higher bar, recommended by Agent researcher)
- pass^10 = very high reliability

**Recommendation**: Start with pass^3 for development, require pass^5 for production deployment. This is a product decision — escalate to Sir Zia.

### 6. Eval Cost Budget

Estimated costs per full eval run:
- Skills eval (5 cases x 3 trials x 2 LLM calls): ~$0.15 with Haiku grader
- Agent eval (10 scenarios x 5 trials x ~10 turns x 2 LLM calls): ~$5-15 depending on models
- AI Employee eval (3 sessions x 10 scenarios x 5 trials): ~$15-45

**Question**: What's the acceptable cost per CI-triggered eval run? This determines dataset size and trial count. A weekly full suite at $50-60 is feasible. Per-commit might need a reduced "smoke test" suite.

### 7. Who Designs the Teaching Quality Rubrics?

The AI Employee researcher correctly identifies that rubric design requires pedagogical expertise, not just engineering. The rubrics define WHAT "good teaching" means. Options:
- (A) Engineer-designed, iteratively refined against production transcripts
- (B) Domain expert (Sir Zia) designs rubrics, engineers implement
- (C) Start with engineer-designed, have domain expert review and refine

**Recommendation**: (C) — engineers draft initial rubrics based on the book's pedagogical frameworks (4-Layer Method, Socratic Method, scaffolding principles). Domain expert reviews and refines. Calibrate against 20-50 human-scored transcripts.
