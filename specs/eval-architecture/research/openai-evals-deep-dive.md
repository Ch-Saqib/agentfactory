# OpenAI Evals Deep-Dive Analysis

**Date**: 2026-02-26
**Purpose**: Determine whether OpenAI Evals offers capabilities that Promptfoo and inspect_ai do not, and whether it deserves consideration in our eval architecture.

---

## 1. Overview (5 minutes to understand)

### What It Does

OpenAI Evals is actually **two distinct products** that share a name but have different architectures, audiences, and capabilities:

1. **OpenAI Evals (Open-Source GitHub)** — `github.com/openai/evals` — An MIT-licensed Python framework and registry of benchmarks for evaluating LLMs. Created January 2023. Uses YAML configs + JSONL data files, runs via `oaieval` CLI. 17.9k stars, 2.9k forks, 460 contributors, 689 commits. This is the "classic" evals framework.

2. **OpenAI Evals API (Platform)** — Launched April 2025 — A hosted API service (`/v1/evals` endpoint) with a web dashboard. Structures evals around four concepts: Eval (task + criteria), Run (execution against a model), DataSourceConfig (schema for test data), and TestingCriteria (graders). Accessed via the OpenAI Python SDK (`pip install openai>=1.20.0`). This is the newer, commercial offering.

OpenAI explicitly recommends the Evals API over the open-source repo for new work.

### Why It Exists

Originally created for OpenAI's internal model evaluation and opened to crowdsource benchmarks. Evolved into a commercial eval-as-a-service platform tightly integrated with OpenAI's model fine-tuning pipeline (the "measure -> improve -> ship" loop with Reinforcement Fine-Tuning).

### Who It's For

- Teams using OpenAI models exclusively who want a tight eval-to-fine-tuning feedback loop
- Researchers submitting benchmarks to OpenAI's registry
- Developers wanting quick eval setup via a web dashboard without local infrastructure

---

## 2. Architecture and Config Format

### Open-Source Framework Architecture

```
Registry (YAML) --> Eval Class (Python) --> CompletionFn (Protocol) --> Model
                                        --> Recorder --> JSONL Logs
```

**Config format**: Two-level YAML in `evals/registry/evals/`:

```yaml
# Level 1: Metadata
spider-sql:
  id: spider-sql.dev.v0
  metrics: [accuracy]
  description: "SQL generation eval"

# Level 2: Implementation
spider-sql.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: sql/spider_sql.jsonl
    eval_type: cot_classify
    modelgraded_spec: sql
```

**Data format**: JSONL files with input/ideal pairs:

```json
{
  "input": [
    {"role": "system", "content": "You are a SQL assistant..."},
    {"role": "user", "content": "How many employees?"}
  ],
  "ideal": "SELECT COUNT(*) FROM employees"
}
```

**Custom eval creation**: Extend `evals.Eval` base class, override `eval_sample()` and `run()`:

```python
class CustomEval(evals.Eval):
    def eval_sample(self, test_sample, rng):
        # Query model via self.completion_fn
        # Record result via evals.record_and_check_match()
        pass

    def run(self, recorder):
        samples = evals.get_jsonl(self.test_jsonl)
        self.eval_all_samples(recorder, samples)
        return {"accuracy": evals.metrics.get_accuracy(recorder.get_events("match"))}
```

**Completion Function Protocol**: Interface for plugging in arbitrary model backends:

```python
class CompletionFn(Protocol):
    def __call__(self, prompt: Union[str, list[dict]], **kwargs) -> CompletionResult:
        ...

class CompletionResult(ABC):
    @abstractmethod
    def get_completions(self) -> list[str]:
        ...
```

### Evals API Architecture (Platform)

Structured around REST endpoints:
- `POST /v1/evals` — Create eval configuration
- `POST /v1/evals/{eval_id}/runs` — Launch eval run
- `GET /v1/evals/{eval_id}/runs` — List runs
- Dashboard UI at `evals.openai.com`

**Key difference from open-source**: Evals API runs on OpenAI's infrastructure — you send data to their servers, they execute models and return graded results. No local execution.

---

## 3. Grading System

The Evals API (platform) supports **six grader types**:

