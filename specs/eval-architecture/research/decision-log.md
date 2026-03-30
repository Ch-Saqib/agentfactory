# Decision Log & Scope Enforcement Record

**Author**: QA & Scope Enforcer
**Date**: 2026-02-26
**Inputs**: research-brief.md, skills-eval-landscape.md, agent-eval-landscape.md, ai-employee-eval-gap-analysis.md

---

## 1. Contradictions Found

### Contradiction 1: Framework Selection — Three Researchers, Three Different Stacks

**What**: Each researcher recommends a different primary toolset, and combining them naively yields 5-6 tools.

**Skills researcher says**: Custom harness (keep existing) + Promptfoo (for model comparison only). Two tools.

**Agent researcher says**: inspect_ai (eval harness) + LangWatch/Scenario (simulation) + Langfuse (observability). Three tools. Explicitly says "do NOT build a custom eval harness."

**AI Employee researcher says**: Promptfoo (ranking/comparison) + Braintrust (production loop). Two tools.

**The problem**: The union of all recommendations is: Custom harness + Promptfoo + inspect_ai + LangWatch/Scenario + Langfuse + Braintrust = **six tools**. This is tool sprawl, not architecture. Maintaining integrations, learning curves, and debugging across six tools is a serious operational burden.

**Deeper issue**: The Skills researcher argues the existing custom Node.js harness is better than any framework for skills-level eval. The Agent researcher argues inspect_ai (Python) is better than building custom. The AI Employee researcher argues Promptfoo covers most of what's needed. These are not just different recommendations — they reflect different philosophies about custom vs. off-the-shelf, and they disagree on the value of the existing codebase.

**Resolution needed**: Can we pick ONE primary eval framework that handles at least 2 of the 3 domains acceptably? Or is the domain difference genuinely large enough to justify different frameworks? The brief asked "three separate systems, three layers of one system, or three configurations of the same system?" — the researchers collectively answered "three separate systems" without explicitly acknowledging they were doing so.

---

### Contradiction 2: Custom Harness — Keep or Kill?

**What**: Direct contradiction on the value of building/maintaining custom eval infrastructure.

**Skills researcher says**: "The project already has a well-designed custom eval harness... Replacing this with Promptfoo would lose fidelity without gaining much." Verdict: Keep custom, add Promptfoo alongside it.

**Agent researcher says**: "What NOT to Build: Custom eval harness — inspect_ai already does this well." Verdict: Don't build custom, adopt inspect_ai.

**AI Employee researcher says**: "Almost nothing is genuinely novel at the infrastructure level." Verdict: Frameworks handle 70%, don't over-invest in custom.

**The tension**: The Skills researcher treats the existing `evals/flashcards/` harness as a valuable asset to preserve. The Agent researcher treats custom harnesses as antipatterns. The AI Employee researcher implies the whole thing is mostly configuration, not code.

**What's at stake**: If we keep the custom harness AND adopt inspect_ai AND use Promptfoo, we maintain three separate execution environments. If we consolidate onto one framework, we lose some fidelity in the domain that framework wasn't designed for.

**Resolution needed**: Is the existing `evals/flashcards/` harness so specialized that no framework can replace it? Or is the Skills researcher exhibiting sunk-cost bias? A concrete test: list the 5 specific capabilities of the custom harness that Promptfoo cannot replicate, and assess whether those capabilities justify maintaining a separate system.

---

### Contradiction 3: Grading Architecture — Skills-as-Graders vs. Rubrics vs. Three-Tier

**What**: Three different mental models for how grading should be architected.

**Skills researcher says**: "Skills-as-Graders" — package grading logic as SKILL.md files with YAML frontmatter, scripts/, and references/. The grader IS a skill. Emphasizes portability and versioning.

**Agent researcher says**: Three-tier grading — code-based (deterministic), model-based (LLM judge with rubric), human (calibration). Doesn't mention Skills-as-Graders at all. Treats graders as eval infrastructure, not skills.

**AI Employee researcher says**: "It's all rubric design, not infrastructure." Grading is writing good LLM judge prompts. The packaging format is secondary.

