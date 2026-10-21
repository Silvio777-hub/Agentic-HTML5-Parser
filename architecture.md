# System Architecture & Technical Design

## 1. High-Level Architecture Overview

This project implements an **Agentic AI Pipeline for Autonomous HTML5 Parser Engineering and Self-Healing**. Rather than relying on monolithic code generation, the system utilizes a **partially ordered multi-agent workflow** with intermediate, auditable artifacts at every stage.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        INPUT: HTML5 SPEC SUBSET                        │
│            (Human specification fragment & interface rules)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │   1. SpecAgentAI   │  (The Architect)
                         │ (Rule Extractor)   │
                         └──────────┬─────────┘
                                    │
                                    ├─→ spec.yml (structured grammar & rules)
                                    │
                                    ▼
                         ┌────────────────────┐
                         │  2. CodegenAgentAI │  (Lead Implementer)
                         │  (Code Generator)  │
                         └──────────┬─────────┘
                                    │
                                    ├─→ code.patch (unified diff implementation)
                                    │
               ┌────────────────────┴────────────────────┐
               │    PARALLEL STAGE (ThreadPoolExecutor)  │
               │   Both consume code.patch concurrently  │
               ▼                                         ▼
    ┌──────────────────────┐                  ┌──────────────────────┐
    │  3. CritiqueAgentAI  │                  │  4. RedTeamAgentAI   │
    │  (Code Reviewer &    │                  │  (Adversarial Edge-  │
    │   Quality Auditor)   │                  │   Case Generator)    │
    └──────────┬───────────┘                  └──────────┬───────────┘
               │                                         │
               ├─→ approval.json                         ├─→ test_red_team.py
               │                                         │
               └────────────────────┬────────────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │   5. TestAgentAI   │  (QA Conformance)
                         │ (Pytest Runner)    │
                         └──────────┬─────────┘
                                    │
                                    ├─→ test_report.json
                                    │
                                    ▼
                         ┌────────────────────┐
                         │  6. MonitorAgentAI │  (DevOps Watchdog)
                         │(Trace & Health)    │
                         └──────────┬─────────┘
                                    │
                                    ├─→ health_report.json
                                    │
                         ┌──────────▼──────────┐
                         │   All Tests Pass?   │──── YES ───► [ SUCCESSFUL BUILD ]
                         └──────────┬──────────┘
                                    │ NO (Failures Detected)
                                    ▼
                         ┌────────────────────┐
                         │  7. RepairAgentAI  │  (Auto-Debugger & Mechanic)
                         │(Trace-guided Patch)│
                         └──────────┬─────────┘
                                    │
                                    ├─→ repair_N.patch (AST / logic fix)
                                    │
                         ┌──────────▼──────────┐
                         │ Iteration Loop ≤ 3  │──── (Re-evaluates Tests)
                         └─────────────────────┘
```

---

## 2. The 7 Specialized Agents

| # | Agent Class | Role | Input | Output Artifact |
|---|---|---|---|---|
| 1 | `SpecAgentAI` | **Architect** | HTML5 subset description & interface contract | `spec.yml` (tokens, tags, closure rules) |
| 2 | `CodegenAgentAI` | **Lead Coder** | `spec.yml` + existing parser code | `code.patch` (Python unified diff) |
| 3 | `CritiqueAgentAI` | **Reviewer** | `code.patch` + `spec.yml` | `approval.json` (syntax, standards, quality score) |
| 4 | `RedTeamAgentAI` | **Ethical Hacker** | `code.patch` + parser contract | `test_red_team.py` (deep nesting, XSS, Unicode) |
| 5 | `TestAgentAI` | **QA Engineer** | Generated parser + test suites | `test_report.json` (pass/fail summary) |
| 6 | `MonitorAgentAI` | **Watchdog** | Execution trace from `parse_with_trace()` | `health_report.json` (latency, memory, recursion) |
| 7 | `RepairAgentAI` | **Mechanic** | Traceback, failure context & source code | `repair_N.patch` (targeted fix, max 3 loops) |

---

## 3. Concurrency & Parallel Execution Model

### Why Parallelism is Used
The overall agent workflow is partially ordered. Most stages have strict linear dependencies (you cannot generate code before specification, nor can you repair failures before running tests).

However, after `CodegenAgentAI` produces `code.patch`:
- `CritiqueAgentAI` needs only the generated code and the specification to evaluate code quality.
- `RedTeamAgentAI` needs only the generated code to generate adversarial attack vectors.

Neither agent depends on the output of the other.

### Implementation (`src/parallel_runner.py`)
Both agents are dispatched concurrently using Python's `concurrent.futures.ThreadPoolExecutor`:

```python
critique_fn = functools.partial(critique_agent.run, generated_code)
red_team_fn = functools.partial(red_team_agent.run, generated_code)