| Grader Type | What It Does | Equivalent in Promptfoo |
|---|---|---|
| **String Check** | Exact match against reference using `{{ item.correct_label }}` templates | `equals`, `contains` assertions |
| **Score Model Grader** | LLM assigns a numeric score to output | `llm-rubric` with score output |
| **Label Model Grader** | LLM classifies output into labels (pass/fail/partial) | `llm-rubric` with classification |
| **Text Similarity** | Cosine, fuzzy_match, BLEU, GLEU, METEOR, ROUGE (1-5, L) | `similar`, `rouge-n` assertions |
| **Python Grader** | Arbitrary Python code in sandboxed environment | `javascript` assertion (different language) |
| **Multi Grader** | Combines multiple graders into single score | `assert-all` / weighted scoring |

### Python Grader Details

```python
# The grader expects a `grade` function with two arguments returning a float
def grade(output: str, reference: str) -> float:
    # Custom logic here
    return 1.0 if output == reference else 0.0
```

**Limitations**:
- Runs in a sandbox disconnected from the internet
- Limited set of packages installed (no arbitrary pip install)
- Cannot internally run model inference (no combining Python + LLM grading)
- Python-only (no JavaScript/TypeScript option)

### Open-Source Framework Graders

The classic framework uses a different grading model:
- **Basic templates**: Deterministic comparison (exact match, includes, fuzzy match)
- **Model-graded templates**: LLM-as-judge using `ModelBasedClassify` with chain-of-thought classification
- **Custom eval classes**: Full Python control by extending `evals.Eval`

**Critical note**: The open-source repo is NOT accepting custom code evals for contribution. You can only submit model-graded evals with custom YAML files. You CAN write custom code for local use, but the community contribution model is restricted.

---

## 4. Feature-by-Feature Comparison with Promptfoo

| Dimension | OpenAI Evals (API + OSS) | Promptfoo | Winner for Our Use Case |
|---|---|---|---|
| **Runtime** | Python 3.9+ required | Node.js native (npm install) | **Promptfoo** — Our codebase is Node.js |
| **Config format** | YAML + JSONL (OSS) or JSON API calls | YAML with inline assertions | **Promptfoo** — More ergonomic YAML |
| **Model support** | OpenAI models only (API); any via CompletionFn (OSS) | 50+ providers native (OpenAI, Anthropic, Azure, Bedrock, Ollama) | **Promptfoo** — We need multi-provider |
| **Simulated users** | No native support | Not native (custom provider needed) | **Tie** — Neither has it built-in |
| **Custom graders** | Python only (sandboxed, limited packages) | JavaScript/TypeScript assertions (native to our stack) | **Promptfoo** — JS is our language |
| **Model comparison** | Per-run comparison only; no side-by-side matrix | Prompt x Model x Test Case matrix; `select-best` | **Promptfoo** — Matrix view is killer |
| **Cost tracking** | No built-in (just API usage charges) | Basic token tracking | **Tie** — Both weak here |
| **CI/CD** | No official GitHub Action; manual API integration | Official GitHub Action, CLI-native for CI | **Promptfoo** — First-class CI support |
| **Open source** | MIT (OSS repo); Proprietary (API) | MIT, fully open | **Promptfoo** — Fully open |
| **Dashboard** | Yes (platform dashboard, good) | Yes (local web UI, good) | **Tie** — Both have UIs |
| **Deterministic checks** | String check + text similarity (~6 types) | 25+ assertion types (contains, regex, cost, latency, JSON schema, etc.) | **Promptfoo** — Far more assertion types |
| **LLM-as-judge** | Score + Label model graders | `llm-rubric`, `model-graded-closedqa`, `factuality` | **Promptfoo** — More pre-built patterns |
| **pass@k / pass^k** | Not supported natively | Not natively (can be built with repeat + aggregation) | **Tie** — Neither has it built-in |
| **Agent eval** | Trace grading (new, OpenAI Agents SDK specific) | Tool call assertions, agent provider support | **Promptfoo** — More mature for arbitrary agents |
| **Fine-tuning loop** | Native (eval -> RFT -> re-eval) | Not integrated | **OpenAI Evals** — Only advantage |
| **Data privacy** | Data sent to OpenAI servers (API) | Runs locally, data stays local | **Promptfoo** — Data sovereignty |
| **Community** | 17.9k stars, declining active development on OSS | 5.6k stars, very active development | **Promptfoo** — More active iteration |
| **Node.js SDK** | No evals support in openai-node SDK | N/A (is Node.js native) | **Promptfoo** — No Python dependency |