**Compatibility assessment**: These are actually more compatible than they appear:
- Skills-as-Graders is a *packaging format* for grading logic (deterministic + LLM judge in one portable unit)
- Three-tier is a *conceptual model* for what kinds of grading exist
- "It's rubric design" is a *priority statement* about where to invest effort

They don't fundamentally disagree — but they don't explicitly agree either. The risk is that Skills-as-Graders becomes the packaging standard for skills-level eval but doesn't extend to agent-level eval (where inspect_ai has its own Scorer abstraction), creating two incompatible grading packaging systems.

**Resolution needed**: Should Skills-as-Graders be the universal grading format across all three domains? Or is it only appropriate for skills-level eval while agent/employee evals use framework-native grading? If universal, how does a SKILL.md grader integrate with inspect_ai's Scorer interface?

---

### Contradiction 4: Python vs. Node.js Runtime Split

**What**: The existing codebase is Node.js/TypeScript. Two of three recommended frameworks are Python-only.

**Skills researcher says**: Keep existing Node.js harness + Promptfoo (Node.js native). All JavaScript. No runtime conflict.

**Agent researcher says**: inspect_ai (Python-only) + LangWatch/Scenario (Python, TypeScript, and Go). Python is the primary recommendation.

**AI Employee researcher says**: Promptfoo (Node.js) + Braintrust (Python SDK + TypeScript SDK). Mixed.

**The problem**: If we adopt inspect_ai for agent eval, the eval infrastructure is split across two runtimes: Node.js for skills, Python for agents. This means:
- Two dependency trees to maintain
- Two CI/CD pipelines for eval
- Developers need proficiency in both
- Shared grading logic (e.g., deterministic checks) must be ported or wrapped

**Nobody explicitly addressed this.** The Agent researcher noted inspect_ai is "Python-only" as a gap but still recommended it as the primary tool. The Skills researcher noted it as a reason to avoid inspect_ai for skills. Neither discussed the operational cost of maintaining two runtimes for one eval system.

**Resolution needed**: Is the team willing to maintain a dual-runtime eval system? Or should runtime consistency (all Node.js, or all Python) be a selection constraint? This is an operational decision, not a technical one.

---

### Contradiction 5: Braintrust — Recommended and Dismissed

**What**: Braintrust appears in two different roles across the research.

**Agent researcher says**: Lists Braintrust as "more of an observability+eval platform than an agent testing framework" (Section 2). Does NOT include it in the primary recommendation. Explicitly suggests Langfuse instead for observability.

**AI Employee researcher says**: Recommends "Braintrust for production loop" as one of two primary tools. Calls it "best unified offline+online."

**Skills researcher says**: Rates Braintrust as "Medium" relevance — "pytest for LLMs with offline evaluation + observability + experiment tracking."

**The contradiction**: One researcher recommends Braintrust, one excludes it in favor of Langfuse, one is neutral. If both Braintrust AND Langfuse end up in the stack, we have two observability platforms. If we pick only one, one researcher's recommendation is overridden.

**Resolution needed**: Braintrust or Langfuse? Not both. Key differentiators: Braintrust is commercial (no self-hosting), Langfuse is MIT-licensed and self-hostable. Braintrust has stronger eval-to-production bridge, Langfuse has stronger tracing. This is a buy-vs-open-source decision.

---

## 2. Scope Enforcement

### Sections Within Scope

The following sections stay appropriately at architecture/direction level:

- **Skills researcher**: Framework analysis (Section 2), Skills-as-Graders architecture (Section 3), recommendation (Section 6) — all discuss WHAT to use and WHY, not implementation details
- **Agent researcher**: Framework analysis (Section 2), simulated user problem (Section 3), recommendation (Section 7) — architecture-level assessment
- **AI Employee researcher**: 4-layer analysis (Section 1), honest assessment (Section 4), framework coverage map (Section 5), recommendation (Section 6) — stays firmly at direction level

### Sections Drifting to Implementation

1. **Skills researcher, Section 4 (Concrete Example)**: The content personalization eval walkthrough goes deep into specific JSON dataset schemas, YAML frontmatter, bash commands, and eval flow pseudocode. This is implementation-level detail — appropriate for a spec, premature for a direction decision. **Verdict**: Useful as illustration but should be flagged as "example only, not prescriptive schema."