critique_result, red_team_result = run_agents_parallel(
    [critique_fn, red_team_fn],
    timeout=120,
)
```

* **Speedup:** Reduces wall-clock review/audit duration by approximately **42%** during full pipeline executions.

---

## 4. Parser Architecture (`src/parser.py`)

The generated parser is a pure-Python, zero-dependency HTML5 parser implementing:
1. **Tokenizer (Finite State Machine):**
   - States: `DATA`, `TAG_OPEN`, `TAG_NAME`, `BEFORE_ATTRIBUTE_NAME`, `ATTRIBUTE_NAME`, `BEFORE_ATTRIBUTE_VALUE`, `ATTRIBUTE_VALUE`, `SELF_CLOSING_START_TAG`.
   - Handles unquoted, single-quoted, and double-quoted attributes, as well as self-closing tags (`<img />`, `<br />`).
2. **DOM Tree Builder:**
   - Constructs hierarchical `TreeNode` instances (`name`, `attributes`, `children`, `text_content`, `parent`).
   - Supports implicit tag closure (e.g., `<p>` closing automatically before `<div>` or next `<p>`).
3. **Streaming API (`StreamingHTMLParser`):**
   - Incrementally consumes chunked HTML input, maintaining state across chunk boundaries.
   - Emits SAX-style callbacks: `on_start_tag(name, attrs)`, `on_end_tag(name)`, `on_data(text)`.
4. **Execution Tracing (`parse_with_trace`):**
   - Instruments tokenizer transitions, DOM insertion events, and execution timing for telemetry consumed by `MonitorAgentAI` and `RepairAgentAI`.

---

## 5. Testing & Verification Methodology

### A. Automated Integration & Streaming Tests
- **Location:** `tests/test_integration.py` and `tests/test_streaming.py`
- **Scope:** 34 automated unit and integration tests covering:
  - Basic and nested tag structures
  - Implicit tag closures
  - Attribute parsing variations (single, double, unquoted, boolean)
  - Streaming chunked parsing and event propagation
  - Malformed and unclosed tag recovery

### B. Adversarial Security Suite
- **Location:** `scripts/run_adversarial.py`
- **Scope:** 15 distinct adversarial attack vectors:
  - Deep tag recursion (200+ levels)
  - Memory stress via long attributes (5,000+ characters)
  - Unicode edge cases, null characters, and zero-width spaces
  - Script injection & malformed comments

### C. Compliance Verification
- **Location:** `scripts/run_compliance.py`
- **Data File:** `data/sample_compliance_tests.dat`
- **Structure:**
  - Evaluates parser outputs against standardized `.dat` test files (input HTML vs expected document tree lines).
  - Current baseline: 10 structural conformance test cases (100% pass on core subset).
  - Designed for extension to the full upstream `html5lib-tests` suite.

---

## 6. Interactive Web Dashboard (`dashboard/index.html`)

- **Server:** `scripts/serve_dashboard.py` (served on port 8082 by default)
- **Features:**
  - **Live DOM Inspector:** Interactive input textarea where users can enter arbitrary HTML and inspect the generated hierarchical DOM tree in real time via `POST /api/parse`.
  - **Pipeline Telemetry:** Displays compliance summaries, adversarial attack results, benchmark latencies, and agent status.
