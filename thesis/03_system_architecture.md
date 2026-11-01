# Chapter 3: System Architecture and Methodology

## 3.1 Architectural Overview
The architecture of the Agentic AI HTML5 Parser system is governed by three foundational design principles:
1. **Division of Concerns:** Decomposing compiler engineering into 7 specialized agent personas.
2. **Intermediate Artifact Auditability:** Replacing opaque inter-agent memory with persistent, human-inspectable files.
3. **Bounded Trace-Guided Closed-Loop Repair:** Automating the diagnostic-patching cycle with deterministic convergence bounds.

The system topology is modeled as a **partially ordered directed acyclic graph (DAG)** with a conditional repair cycle:

```
[Human Spec Input]
        │
        ▼
┌──────────────────┐
│  1. SpecAgentAI  │ ──► [spec.yml]
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│2. CodegenAgentAI │ ──► [code.patch]
└────────┬─────────┘
         │
    ┌────┴─────────────────────────────┐
    │  PARALLEL STAGE (ThreadPool)     │
    ▼                                  ▼
┌──────────────────┐       ┌──────────────────┐
│3. CritiqueAgentAI│       │4. RedTeamAgentAI │
└────────┬─────────┘       └────────┬─────────┘
         │                          │
    [approval.json]         [test_red_team.py]
         │                          │
    └────┬─────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  5. TestAgentAI  │ ──► [test_report.json]
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│6. MonitorAgentAI │ ──► [health_report.json]
└────────┬─────────┘
         │
   [All Tests Pass?]
   ├── YES ────────► [SUCCESSFUL BUILD / Production Ready]
   └── NO (Failures)
         │
         ▼
┌──────────────────┐
│ 7. RepairAgentAI │ ──► [repair_N.patch] (Loop <= 3 Iterations)
└────────┬─────────┘
         │
         └─────────► (Re-trigger TestAgentAI)
```

## 3.2 The 7 Specialized Agent Roles

### 3.2.1 Stage 1: Specification Formulation (`SpecAgentAI`)
* **Role:** The Lead Systems Architect.
* **Input:** Human feature descriptions and structural subset specifications.
* **Responsibilities:** Analyzes the target HTML5 features and extracts formal grammar rules, tokenizer states, tag classifications (void, formatting, phrasing, flow), and implicit closure triggers.
* **Output Artifact:** `specs/spec.yml` (Structured YAML specification).

### 3.2.2 Stage 2: Code Implementation (`CodegenAgentAI`)
* **Role:** Lead Software Implementer.
* **Input:** `spec.yml` and the existing baseline codebase.
* **Responsibilities:** Synthesizes AST-compliant Python code implementing the state machine and tree construction logic. Crucially, the agent outputs unified diffs (`code.patch`) rather than full-file replacements, preserving existing regressions.
* **Output Artifact:** `runs/<id>/artifacts/code.patch`.

### 3.2.3 Stage 3: Concurrent Audit & Stress Testing
To optimize wall-clock synthesis time, Stage 3 executes two non-dependent agents concurrently using Python's `ThreadPoolExecutor`:
* **`CritiqueAgentAI` (The Code Reviewer):** Conducts static AST audits, PEP 8 enforcement, type annotation verification, and checks against prohibited functions (`eval`, `exec`). Produces `runs/<id>/artifacts/approval.json`.
* **`RedTeamAgentAI` (The Ethical Hacker):** Synthesizes adversarial stress cases designed to trigger recursion stack overflow, CPU hangs, and injection vulnerabilities. Produces `tests/test_red_team.py`.

### 3.2.4 Stage 4: Conformance & Telemetry Gating
* **`TestAgentAI` (QA Conformance):** Programmatically executes `pytest` against unit tests, W3C boundary suites, and newly generated red-team suites. Produces `test_report.json`.
* **`MonitorAgentAI` (DevOps Watchdog):** Ingests runtime telemetry from `parse_with_trace()`. It evaluates memory allocation, peak recursion depth, and execution duration per token, compiling `health_report.json`.

### 3.2.5 Stage 5: Autonomous Closed-Loop Self-Repair (`RepairAgentAI`)
* **Role:** The Automated Debugger.
* **Trigger:** Activated if `test_report.json` contains failures or `health_report.json` detects resource violations.
* **Mechanism:** Consumes the exact failure diff, the active token stream, and source lines. It generates a surgical patch (`repair_N.patch`).
* **Convergence Bounds:** The loop is bounded to $\le 3$ iterations. If convergence is not achieved within 3 cycles, the pipeline halts and generates an escalation log.

## 3.3 Concurrency Architecture & Parallel Dispatch
Stage 3 represents an independent verification phase: `CritiqueAgentAI` and `RedTeamAgentAI` both depend solely on `code.patch` and `spec.yml`. 

Implemented in `src/parallel_runner.py`, `run_agents_parallel()` dispatches both agent calls concurrently. As detailed in Chapter 5, this parallelization reduces Stage 3 wall-clock execution time by **42%** without degrading critique depth.

## 3.4 Economic Efficiency & Green AI via SHA-256 Caching
A common critique of multi-agent LLM systems is excessive token consumption and computational carbon footprint. To address this, our architecture incorporates an on-disk SHA-256 `ResponseCache` (`src/cache.py`).

The cache hashes the composite prompt `sha256(system_prompt + "::" + user_message)`. When tests or benchmarks are re-executed:
* Repeated LLM API calls are intercepted.
* Financial cost is reduced from **\$0.06 per run** to **\$0.00**.
* Latency drops from **~8.2s** to **0.00s**.
* Computational carbon emissions drop to zero.