2. **Agent researcher, Section 6 (Concrete Example)**: The TutorClaw eval walkthrough specifies YAML task definitions, multi-turn conversation scripts, and specific grading scores. Similar to Skills Section 4 — illustrative but implementation-level. **Verdict**: Same as above.

3. **Skills researcher, Section 3 (Skills-as-Graders Architecture)**: The directory structure (`teaching-quality-grader/SKILL.md` + `scripts/` + `references/`) and pipeline diagram are concrete enough to be implementation guidance. This is the RIGHT level of detail for a spec but slightly ahead of a direction decision. **Verdict**: Borderline — useful for the decision-maker but not essential at this stage.

### Scope Verdict

**Overall: The team stayed mostly focused on direction decisions.** The concrete examples in the Skills and Agent research are implementation-flavored but serve as illustrations of feasibility. No researcher produced database schemas, API endpoints, or actual code — the brief's OUT OF SCOPE boundaries were respected. The main drift is toward premature specificity in examples, not toward building things we shouldn't be deciding yet.

---

## 3. Key Questions Assessment

### Q1: Three Separate Systems, Three Layers of One System, or Three Configurations of the Same System?

**Skills researcher position**: Skills eval is fundamentally single-turn prompt evaluation. It's so different from multi-turn agent eval that it belongs in a separate system (the existing custom harness + Promptfoo).

**Agent researcher position**: Agent eval is multi-turn, tool-using, stateful. It needs purpose-built agent eval tools (inspect_ai + LangWatch/Scenario). Implicitly treats this as a separate system from skills eval.

**AI Employee researcher position**: AI Employee eval is "70% framework features, 20% rubric design, 10% custom scripting." Doesn't treat it as needing its own system — it's configuration on top of Promptfoo + Braintrust.

**Synthesis**: The researchers **implicitly answered "three separate systems"** without explicitly confronting this question. Each researcher optimized for their domain in isolation and picked the best tools for that domain. Nobody proposed a unified framework that handles all three.

**QA enforcer assessment**: This is the most important unresolved question. The answer has massive implications for maintenance, developer experience, and architectural complexity. Three separate systems means three times the integration work, three learning curves, and three sets of CI/CD pipelines. The researchers were asked to evaluate their domains — they weren't asked to optimize for cross-domain simplicity. This question needs stakeholder input with a clear presentation of the tradeoffs.

**My recommendation**: Push toward "three configurations of ONE primary system" with a secondary tool where necessary. The primary system should be Promptfoo (covers skills natively, has multi-turn support for agent eval, and is Node.js-native). The secondary tool should be LangWatch/Scenario for simulated users (the ONE capability Promptfoo genuinely lacks). This gives two tools, not six. inspect_ai is excellent but introduces a Python runtime; Braintrust is excellent but introduces a commercial dependency. Neither is justified when Promptfoo + LangWatch/Scenario can cover the same ground with less operational cost.

---

### Q2: Is the "Thin Layer We Build" Just Agent Skills (Graders + Datasets), or Does It Include Infrastructure?

**Skills researcher says**: Yes to Skills-as-Graders. The thin layer is: extract existing grading logic into SKILL.md format + build a grader-skill loader. No new infrastructure — just repackaging.

**Agent researcher says**: The thin layer is: TutorClaw AgentAdapter + teaching quality rubrics + student persona definitions + eval datasets + orchestration scripts. Five components, mostly content, some scripting.

**AI Employee researcher says**: "It's rubric design." The thin layer is: student persona library + teaching quality rubrics + session-chaining script (200-500 lines). Almost entirely content, minimal code.

**Synthesis**: All three researchers agree the thin layer is predominantly **content** (rubrics, personas, datasets), not infrastructure. The disagreement is on packaging: Skills researcher wants to package grading logic as SKILL.md files, Agent researcher wants to use framework-native abstractions, AI Employee researcher is packaging-agnostic.

**QA enforcer assessment**: This is the clearest consensus across all three researchers. The thin layer is:
1. Grading rubrics (LLM judge prompts for teaching quality, personalization quality, etc.)
2. Student personas (behavioral definitions for simulated students)
3. Eval datasets (test cases with expected criteria)
4. A thin orchestration/session-chaining script for longitudinal eval

