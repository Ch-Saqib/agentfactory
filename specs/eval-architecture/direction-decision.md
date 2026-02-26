# Eval Architecture — Final Direction Decision

**Date**: 2026-02-26
**Status**: FINAL — Ready for stakeholder review
**Research**: 10 documents, ~4,520 lines of analysis, 1 working proof-of-concept
**Verification**: Post-research audit + hands-on Promptfoo testing completed

---

## Golden Principles

These are the non-negotiable truths distilled from Anthropic, OpenAI, and our own research. Every decision and every task must trace back to one of these.

> **1. "Invest your energy in the evals themselves, not the framework."**
> — Anthropic, "Demystifying Evals for AI Agents"
>
> The framework is a commodity. The test cases, rubrics, and grading logic ARE the product. Stop choosing tools. Start writing evals.

> **2. "Every manual fix is a signal. Turn it into a test."**
> — OpenAI, "Eval Skills"
>
> Every time someone manually corrects a skill output, that correction is a free test case. Capture it. The eval dataset should grow organically from real failures, not be invented in a conference room.

> **3. "Choose deterministic graders where possible."**
> — Anthropic
>
> LLM judges are expensive, slow, and unreliable (up to 9pp variance per "Lost in Simulation"). Deterministic checks are fast, cheap, and reproducible. Use LLM judges only for dimensions that can't be checked with code.

> **4. "A 0% pass rate across many trials is most often a signal of a broken task, not an incapable agent."**
> — Anthropic
>
> If an eval always fails, the eval is wrong — not the model. Fix the eval before blaming the agent.

> **5. "We do not take eval scores at face value until someone digs into the details and reads some transcripts."**
> — Anthropic
>
> Numbers without inspection are dangerous. Someone must read the actual outputs regularly. Evals without an owner become shelfware.

> **6. "Build evals to define planned capabilities BEFORE agents can fulfill them."**
> — Anthropic (Eval-Driven Development)
>
> Write the test first. Like TDD but for AI: define what "good teaching" looks like, then iterate the agent until it passes. Capability evals that start at 0% pass rate make progress visible.

> **7. "Keep checks small and focused on must-pass rather than encoding every preference."**
> — OpenAI
>
> Don't boil the ocean. A few critical checks that catch real failures beat 100 marginal checks that create noise. If a check never fails, delete it.

> **8. Regression detection is the minimum viable eval.**
>
> Before anything fancy: can you tell when a model update breaks something? Baseline comparison + pass^k + deterministic checks. If you can't detect regression, nothing else matters.

---

## Executive Summary

Eval is **dataset + LLM runs + compare + tweak.** The framework landscape is mature enough. We don't need to build eval plumbing. What we need is: **good rubrics, more test cases, and one framework to orchestrate.**

The 4-layer vision (L0-L3) survives as a **deployment roadmap**, not novel architecture. It's approximately 70% existing framework features, 20% grading rubric design, and 10% custom scripting. The innovation is in WHAT we grade (teaching quality, personalization quality), not HOW we run evals.

**Final stack: 2 tools now, 3 when production traffic arrives.**

| Tool | Role | Domains |
|---|---|---|
| **Custom harness** (keep) | Regression testing, pass^k, 25 deterministic checks, baseline diffs | Skills |
| **Promptfoo** (adopt) | Model comparison, multi-turn agent eval, simulated users, CI/CD | All three |
| **Langfuse** (adopt later) | Cost tracking + production monitoring | Agent, AI Employee (when deployed) |

---

## 1. Why Not 5 Tools? Why These 2?

### The Original 5-Tool Stack (and why each was proposed)

| # | Tool | Proposed Role | Who Proposed It |
|---|---|---|---|
| 1 | Custom harness | Skills regression testing | Skills Eval Researcher |
| 2 | Promptfoo | Model comparison only | All researchers |
| 3 | inspect_ai | Agent eval runner | Agent Eval Researcher |
| 4 | LangWatch/Scenario | Simulated users | Agent Eval Researcher |
| 5 | Langfuse | Observability + cost tracking | Integration Architect |

### Why 3 Were Dropped