**Score: Promptfoo wins 12 dimensions, OpenAI Evals wins 1, Tie on 4.**

---

## 5. Multi-Turn and Agent Eval Support

### OpenAI Evals Approach

**Open-source framework**: Uses the Completion Function Protocol. For multi-turn, you implement a custom `CompletionFn` that manages conversation state internally. The framework itself is single-turn by default — the `prompt -> completion` interface processes one exchange. Multi-turn requires wrapping the agent loop inside the completion function, which is an awkward inversion of control.

**Evals API (Platform)**: Introduced **trace grading** for agent evaluation:
- A "trace" is the end-to-end log of decisions, tool calls, and reasoning steps
- Trace evals grade these logs to assess correctness, quality, and adherence to expectations
- Designed to work with the **OpenAI Agents SDK** specifically
- Evaluates agent performance across many examples for benchmarking changes and identifying regressions

**Key limitation**: Trace grading is designed for the OpenAI Agents SDK ecosystem. If your agent doesn't produce OpenAI-format traces, you'd need to convert your trace format. This is a tight coupling to OpenAI's agent infrastructure.

### Promptfoo Approach

Multi-turn via `_conversation` variable and `sessionId` + `runSerially: true`. Each conversation maintains history. User turns are explicitly scripted — you define every turn in the YAML. No dynamic simulation, but predictable and deterministic.

### inspect_ai Approach (for reference)

Purpose-built for multi-turn via the `Dataset -> Task -> Solver -> Scorer` pipeline. Solvers implement arbitrary agent loops. Building a simulated user is ~20 lines of Python. Architecturally the strongest multi-turn story.

### Verdict on Multi-Turn

OpenAI Evals' trace grading is the newest approach and architecturally interesting, but it is tightly coupled to OpenAI's Agents SDK. For our use case (evaluating TutorClaw, which is NOT built on the OpenAI Agents SDK), this coupling is a dealbreaker for trace grading. The open-source framework's multi-turn story requires awkward workarounds via custom CompletionFn implementations.

---

## 6. Strengths (Where OpenAI Evals Is Genuinely Better)

### 1. Fine-Tuning Feedback Loop
The Evals API integrates directly with OpenAI's Reinforcement Fine-Tuning (RFT). The workflow is: write eval -> run eval -> identify failures -> fine-tune model on failures -> re-evaluate. No other framework offers this closed loop. If you are fine-tuning OpenAI models, this is genuinely valuable.

### 2. Benchmark Registry
The open-source repo contains 1,400+ community-contributed evals across QA, reasoning, code generation, content filtering, and more. This is the largest open eval registry. Useful for benchmarking models against established baselines (e.g., "how does GPT-4.5 compare to GPT-4o on MMLU?").

### 3. Web Dashboard
The platform dashboard at `evals.openai.com` provides a clean UI for creating evals, viewing results, and iterating — without writing any code. For non-technical stakeholders who want to see eval results, this is friendlier than Promptfoo's local UI.

### 4. Trace Grading (If Using OpenAI Agents SDK)
For teams building on the OpenAI Agents SDK specifically, trace grading provides deep introspection into agent behavior — tool call sequences, reasoning steps, decision points. This is more granular than Promptfoo's output-level assertions.

### 5. Zero-Setup for OpenAI-Only Teams
If your entire stack is OpenAI models + OpenAI Agents SDK, the Evals API requires no local setup. Configure in dashboard, run via API, view results. No CLI installation, no YAML authoring.

---

## 7. Weaknesses (Where It Falls Short for Our Use Case)

### 1. OpenAI Lock-In (Critical)
The Evals API only works with OpenAI models. We need to evaluate and compare across providers (OpenAI, Anthropic, Google). This is a fundamental architectural mismatch. The open-source framework technically supports custom CompletionFns for other providers, but this requires writing Python wrappers — significant effort compared to Promptfoo's one-line provider config.

### 2. Python-Only Runtime (Critical)
Our codebase is Node.js/TypeScript. OpenAI Evals requires Python 3.9+. There is NO evals support in the `openai-node` TypeScript SDK. Using OpenAI Evals means maintaining a Python environment, Python dependencies, and Python graders alongside our TypeScript stack. This is a cost, not a feature.