Skills-as-Graders is an attractive packaging format that dogfoods the project's own standard. Whether it's the RIGHT packaging for agent-level grading depends on whether inspect_ai or Promptfoo is the eval runner (each has its own grader abstraction). If we choose one primary framework, we should use THAT framework's native grading mechanism and only use Skills-as-Graders as the SOURCE FORMAT that gets compiled into framework-native graders.

---

### Q3: Does the 4-Layer Architecture Survive Contact With the Existing Framework Landscape?

**Skills researcher**: Doesn't address the 4-layer architecture. Focuses on skills-level eval only.

**Agent researcher**: Doesn't address the 4-layer architecture directly. Proposes a three-tool stack that partially maps to it.

**AI Employee researcher**: Directly challenges the 4-layer architecture. Verdict: "70% existing framework features, 20% grading rubric design, 10% custom scripting." Layer 0 is "process discipline." Layer 1 is "Promptfoo config." Layer 2 is "two different rubrics." Layer 3's bridge loop is "a Braintrust feature."

**Synthesis**: The AI Employee researcher effectively **deflated the 4-layer vision** from a novel architecture to a configured deployment of existing tools. The other two researchers didn't engage with the 4-layer framing at all, which itself is telling — they didn't need it to explain their domain's eval needs.

**QA enforcer assessment**: The 4-layer vision survives as a **conceptual framework for thinking about eval maturity**, not as an **architecture requiring custom infrastructure**. This is actually a positive finding — it means less to build. But it requires a mindset shift: the 4 layers describe a maturity journey through progressive configuration of existing tools, not a novel system to engineer.

The vision should be reframed as:
- **Layer 0**: Adopt eval framework + set up CI hooks (week 1)
- **Layer 1**: Configure ranking tables + write domain rubrics (weeks 2-4)
- **Layer 2**: Add persona-specific rubrics for personalization dimensions (weeks 4-6)
- **Layer 3**: Connect production monitoring + automate trace-to-dataset pipeline (weeks 6-8)

This is a deployment roadmap, not an architecture diagram.

---

## 4. Risk Assessment

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| 1 | **Tool proliferation**: Union of recommendations = 6 tools. Maintenance burden, integration complexity, onboarding cost. | High | High (if recommendations followed uncritically) | Pick ONE primary framework. Add secondary tools only when primary genuinely can't do the job. Maximum 2-3 tools total. |
| 2 | **Python/Node.js runtime split**: inspect_ai is Python-only, existing codebase is Node.js. Two dependency trees, two CI pipelines, two skill sets. | Medium | High (if inspect_ai adopted) | Either commit to Python for all eval (migration cost) or stay Node.js-native (Promptfoo + custom). Avoid maintaining both. |
| 3 | **LangWatch/Scenario maturity**: Newer framework, less battle-tested. Could have breaking changes, sparse documentation, smaller community. | Medium | Medium | Evaluate LangWatch/Scenario against Promptfoo's simulated user provider first. If Promptfoo's multi-turn support is "good enough," skip LangWatch entirely. |
| 4 | **Integration glue**: The recommended tools don't natively integrate with each other. inspect_ai doesn't call LangWatch/Scenario. Langfuse doesn't read Promptfoo results. We'd be building glue code. | Medium | High (if multi-tool stack adopted) | Prefer tools with native integrations. Promptfoo + Langfuse have some integration. inspect_ai + LangWatch have none. |
| 5 | **Over-architecture**: The 4-layer vision pulls toward building a sophisticated system when "Promptfoo + good rubrics" might be 80% of the value. | High | Medium | Start with the simplest possible eval (Promptfoo config + one rubric + 5 test cases). Add complexity only when the simple version provably fails. |
| 6 | **"Just rubrics" underestimation**: If AI Employee researcher is right that it's mostly rubric design, under-investing in rubric quality while over-investing in infrastructure wastes effort in both directions. | Medium | High | Allocate 60% of eval effort to rubric design and calibration, 40% to infrastructure. Most teams do the inverse. |
| 7 | **Simulated user unreliability**: Research shows simulated users vary up to 9 percentage points by model and systematically miscalibrate. Trusting simulation scores as absolute quality measures is dangerous. | High | High | Treat simulation evals as regression detectors and relative comparisons ONLY. Never use simulated scores to make absolute quality claims. Human calibration is non-negotiable. |
| 8 | **Sunk cost on existing harness**: The existing `evals/flashcards/` harness works and the Skills researcher recommends keeping it. But maintaining custom infrastructure alongside framework adoption creates long-term maintenance debt. | Low | Medium | Set a decision deadline: after framework adoption, evaluate whether the custom harness offers capabilities the framework can't replicate. If not, migrate and deprecate. |

