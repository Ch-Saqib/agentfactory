# Eval Architecture (Index)

**Authoritative decision**: `specs/eval-architecture/direction-decision.md`

This folder contains both (a) the final direction and (b) research notes that include discarded options. If you’re feeling “scope creep”, start with the direction decision.

## What We’re Actually Building

An eval *capability* across three nested scopes:

1. **Skills evals** (single-turn): input → skill output → grade → regressions + model comparison  
2. **Agent evals** (multi-turn): scripted/simulated conversations + tool-use verification + session scoring  
3. **AI Employee evals** (end-to-end): personalization + longitudinal/session-chaining + ranking tables

**Non-goal** (explicit): rebuilding generic eval plumbing. Frameworks already do “dataset + run + compare”.

## Current Repo Reality (Why It Feels Sprawly)

Today there are **multiple eval stacks** in the repo:

- **Skills regression harness (Node)**: `evals/flashcards/`  
  Deterministic checks + LLM judge + pass@k/pass^k + baselines + reports.
- **Promptfoo proof-of-concept (Node)**: `evals/promptfoo-proof/`  
  Shows Promptfoo can run our deterministic grader as a JS assertion (model comparison runner).
- **Assessment grading runner (bash + optional Claude CLI)**: `evals/assessment-architect/`  
  A separate, bespoke runner for exam quality grading (not yet in the same dataset/trials/baseline pattern).
- **Tutor prompt evals (Python + OpenAI Evals API)**: `apps/study-mode-api/evals/`  
  20-case suite with model-graded rubrics (OpenAI-only + Python; conflicts with the “Promptfoo + custom harness” consolidation decision).

This is the main source of confusion: we have *eval intent* across the org, but not a single coherent “one way” to run/grade/compare.

## Requirements → Current Status (Snapshot)

| Requirement | Intended tool/shape (Direction Decision) | Current implementation | Status |
|---|---|---|---|
| Skills regression eval | Custom harness (`run-eval.sh` pattern) | `evals/flashcards/` | ✅ Working (flashcards only) |
| Model comparison | Promptfoo matrix view | `evals/promptfoo-proof/` | ✅ POC working (live run needs API key) |
| 20+ skill test cases | Dataset growth from failures | `evals/flashcards/datasets/cases.json` (5 cases) | ❌ Not done |
| Rubrics as SKILL.md “grader skills” | Extract `buildPrompt()` into SKILL.md | Flashcards rubric is inline in `llm-judge.js` | ❌ Not done |
| Agent eval (multi-turn) | Promptfoo multi-turn + scripted first | Not present (Tutor eval exists elsewhere) | ❌ Not started |
| AI Employee eval (longitudinal) | Deferred until employee exists | None | ⏸ Deferred |
| CI quality gate | Promptfoo GitHub Action (+ harness gates) | None | ❌ Not done |
| Observability + prod loop | Langfuse later | None | ⏸ Deferred |

## How to Get Unstuck (Recommended)

Pick **one “now” objective** and delete the rest from your mental scope:

### MVP (1–2 weeks)
- Make **Skills evals** boring-and-reliable: expand flashcards to **20+ cases**, freeze baselines, and run in CI.
- Use **Promptfoo only for model comparison experiments** (don’t migrate the whole harness yet).

### Consolidation decision (choose explicitly)
- **Option A (recommended)**: Keep `apps/study-mode-api/evals` for now, but treat it as *legacy/isolated*; converge new evals to Promptfoo + Node harness.
- **Option B**: Migrate tutor evals from OpenAI Evals API → Promptfoo (single runner across domains).

If you want, I can implement Option A’s “index + guardrails” (docs + scripts) or start the Option B migration (Promptfoo config + rubric assertions for the tutor suite).