### 3. No Node.js/TypeScript SDK for Evals (Critical)
The OpenAI Node.js SDK (`openai` npm package) does not expose evals endpoints. The README makes no mention of evals. All Evals API examples are Python-only. This means even API-based evals require Python client code.

### 4. Weak Deterministic Assertions
We need 25+ deterministic checks per eval. OpenAI Evals offers: string check, text similarity (with multiple metrics), and Python grader. Promptfoo offers: equals, contains, icontains, regex, starts-with, is-json, is-valid-openai-tools-call, is-valid-openai-function-call, contains-json, javascript, python, cost, latency, perplexity, rouge-n, similar, and more. The assertion library gap is massive.

### 5. No Model Comparison Matrix
Promptfoo's core value proposition is the `prompt x model x test case` matrix with side-by-side results. OpenAI Evals has no equivalent. You can run the same eval against different models in separate runs, but there's no built-in comparison view. This is a major gap for our "which model produces best output?" requirement.

### 6. Sandboxed Python Grader Limitations
The Python grader runs in a sandbox: no internet, limited packages, cannot call models. This means you cannot implement complex grading that requires fetching reference data, calling a separate grading model, or using specialized libraries. Promptfoo's JavaScript assertions run in your local environment with full access.

### 7. Data Privacy Concern
The Evals API sends your test data and model outputs to OpenAI's servers. For educational content that may contain proprietary curriculum, this is a governance concern. Promptfoo runs entirely locally.

### 8. No Official CI/CD Integration
No GitHub Action, no CLI designed for CI pipelines. You can script API calls, but there's no first-class CI story. Promptfoo has a dedicated GitHub Action with threshold-based pass/fail.

### 9. Two Confusing Products
Having both the open-source framework AND the platform API — with different architectures, different capabilities, and different config formats — creates confusion. The open-source repo's README now redirects to the platform, suggesting the OSS version is in maintenance mode. Betting on a product with an unclear future is risky.

---

## 8. Maturity Assessment

| Metric | OpenAI Evals (OSS) | OpenAI Evals API | Promptfoo |
|---|---|---|---|
| First release | Jan 2023 | Apr 2025 | 2023 |
| GitHub stars | 17.9k | N/A (hosted) | 5.6k |
| Contributors | 460 | N/A | 150+ |
| Update frequency | Declining (OSS being deprecated in favor of API) | Active (part of OpenAI platform) | Very active (weekly releases) |
| Production usage | OpenAI internal, research community | OpenAI customers | Broad industry adoption |
| Documentation | Good (OSS), improving (API) | Growing cookbook examples | Excellent, comprehensive |
| Version stability | No semver, commits-based | API versioned | Semver, stable releases |

### Risk Assessment

- **OSS repo**: Likely heading toward archive/maintenance-only status as OpenAI pushes the platform API
- **Evals API**: Tightly coupled to OpenAI's commercial strategy; features prioritize OpenAI model users
- **Promptfoo**: Independent open-source project; no vendor lock-in risk

---

## 9. Runtime and Dependencies

### OpenAI Evals (OSS)
```
Language: Python 3.9+
Install: pip install evals
Dependencies: openai, pyyaml, numpy, pandas, and many others
CLI: oaieval
Data storage: Git-LFS for registry, /tmp/evallogs/ for results
```

### OpenAI Evals API
```
Language: Python 3.9+ (SDK requirement)
Install: pip install openai>=1.20.0
Dependencies: openai Python SDK
Auth: OPENAI_API_KEY required
Data storage: OpenAI's servers
Node.js: NOT SUPPORTED for evals
```

### Promptfoo (for comparison)
```
Language: Node.js (TypeScript/JavaScript)
Install: npx promptfoo@latest init
Dependencies: Minimal, npm-based
CLI: promptfoo eval
Data storage: Local (SQLite), configurable
Auth: Per-provider API keys
```

**The runtime mismatch is decisive**: Our project runs on Node.js. Adding Python as a dependency for evaluation tooling introduces environment management complexity (venv, pip, Python version management), cross-language build coordination, and a second language that team members must understand for grader authoring.

---

## 10. Agent Eval Features Comparison