| Dropped Tool | Justification for Including | Why It's Out |
|---|---|---|
| **inspect_ai** | "Purpose-built for agent eval, best solver/scorer architecture, sandboxing" | **Python runtime** in a Node.js codebase. The unique value (sandboxing) isn't needed — our agents don't execute arbitrary code. Also pre-1.0 (v0.3.x). Promptfoo covers multi-turn + simulation natively in Node.js. |
| **LangWatch/Scenario** | "Promptfoo can't do simulated users" | **That claim was factually wrong.** Promptfoo HAS `promptfoo:simulated-user` with persona support, maxTurns, multi-turn. The entire justification was a research error we caught in verification. Also pre-1.0 (v0.7.x). |
| **Langfuse** | Cost tracking + production monitoring | **No production traffic yet.** Zero agents serving real users. Deferred — not eliminated. Add when we deploy to production. |

### What Anthropic Says About Tool Count

From ["Demystifying Evals for AI Agents"](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):

> "We use a version of Promptfoo for many of our product evals."

> "It's often best to quickly pick a framework that fits your workflow, then invest your energy in the evals themselves."

> "Many teams combine multiple tools, roll their own eval framework, or just use simple evaluation scripts."

**No single-tool mandate.** Anthropic validates our approach: custom harness + Promptfoo. Invest in rubrics and test cases, not framework shopping.

---

## 2. Are We Over-Relying on Promptfoo?

**No. Here's the actual split of responsibilities:**

### What Promptfoo Does (orchestration + comparison)

| Capability | How It Works |
|---|---|
| Model comparison | Matrix view: Model A vs Model B on same test cases |
| YAML-driven test configs | Declarative test definitions, variable substitution |
| Custom JS assertion hosting | Our deterministic checks run inside Promptfoo (proven in POC) |
| Simulated user conversations | Native `promptfoo:simulated-user` provider with personas |
| CI/CD integration | GitHub Actions, PR comments with results |
| Cost tracking (basic) | Per-model token usage in results |

### What Promptfoo CANNOT Do (our custom code covers)

| Gap | Our Solution | Status |
|---|---|---|
| pass@k / pass^k aggregation | `aggregate.js` (lines 215-218) | Exists, working |
| Baseline comparison with deltas | `aggregate.js` (lines 277-291) | Exists, working |
| 25-check deterministic bundle with hard/soft gates + weights | `deterministic.js` (769 lines) | Exists, working |
| Multi-deck cases (F05: 2 lessons → 2 decks) | `run-eval.sh` orchestration | Exists, working |
| LLM judge with 15 criteria + 6 critical thresholds | `llm-judge.js` (354 lines) | Exists, working |
| Consistency scoring formula | `aggregate.js` (line 252) | Exists, working |

**This is a hybrid architecture, not Promptfoo-only.** Promptfoo orchestrates and compares. Our code grades and aggregates. Neither replaces the other.

### Proof-of-Concept Validated This

The working proof at `evals/promptfoo-proof/` demonstrates:
- Promptfoo config parses and renders our skill prompt correctly
- Custom JS adapter bridges our 25-check deterministic grader to Promptfoo's assertion format
- Mock pipeline test: `1 passed, 0 failed, 0 errors (100%)`
- Live run blocked only by missing `ANTHROPIC_API_KEY` in env — config is correct

**Verdict from hands-on testing**: **Complement, not replace.** Promptfoo for model selection experiments. Custom harness for CI regression testing and quality gates.

---

## 3. What the Source Articles Say

### Anthropic: "Demystifying Evals for AI Agents"

**Key patterns extracted** (full analysis: `research/anthropic-evals-deep-dive.md`, 545 lines):

| Pattern | What Anthropic Says | Our Alignment |
|---|---|---|
| Deterministic-first grading | "Start with code-based graders" | 25 deterministic checks run before LLM judge |
| pass@k vs pass^k | "pass@k = at least one trial passes, pass^k = ALL pass" | Implemented exactly (aggregate.js:215-218) |
| Baseline comparison | Track regressions against known-good | baseline-v1.json and baseline-v2.json exist |
| Golden outputs | Known-correct examples for calibration | 5 golden outputs in fixtures/ |
| Negative controls | Cases where output should NOT be produced | F03 is explicit negative control |
| Hard/soft gates | Some checks are blocking, others advisory | hard_pass gates + soft weighted scoring |
| Multiple grader types | Combine code-based + model-based + human | deterministic.js + llm-judge.js (no human yet) |

**16 alignments, 9 gaps identified.** Top gap: **dataset size** — we have 5 cases, Anthropic recommends 20+.

**Tools Anthropic mentions**: Harbor, Promptfoo, Braintrust, LangSmith/Langfuse. They recommend Promptfoo for product evals.

### OpenAI: "Eval Skills" Blog

**Key patterns** (full analysis: `research/openai-evals-deep-dive.md`, 368 lines):