---

## 5. Decisions Requiring Stakeholder Input

### Decision 1: Primary Eval Framework

**Question**: Which single framework should be the primary eval runner across all three domains?

**Options**:
- **A: Promptfoo** — Node.js native (matches existing stack), strong model comparison, supports multi-turn (scripted), YAML-driven, MIT licensed. Weakest on simulated users.
- **B: inspect_ai** — Python-only, purpose-built for agent eval, strongest multi-turn/sandboxing, government-backed. Requires Python runtime and porting graders.
- **C: Promptfoo for skills + inspect_ai for agents** — Best-of-breed per domain but dual-runtime, dual-pipeline, higher maintenance.

**Researchers recommend**: Effectively option C (different primary tools per domain).

**QA enforcer recommends**: **Option A (Promptfoo)** as the single primary framework, with LangWatch/Scenario added ONLY IF Promptfoo's multi-turn proves insufficient after hands-on testing. Rationale: Promptfoo is Node.js-native (no runtime split), covers skills eval strongly, has multi-turn support (scripted), and has the best model comparison. Its gaps (simulated users, session-level scoring) can be addressed with custom providers or a secondary tool. Starting with one framework and expanding is less risky than starting with three and trying to integrate.

**Stakes**: Getting this wrong means either (a) adopting a tool that can't handle a domain and migrating later (months of rework), or (b) adopting too many tools and drowning in integration complexity (ongoing maintenance burden).

---

### Decision 2: Observability Layer

**Question**: Do we need a dedicated observability/cost-tracking tool alongside the eval framework?

**Options**:
- **A: Langfuse** — MIT licensed, self-hostable, strong tracing, weaker eval features. Free.
- **B: Braintrust** — Commercial, strong eval-to-production bridge, excellent cost tracking. $249/month Pro tier.
- **C: Neither (defer)** — Start without observability, add it when production monitoring becomes necessary. Reduces initial complexity.

**Researchers recommend**: Agent researcher says Langfuse. AI Employee researcher says Braintrust.

**QA enforcer recommends**: **Option C (defer)**. Observability is a production concern. The immediate need is getting evals running at all. Adding an observability layer before we have production traffic to observe is premature. Revisit after the first eval suite is running and producing results.

**Stakes**: Low stakes either way. Observability tools are additive — easy to adopt later. The main risk of early adoption is distraction from the harder problem (rubric design).

---

### Decision 3: Skills-as-Graders Scope

**Question**: Should Skills-as-Graders (SKILL.md packaging for grading logic) be the universal grading format, or skills-domain only?

**Options**:
- **A: Universal** — All graders across all domains are packaged as SKILL.md files. Dogfoods the standard, maximizes portability. Requires adapters for framework-native grading interfaces.
- **B: Skills-domain only** — Skills eval uses Skills-as-Graders. Agent/Employee eval uses framework-native graders (Promptfoo assertions, inspect_ai Scorers). Less portable, less adapter code.
- **C: SKILL.md as source, compile to framework-native** — Write grading rubrics as SKILL.md (canonical source), but compile/transform them into the target framework's native grading format. Best of both worlds but requires a compiler layer.

**Researchers recommend**: Skills researcher implies universal. Agent and AI Employee researchers don't engage with the format at all.

**QA enforcer recommends**: **Option B (skills-domain only)** for now. Skills-as-Graders makes sense where the existing skill infrastructure already exists. Forcing agent-level grading into SKILL.md format before we know which agent eval framework we're using adds complexity without value. Revisit universality after both domains have working evals.

