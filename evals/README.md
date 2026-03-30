# Evals (Repo Entry Point)

This repo currently has multiple eval suites/runners. Use this as the jumping-off point.

## Flashcards Skill (Node custom harness)

Path: `evals/flashcards/`

- Run deterministic-only fixture suite: `./evals/flashcards/run-eval.sh --with-llm never`
- Run with LLM judge (requires `claude` CLI or `--judge-cmd`): `./evals/flashcards/run-eval.sh --with-llm auto --judge-model haiku`
- Grade live outputs: `./evals/flashcards/run-eval.sh --grade-live --with-llm never`

See: `evals/flashcards/README.md`

## Promptfoo Proof (Model comparison POC)

Path: `evals/promptfoo-proof/`

- Pipeline test (no API key): `cd evals/promptfoo-proof && npx promptfoo eval --config promptfooconfig.mock.yaml --no-cache`
- Live comparison (requires `ANTHROPIC_API_KEY`): `cd evals/promptfoo-proof && npx promptfoo eval --no-cache`
- View results: `cd evals/promptfoo-proof && npx promptfoo view`

See: `evals/promptfoo-proof/README.md`

## Assessment Architect (Exam quality grader)

Path: `evals/assessment-architect/`

- Run: `./evals/assessment-architect/run-eval.sh <SLUG> [chapter-type] [chapter-path]`

This runner is currently bespoke (bash + optional `claude -p`) and not yet in the same dataset/trials/baseline pattern as `evals/flashcards/`.

## Teach Me Tutor (Python + OpenAI Evals API)

Path: `apps/study-mode-api/evals/`

- Run: `cd apps/study-mode-api && uv run python evals/run_eval.py`

This suite uses OpenAI’s hosted Evals API and is separate from the Node eval stacks under `evals/`.