OpenAI's 4-layer eval approach maps directly to our deterministic checks:

| OpenAI Layer | Our Equivalent Checks |
|---|---|
| Outcome checks ("Did the task complete?") | `yaml_parse_success`, `deck_count_matches_target` |
| Process checks ("Did it follow correct steps?") | `card_required_fields_present`, `card_id_pattern_full_prefix` |
| Style checks ("Does output match conventions?") | `fronts_end_with_question_mark`, `thinking_fronts_why_or_how` |
| Efficiency checks ("No waste?") | `no_duplicate_front_back_pairs`, `no_compound_questions` |

**Key advice**: "Start with 10-20 small prompts. Every manual fix is a signal. Turn it into a test."

### OpenAI: Evals API/Platform Guide

**Verdict: EXCLUDE.**

| Reason | Detail |
|---|---|
| **OpenAI model lock-in** | API only evaluates OpenAI models. We need to compare Anthropic models (Haiku vs Sonnet). |
| **Python-only** | No TypeScript/Node.js SDK for evals. |
| **Weak assertions** | 6 grader types vs Promptfoo's 25+. No custom JS assertions. |
| **OSS heading to maintenance** | Open-source version appears deprioritized as OpenAI pushes commercial platform. |
| **One genuine strength** | Eval-to-fine-tuning feedback loop (unique). Not in our requirements. |

---

## 4. Domain Definitions

### Skills Evals
Evaluating a SKILL.md in isolation. Single-turn: input → skill instructions → output → grade. Does this skill produce correct output? Does a new version regress? Does it work better with Model A or Model B?

### Agent Evals
Evaluating a multi-turn, tool-using agent system (TutorClaw). Requires simulated users, session-level scoring, tool call verification. Does the agent complete the teaching task? Is it consistent (pass^k)?

### AI Employee Evals
Evaluating the full AI Employee across sessions. Adds personalization assessment (content WHAT × interaction HOW), longitudinal tracking (is the system learning the student?), and the ranking table (Model × Student Type → Score).

### The Nesting Verdict

Skills → Agent → AI Employee **composes at the grading layer** (rubrics nest: format checks ⊂ teaching quality ⊂ personalization quality). It does **not compose at the runner layer** — single-turn and multi-turn need different orchestration. This means: **shared grading components, separate runners per scope**.

---

## 5. Framework Landscape (Final Assessment)

| Framework | Skills Eval | Agent Eval | AI Employee Eval | Node.js | Open Source | Model Comparison | Verdict |
|---|---|---|---|---|---|---|---|
| **Promptfoo** | Strong | Good (multi-turn + simulated user) | Moderate (ranking native) | Native | MIT | Best-in-class | **ADOPT** |
| **Custom harness** | Exact fit | N/A | N/A | Native | Ours | Manual | **KEEP** |
| inspect_ai | Overkill | Excellent | Good | No (Python) | MIT | Good | **EXCLUDE** — Python runtime |
| LangWatch/Scenario | N/A | Excellent | Good | TS + Python | MIT (pre-1.0) | Weak | **EXCLUDE** — Promptfoo covers sim |
| OpenAI Evals | N/A | N/A | N/A | No (Python) | Partial | No (OpenAI-only) | **EXCLUDE** — vendor lock-in |
| Braintrust | Moderate | Good | Strong | Partial | No (commercial) | Good | **EXCLUDE** — commercial, deferred |
| Langfuse | N/A | Good | Good | Partial | MIT | Weak | **DEFER** — add at production |

---

## 6. The Skills-as-Graders Verdict

**Yes — viable and recommended for skills-domain eval. Defer universality.**

The project already implements this pattern informally:
- `llm-judge.js:buildPrompt()` IS a grader — just not packaged as SKILL.md
- `rubric-grader.md` IS a grader skill body — just lacks frontmatter

**Phase 1**: Extract existing rubrics into proper SKILL.md grader skills (repackaging, no new capabilities).
**Phase 2**: Build a generic grader-skill loader for the eval runner.
**Later**: Evaluate whether Skills-as-Graders extends to agent-level grading or stays skills-domain only.

---

## 7. Build-vs-Adopt Matrix (Final)