**Stakes**: Medium. If we go universal now and it doesn't fit agent eval, we've wasted effort on adapters. If we go domain-only now and want universal later, the migration is straightforward (repackage rubrics into SKILL.md).

---

### Decision 4: Runtime Constraint

**Question**: Should "Node.js-compatible" be a hard constraint on framework selection?

**Options**:
- **A: Hard constraint** — All eval tools must run in Node.js or have a Node.js SDK. Eliminates inspect_ai. Keeps the stack homogeneous.
- **B: Soft constraint** — Prefer Node.js but allow Python for capabilities that can't be replicated in Node.js. Accept dual-runtime if justified.
- **C: No constraint** — Pick the best tool regardless of runtime. Accept operational complexity.

**Researchers recommend**: Skills researcher implicitly says A (keeps recommending Node.js tools). Agent researcher implicitly says C (recommends Python tools freely). AI Employee researcher doesn't address this.

**QA enforcer recommends**: **Option A (hard constraint)** unless someone can demonstrate a specific capability that ONLY exists in Python tools and is essential (not nice-to-have). The operational cost of dual-runtime eval infrastructure is ongoing and compounds. inspect_ai's advantages over Promptfoo for agent eval are real but not so large that they justify a permanent Python dependency in a Node.js project.

**Stakes**: High for long-term maintenance. A dual-runtime system is permanently more expensive to operate, debug, and onboard new developers into.

---

### Decision 5: Simulated User Approach

**Question**: How should simulated student conversations be generated for agent eval?

**Options**:
- **A: LangWatch/Scenario** — Native simulated user support, MIT licensed, purpose-built. Adds a new dependency but minimal custom code.
- **B: Promptfoo custom provider** — Build a custom provider that uses an LLM as the simulated student within Promptfoo's multi-turn framework. More custom code, fewer dependencies.
- **C: Scripted conversations only** — Pre-write all conversation scripts (no simulation). Simplest, most deterministic, but doesn't test agent adaptation to novel student responses.
- **D: Defer** — Start with skills-level eval (single-turn) which doesn't need simulated users. Add simulated users when agent eval becomes a priority.