| Feature | OpenAI Evals | Promptfoo | inspect_ai |
|---|---|---|---|
| Tool use tracking | Trace grading (OpenAI SDK only) | Tool call assertions | Built-in (solver pipeline) |
| Trajectory analysis | Trace grading (decision + tool + reasoning logs) | Output-level only | Full transcript inspection |
| State management | Via OpenAI Agents SDK traces | Conversation variable `_conversation` | `state.messages` in solver |
| Simulated users | No | No (custom provider) | Architecturally easy (~20 LOC) |
| Sandboxed execution | Cloud-side (OpenAI servers) | Local | Docker, Kubernetes, Proxmox |
| Multi-agent | OpenAI Agents SDK multi-agent traces | Not native | Composable multi-agent |
| External agent support | OpenAI Agents SDK only | Any HTTP/CLI agent | External agents via CLI |

---

## 11. Verdict: EXCLUDE

**Recommendation**: Exclude OpenAI Evals from our eval architecture.

**Rationale**:

1. **Language mismatch is disqualifying**: Python-only runtime in a Node.js codebase. No TypeScript SDK support for evals. Every grader, every config interaction, every CI integration would require Python — a permanent tax on our development workflow.

2. **Provider lock-in is disqualifying**: The Evals API works with OpenAI models only. We explicitly require multi-provider model comparison (OpenAI vs Anthropic vs Google). This is a core requirement, not an edge case.

3. **Promptfoo is strictly better for our use case**: Promptfoo wins on 12 of 17 comparison dimensions. It is Node.js native, supports 50+ providers, has 25+ assertion types, has first-class CI/CD support, and runs locally. There is no dimension where OpenAI Evals is better for us except fine-tuning integration, which we do not currently need.

4. **The one genuine strength (fine-tuning loop) is not in our requirements**: If we later need to fine-tune OpenAI models based on eval failures, we can export eval results from Promptfoo and feed them into OpenAI's fine-tuning API separately. The tight integration is convenient but not necessary.

5. **Strategic risk**: The open-source framework appears to be in decline (OpenAI redirects to platform API). The platform API is a commercial product with vendor lock-in incentives. Betting on it would tie our eval infrastructure to OpenAI's commercial roadmap.

### If We Ever Reconsider

The ONLY scenario where OpenAI Evals would add value:

- We commit to fine-tuning OpenAI models specifically using Reinforcement Fine-Tuning (RFT)
- We want the automated "eval -> find failures -> fine-tune on failures -> re-eval" loop
- AND we're willing to maintain a parallel Python eval pipeline for this specific workflow

In that narrow case, the Evals API could serve as a supplementary tool alongside Promptfoo (primary) — not a replacement. But this is a future decision contingent on fine-tuning needs that do not currently exist.

---

## Sources

- [OpenAI Evals GitHub Repository](https://github.com/openai/evals)
- [OpenAI Evals API Documentation](https://platform.openai.com/docs/guides/evals)
- [OpenAI Evals API Reference](https://platform.openai.com/docs/api-reference/evals)
- [OpenAI Graders Documentation](https://platform.openai.com/docs/guides/graders)
- [OpenAI Agent Evals Guide](https://developers.openai.com/api/docs/guides/agent-evals/)
- [OpenAI Trace Grading Guide](https://developers.openai.com/api/docs/guides/trace-grading/)
- [Testing Agent Skills Systematically with Evals (OpenAI Blog)](https://developers.openai.com/blog/eval-skills/)
- [OpenAI Evals Getting Started Cookbook](https://developers.openai.com/cookbook/examples/evaluation/getting_started_with_openai_evals)
- [OpenAI Custom Eval Documentation](https://github.com/openai/evals/blob/main/docs/custom-eval.md)
- [OpenAI Completion Function Protocol](https://github.com/openai/evals/blob/main/docs/completion-fn-protocol.md)
- [Helicone: Top Prompt Evaluation Frameworks 2025](https://www.helicone.ai/blog/prompt-evaluation-frameworks)
- [DataTalks.Club: Open Source Agent Evaluation Tools](https://datatalks.club/blog/open-source-free-ai-agent-evaluation-tools.html)
- [OpenAI for Developers 2025](https://developers.openai.com/blog/openai-for-developers-2025/)
- [OpenAI Node.js SDK](https://github.com/openai/openai-node)
- [OpenAI Evals Pricing Discussion](https://community.openai.com/t/pricing-details-re-evals-feature/981379)