| Component | Decision | Tool/Approach | Effort |
|---|---|---|---|
| Eval runner (single-turn) | **Keep** | Custom harness (`run-eval.sh`) | None (exists) |
| Eval runner (multi-turn) | **Adopt** | Promptfoo (multi-turn + simulated user) | Low-Medium |
| Deterministic graders | **Keep** | Custom JS (`deterministic.js`) | None (extend per domain) |
| LLM graders | **Extend** | Grader Skills (SKILL.md rubrics) | Medium |
| Model comparison | **Adopt** | Promptfoo matrix view | Low (YAML config) |
| Aggregation (pass@k/pass^k) | **Keep** | Custom (`aggregate.js`) | None (exists) |
| Baseline comparison | **Keep** | Custom (baseline diff pattern) | None (exists) |
| Cost tracking | **Defer** | Langfuse (when production traffic exists) | — |
| Production monitoring | **Defer** | Langfuse (when production traffic exists) | — |
| Ranking/reporting | **Adopt** | Promptfoo matrix view | Low |
| Student personas | **Build** | JSON definitions | Medium (content) |
| Teaching rubrics | **Build** | SKILL.md grader files | Medium-High (pedagogical expertise) |
| Session chaining | **Defer** | Phase 2+ | — |
| CI/CD integration | **Adopt** | Promptfoo GitHub Actions | Low |

**Summary**: 5 Keep, 4 Adopt, 1 Extend, 2 Build, 3 Defer. The "Build" items are content (rubrics, personas), not infrastructure.

---

## 8. The 4-Layer Vision Reframed

The 4-layer vision survives as a **maturity roadmap**, not custom infrastructure:

| Layer | Original Vision | What It Actually Is | Effort |
|---|---|---|---|
| L0: Continuous Improvement | "System gets better at getting better" | **Process discipline**: run evals regularly, track trends, feed failures back | Habit, not code |
| L1: Ranking Table | Variable × Across → Score matrix | **Promptfoo config**: providers × test cases → matrix view | YAML configuration |
| L2: Personalization | Content WHAT × Interaction HOW | **Two LLM judge rubrics** on the same framework | Rubric design |
| L3: Dual-Mode | Simulation × Production bridge | **Langfuse feature** (deferred) + Promptfoo simulated users | Framework config |

**What's genuinely novel**: Teaching quality rubrics, student persona library, and a session-chaining script (~200-500 lines). Everything else is framework configuration.

---

## 9. Recommended Path (Final)

### Phase 1: Skills Eval + Model Comparison (Week 1-3)
- Extract flashcard LLM rubric → `flashcard-quality-grader/SKILL.md`
- Add Promptfoo config for model comparison (which model generates best flashcards?)
- **Expand test cases from 5 to 20+** (highest priority per Anthropic + OpenAI guidance)
- Build Content Personalization eval using existing harness pattern
- Create shared learner profile schema + 3 profiles (Fatima, Raj, Marcus)
- **Deliverable**: First ranking table (model comparison for flashcard generation)

### Phase 2: Agent Eval (Week 4-7)
- Set up Promptfoo multi-turn config for TutorClaw
- Create teaching quality grader rubric (SKILL.md format)
- Build TutorClaw eval with scripted conversations first (not simulated)
- Test Promptfoo simulated user with student persona
- Sir Zia's Simulator: Model × Persona → Ranking Table
- **Deliverable**: TutorClaw ranking table across models

### Phase 3: Production Loop (Week 8+)
- Add Langfuse for cost tracking + production monitoring
- Automated regression detection in CI (Promptfoo GitHub Actions)
- Production trace → eval dataset pipeline
- Session chaining for longitudinal eval

---

## 10. Three Immediate Deliverables Mapped

### Sir Zia's Simulator (Model × Student → Ranking Table)
- **Runner**: Promptfoo (model comparison is its core strength)
- **Grading**: Teaching quality grader skill
- **Output**: Matrix view — 3+ models × 3 personas × 3 scenarios
- **Phase**: Week 4-7

### TutorClaw Eval
- **Runner**: Promptfoo multi-turn + custom harness for regression
- **Grading**: Code-based (turn count, forbidden patterns) + teaching quality grader
- **Simulation**: Scripted conversations first, Promptfoo simulated users later
- **Key metric**: pass^5 (consistency matters more than occasional brilliance)
- **Phase**: Week 4-7

### Content Personalization Eval
- **Runner**: Custom harness (single-turn, existing pattern)
- **Grading**: Deterministic (format, word count) + two rubric graders (content-WHAT, interaction-HOW)
- **Output**: Per-profile scores + model comparison
- **Phase**: Week 1-3 (simplest, starts first)

---

## 11. Decisions Made (Post-Research + Proof-of-Concept)