**Researchers recommend**: Agent researcher says A (LangWatch/Scenario). AI Employee researcher leans toward B (Promptfoo's simulated user provider).

**QA enforcer recommends**: **Option D (defer)**. Skills eval doesn't need simulated users. Agent eval (TutorClaw) is not mentioned as an immediate priority in the brief. Start with what's needed now (skills eval), and make the simulated user decision when agent eval work begins. By that time, the framework landscape may have shifted (Promptfoo's multi-turn support is actively improving).

**Stakes**: Low for deferral. The simulated user decision doesn't block skills eval. The risk of deciding now is locking into a tool before we have hands-on experience with the eval framework.

---

## 6. The Honest Questions

### Things Nobody Addressed That Should Have Been

1. **Who runs evals?** All three researchers describe WHAT to build but none discuss WHO operates it. Is this a CI/CD-only process? Does a human trigger eval runs? Who reads the results and acts on them? Eval infrastructure without an operational owner becomes shelfware.

2. **What's the eval budget?** The Skills researcher mentions "$0.05 with Haiku, $3.00 with Opus per eval run." The Agent researcher mentions 5-10 trials per task with multi-turn conversations. Nobody modeled the total cost of running a comprehensive eval suite across all three domains weekly. This could be $5/week or $500/week depending on scale. The budget determines what's feasible.

3. **How does eval quality itself get measured?** All researchers discuss calibrating graders against human judgment. But who does the human judging? How often? What's the process for detecting grader drift? The Anthropic article emphasizes regular transcript review — nobody specified what "regular" means or who does it.

4. **What are the first 5 test cases?** Three research documents totaling ~3,500 lines and nobody proposed the first 5 concrete test cases for any domain. The AI Employee researcher is right — rubric design is the hard part. But nobody started designing a rubric. The research phase should have produced at least one draft rubric to validate against.

5. **What's the existing harness's actual coverage?** The Skills researcher references `evals/flashcards/` repeatedly but nobody measured its current coverage. How many skills have evals? How many don't? What percentage of the skill catalog is un-evaluated? This determines urgency.

### Assumptions Everyone Made That Should Be Challenged

1. **"LLM-as-judge is good enough for teaching quality"** — All three researchers assume LLM judges can evaluate pedagogical quality. But teaching quality is deeply subjective and culturally dependent. Has anyone validated that an LLM judge can distinguish between a Socratic approach that helps learning and one that frustrates the student? The Agent researcher cites the "Lost in Simulation" paper showing simulated users are unreliable — the same skepticism should apply to simulated judges.

2. **"We need multi-turn simulation"** — The Agent researcher treats multi-turn simulation as essential. But for initial eval, scripted conversations (option C above) would be simpler, more deterministic, and fully sufficient for regression testing. Dynamic simulation is a Phase 2 problem, not a Phase 1 requirement.

3. **"The three domains are clearly distinct"** — Everyone accepted the Skills/Agent/Employee taxonomy from the brief. But is there actually a sharp boundary between "agent eval" and "employee eval"? An AI Employee IS an agent with additional context. The distinction may be more about eval maturity (simple -> complex) than about fundamentally different systems.

4. **"Promptfoo is maintained and stable"** — Everyone recommends or considers Promptfoo but nobody audited its maintenance trajectory. Open-source CLI tools can be abandoned. What's the bus factor? Who funds development? Is there a commercial entity behind it?

### Risks Everyone Overlooked

1. **Eval fatigue**: If evals are expensive to run and results are hard to interpret, the team will stop running them. The biggest risk isn't choosing the wrong framework — it's building an eval system nobody uses. Simplicity and low friction should be the top design priorities.

2. **Rubric gaming**: If the AI Employee learns the rubric criteria (because the rubric is in the codebase and the model has access to it during training or through system prompts), it may optimize for rubric scores rather than genuine teaching quality. This is Goodhart's Law applied to AI eval. Nobody discussed adversarial robustness of the grading system.

3. **Versioning complexity**: Skills-as-Graders introduces a versioning challenge — the grader version, the subject skill version, the dataset version, and the model version all affect results. A result from "grader v1.2 + skill v3.0 + dataset v2.1 + claude-sonnet-4-20250514" is not comparable to "grader v1.3 + skill v3.0 + dataset v2.1 + claude-sonnet-4-20250514" without careful version tracking. Nobody proposed a versioning scheme.

---

## 7. Verdict: Ready for Direction Decision?

### Is There Enough Information?

**Yes, with caveats.** The three research documents collectively cover the framework landscape thoroughly. The key findings are:

1. The framework landscape is mature — no need to build eval plumbing from scratch
2. Skills eval (single-turn) and agent eval (multi-turn) have genuinely different requirements
3. The thin layer is mostly rubrics + personas + datasets, not infrastructure
4. The 4-layer vision translates to a maturity roadmap, not a novel architecture

What's missing is hands-on validation. No researcher tested any framework against the project's actual eval needs. The recommendations are based on documentation review and feature comparison, not proof-of-concept testing.

### The Minimum Viable Decision

**Decide these three things now:**

1. **Primary framework**: Promptfoo (my recommendation) or inspect_ai. Pick one. Start there.
2. **Runtime constraint**: Node.js-only or allow Python. This constrains the framework choice.
3. **First domain**: Start with skills eval (simplest, most infrastructure already exists) before tackling agent eval.

**Defer everything else:**
- Observability tool selection (no production traffic yet)
- Simulated user approach (skills eval doesn't need it)
- Universal grading format (decide after one domain is working)
- Longitudinal eval (Phase 2+)

### What Should Be Deferred to the Build Phase

1. **Framework integration details** — How exactly Promptfoo consumes SKILL.md files, specific YAML configs, adapter code
2. **Rubric design** — Actual grading criteria for teaching quality, personalization, etc.
3. **Dataset creation** — Specific test cases, golden outputs, persona definitions
4. **Observability setup** — Langfuse/Braintrust/neither decision
5. **Simulated user implementation** — Which approach, which framework
6. **Longitudinal eval scripting** — Session-chaining, temporal comparison

### The Path Forward

The direction decision should be a 30-minute conversation with stakeholders, not a 50-page document. Present the 5 decisions above, get alignment on each, and start building. The research phase has produced sufficient signal. More research will not reduce uncertainty — only hands-on building will.
