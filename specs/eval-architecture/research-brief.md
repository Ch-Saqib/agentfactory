# Eval Architecture — Research Brief

## Core Question

Eval is fundamentally: **dataset + LLM runs + compare + tweak.** Dozens of frameworks already do this. We are NOT rebuilding eval plumbing.

What we need:
1. Which existing framework(s) handle our three domains best?
2. What's the thin layer we build on top?
3. Can that thin layer be Agent Skills (per agentskills.io spec)?
4. What datasets do we need to create?
5. How do the three domains share infrastructure but differ in what they measure?

## The Three Domains (Nested Scopes)

### Skills Evals
Evaluating an Agent Skill (SKILL.md + scripts/ + references/) in isolation. Does this skill produce correct output? Does a new version regress? Does it work better with Model A or Model B?

### Agent Evals
Evaluating an agent system (harness + model + tools + skills working together). Multi-turn. Does the agent complete the task? Does it degrade after 50 tool calls? Does it recover from errors?

### AI Employee Evals
Evaluating the full AI Employee (agent + channels + memory + governance + personalization). Sir Zia's 4-layer vision:
- Layer 0: Continuous improvement substrate
- Layer 1: Component evals (variable × across → ranking table)
- Layer 2: Personalization evals (content WHAT × interaction HOW)
- Layer 3: Dual-mode engine (simulation × production, bridge loop)

## Input Artifacts

1. **Anthropic: "Demystifying Evals for AI Agents"** — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
2. **Agent Skills Specification** — https://agentskills.io/specification
3. **Agent Skills Integration Guide** — https://agentskills.io/integrate-skills
4. **Issue #766** — Existing eval harness v2 spec for flashcard evals (golden comparison, skill invocation, multi-agent grading)

## Existing Eval Infrastructure (Issue #766)

The project already has `evals/flashcards/` with:
- Deterministic graders (`graders/deterministic.js`)
- LLM judge grader (`graders/llm-judge.js`)
- Aggregator (`graders/aggregate.js`)
- Dataset cases (`datasets/cases.json`)
- Run script (`run-eval.sh`)

Issue #766 proposes: skill invocation layer, golden comparison mode, per-agent reporting, manifest schema enhancement.

## Deliverable

A single **Direction Decision Document** with:
1. Domain definitions — what each means, how they nest, what's shared
2. Landscape map — existing frameworks rated against our three domains
3. The Skills-as-Graders verdict — can our eval logic be Agent Skills?
4. Build-vs-Adopt matrix — per component, per domain
5. Revised architecture — does the 4-layer vision hold, simplify, or transform?
6. Recommended path — one clear recommendation with trade-offs
7. Three immediate deliverables mapped
8. Open decisions — what needs stakeholder input