Based on the research, verification, deep-dives, and hands-on proof-of-concept, these decisions have clear answers:

### Decision 1: Primary Agent Eval Framework → **Promptfoo**
- Node.js native (no runtime split)
- Covers multi-turn, simulated users, model comparison
- Anthropic uses it for their product evals
- Proof-of-concept validates custom assertion integration
- Custom harness stays for regression testing with pass^k

### Decision 2: Observability → **Defer**
- No production traffic yet
- Add Langfuse when agents serve real users
- Basic cost tracking available in Promptfoo results

### Decision 3: Runtime Constraint → **Node.js only**
- Eliminates inspect_ai, keeps stack homogeneous
- All existing eval code is JavaScript
- Promptfoo is Node.js native

### Decision 4: Skills-as-Graders Scope → **Skills-domain only (for now)**
- Extract existing rubrics first (repackaging)
- Extend to agent grading in Phase 2 if pattern holds
- Don't over-engineer the grader format before proving it

### Decision 5: Simulated Users → **Scripted first, Promptfoo simulated user later**
- Phase 2 starts with scripted conversations (deterministic, debuggable)
- Promptfoo's `promptfoo:simulated-user` provider for exploratory testing
- "Lost in Simulation" paper (9pp variance) means simulated users are research tools, not quality gates

### Decision 6: Teaching Quality Rubric Ownership → **Hybrid**
- Engineers draft from book's pedagogy (4-layer teaching method, Bloom's, CEFR)
- Sir Zia refines with domain expertise
- First rubric: flashcard quality (already partially built in llm-judge.js)

### Decision 7: Eval Cost Budget → **Stakeholder decision needed**
- Skills eval: ~$0.15/run (cheap, run in CI on every PR)
- Agent eval: ~$5-15/run (weekly or per significant change)
- Full suite: ~$50-60/run (monthly baseline)
- **Recommended weekly budget: $15-25** (CI skills evals + weekly agent eval)

---

## 12. Honest Questions That Still Need Answers

1. **Who runs evals? Who reads results? Who acts on findings?** Eval infrastructure without an operational owner becomes shelfware.

2. **Expand test cases from 5 to 20+.** Both Anthropic and OpenAI say 5 is not enough. This is the #1 priority — more test cases, not more architecture.

3. **Can an LLM judge reliably distinguish good teaching from bad teaching?** Everyone assumes yes. Nobody validated it. Must test with known-good and known-bad examples before trusting LLM grading.

4. **Eval fatigue risk.** If evals are expensive to run and hard to interpret, the team will stop running them. Simplicity and low friction above all.

5. **Set the ANTHROPIC_API_KEY and run the live proof.** `cd evals/promptfoo-proof && npx promptfoo eval` — one command to validate Haiku vs Sonnet comparison.

---

## 13. Proof-of-Concept Artifacts

### Working Code (evals/promptfoo-proof/)

| File | Purpose | Status |
|---|---|---|
| `promptfooconfig.yaml` | Production config (Haiku + Sonnet) | Ready (needs API key) |
| `promptfooconfig.mock.yaml` | Mock config (golden fixture, no API) | Tested, passing |
| `prompt.txt` | Flashcard skill prompt with template vars | Working |
| `deterministic-adapter.js` | Bridges 25-check deterministic.js to Promptfoo | Working (VM sandbox) |
| `mock-provider.js` | Returns golden fixture for pipeline testing | Working |
| `test-adapter.js` | 4 unit tests for the adapter | All passing |

### To Run the Live Proof

```bash
cd evals/promptfoo-proof
export ANTHROPIC_API_KEY=sk-ant-...
npx promptfoo eval                    # Run against real models
npx promptfoo view                    # Open comparison view
```

---

## 14. Research Artifacts

All research deliverables in `specs/eval-architecture/research/`:

| File | Lines | Key Contribution |
|---|---|---|
| `skills-eval-landscape.md` | 443 | Framework comparison, Skills-as-Graders architecture |
| `agent-eval-landscape.md` | 494 | Multi-turn framework comparison, TutorClaw walkthrough |
| `ai-employee-eval-gap-analysis.md` | 261 | 4-layer gap analysis, "70/20/10" honest assessment |
| `unified-architecture.md` | 561 | Original 5-tool stack, build-vs-adopt matrix |
| `decision-log.md` | 365 | QA: 5 contradictions, 8 risks, honest questions |
| `verification-audit.md` | 242 | 1 critical error found, 4 minor errors |
| `anthropic-evals-deep-dive.md` | 545 | Every pattern from Anthropic's article, 16 alignments, 9 gaps |
| `promptfoo-deep-dive.md` | 1018 | Full Promptfoo feature reference, adapter requirements, config patterns |
| `openai-evals-deep-dive.md` | 368 | OpenAI Evals assessment — EXCLUDE verdict |
| `promptfoo-proof-results.md` | 223 | POC results — complement, not replace |

**Total**: 4,520 lines across 10 documents + 6 working code files.

---

## 15. Next Steps — No More Architecture, Only Building

*Principle: "Invest your energy in the evals themselves, not the framework."*

### Immediate (This Week)

| # | Task | Principle | Effort | Output |
|---|---|---|---|---|
| 1 | **Run the live Promptfoo proof** | P8 (regression detection) | 5 min | Set `ANTHROPIC_API_KEY`, run `cd evals/promptfoo-proof && npx promptfoo eval`. Validates Haiku vs Sonnet comparison with our grader. |
| 2 | **Write 15 more flashcard test cases** | P2 (every fix = test) | 1-2 days | Mine from: real `--grade-live` failures, edge cases (empty lesson, very short, very long, non-English, ambiguous prompt, formula-only, code-heavy, multi-chapter). Target: 20 total. |
| 3 | **Assign eval owner** | P5 (someone must read transcripts) | 30 min | Who runs evals? Who reads results? Who acts on failures? Name a person, not a role. |

### Short-Term (Week 2-3)

| # | Task | Principle | Effort | Output |
|---|---|---|---|---|
| 4 | **Extract `buildPrompt()` into Grader SKILL.md** | P1 (invest in evals) | Half day | Move `llm-judge.js:100-163` rubric into `flashcard-quality-grader/SKILL.md` with frontmatter. First Skills-as-Graders deliverable. |
| 5 | **Build eval for assessment-architect skill** | P6 (eval before capability) | 1 day | `rubric-grader.md` already exists — add frontmatter, write 5 test cases, wire into harness. Second skill with evals. |
| 6 | **Set up Promptfoo GitHub Action** | P8 (regression detection) | Half day | CI regression on every PR. Skills eval runs, blocks merge on failure. |
| 7 | **Human calibration baseline** | P5 (don't trust scores blindly) | Half day | Have a human grade 5 random flashcard outputs. Compare scores with LLM judge. Measure agreement. Do this once, establish the baseline. |

### Medium-Term (Week 4-7)

| # | Task | Principle | Effort | Output |
|---|---|---|---|---|
| 8 | **Write 5 scripted TutorClaw conversations** | P6 (eval before capability) | 2 days | Hardcoded multi-turn test cases: student asks question → agent responds → grade the response. Not simulated — scripted and deterministic. |
| 9 | **Build teaching quality grader rubric** | P1 (invest in evals) | 2-3 days | SKILL.md rubric: Does the agent teach correctly? Does it follow pedagogical patterns? Does it handle misconceptions? Engineer drafts, Sir Zia refines (Decision 6). |
| 10 | **First model comparison ranking table** | P8 (regression detection) | 1 day | Promptfoo matrix: 3 models × 20 flashcard test cases. Which model generates the best flashcards? Visual answer. |

### What We're NOT Doing (Explicitly Deferred)

| Not Doing | Why | When to Revisit |
|---|---|---|
| Simulated users | "Lost in Simulation" shows 9pp variance. Scripted tests first. | After 20+ scripted cases work reliably |
| Langfuse/observability | No production traffic. Zero agents serving real users. | When TutorClaw is deployed |
| Session chaining | No multi-session agent exists yet | When longitudinal tracking is needed |
| AI Employee eval | No AI Employee exists yet | After agent eval is working |
| More framework research | Framework is decided. Promptfoo + custom harness. | Never (unless a tool fails in practice) |

---

## Sources

- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI: Eval Skills](https://developers.openai.com/blog/eval-skills/)
- [OpenAI: Evals API Guide](https://developers.openai.com/api/docs/guides/evals/)
- [Promptfoo Documentation](https://www.promptfoo.dev/docs/)
- [Promptfoo Simulated User Provider](https://www.promptfoo.dev/docs/providers/simulated-user/)
- [Lost in Simulation (arxiv 2601.17087)](https://arxiv.org/abs/2601.17087) — LLM-simulated users have up to 9pp variance
- [LangWatch/Scenario](https://github.com/langwatch/scenario) — v0.7.14, MIT, pre-1.0
- [inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) — v0.3.130, MIT, Python-only
