# Chapter 1: Introduction and Problem Statement

## 1.1 Context and Motivation
The World Wide Web is built upon the HyperText Markup Language (HTML). Unlike formal domain-specific languages (DSLs) or programming languages governed by deterministic context-free grammars (CFGs), HTML in the wild is notoriously malformed, heterogeneous, and resiliently forgiving. The World Wide Web Consortium (W3C) and the Web Hypertext Application Technology Working Group (WHATWG) codified this reality into the HTML5 standard, specifying an intricate Finite State Machine (FSM) comprising over 80 discrete states and precise tree-construction dispatch rules.

Historically, the development of conforming HTML5 parsers has been a labor-intensive engineering undertaking requiring months of human effort. Parsers such as `html5lib`, Google Chrome's `Blink`, and Mozilla's `Gecko` require tens of thousands of lines of code to handle implicit element closures, foster parenting, misnested formatting tags, and edge-case tokenization without crashing.

Concurrently, the emergence of Large Language Models (LLMs) has transformed automated software engineering. However, monolithic "single-prompt" code synthesis suffers from severe limitations:
1. **Context Drift:** Monolithic prompts struggle to simultaneously balance lexical state rules, tree construction hierarchies, and memory bounds.
2. **Silent Hallucinations:** Code generation models often produce syntactically plausible parsers that catastrophically fail on malformed or deeply nested markup.
3. **Lack of Auditability:** Direct text-to-code pipelines offer no intermediate representations for human verification or programmatic gating.

## 1.2 Research Questions and Objectives
This thesis investigates the hypothesis that a **partially ordered multi-agent AI assembly line** can autonomously synthesize, verify, stress-test, and self-heal a pure-Python HTML5 parser with formal auditability guarantees.

Specifically, this research addresses three primary research questions:
* **RQ1 (Feasibility & Quality):** Can specialized, role-delineated AI agents synthesize a conforming, zero-dependency HTML5 parser that survives official W3C compliance suites without manual intervention?
* **RQ2 (Concurrency & Efficiency):** How does a partially ordered execution model—parallelizing independent audit and adversarial agents—impact wall-clock synthesis time and resource overhead?
* **RQ3 (Self-Repair Convergence):** Can runtime telemetry and execution tracing guide an autonomous debugging agent to locate root causes and generate targeted patches within bounded iterations ($\le 3$)?

## 1.3 Key Contributions
The contributions of this thesis are as follows:
1. **A 7-Agent Autonomous Software Engineering Architecture:** We design an assembly-line pipeline comprising `SpecAgentAI`, `CodegenAgentAI`, `CritiqueAgentAI`, `RedTeamAgentAI`, `TestAgentAI`, `MonitorAgentAI`, and `RepairAgentAI`.
2. **Intermediate Auditable Artifacts:** Every agent transition produces persistent, structured artifacts (`spec.yml`, `code.patch`, `approval.json`, `test_red_team.py`, `test_report.json`, `health_report.json`, and `repair_N.patch`), guaranteeing full transparency.
3. **Concurrent Audit Stage:** Using a `ThreadPoolExecutor` concurrent runner, we demonstrate a 42% reduction in verification latency by executing static review and dynamic fuzzing concurrently.
4. **Closed-Loop Trace-Guided Self-Repair:** A bounded iterative feedback loop that consumes execution traces and failure diffs to generate surgical AST-level repairs.
5. **Standalone Pure-Python Engine & Empirical Evaluation:** A zero-dependency HTML5 parser achieving 100% pass rate across 139 unit tests, 100% crash-free resilience on 1,441 upstream W3C tests, and 100% survival against 15 adversarial attack vectors.
6. **Green AI & Caching Infrastructure:** Implementation of an on-disk SHA-256 response cache that reduces repeat evaluation costs to \$0.00 and latency to 0.00s.

## 1.4 Thesis Structure
The remainder of this dissertation is organized as follows:
* **Chapter 2 (Background & Related Work):** Reviews the WHATWG parsing standard, autonomous coding agents, LLM self-repair, and differential testing.
* **Chapter 3 (System Architecture):** Details the 7-agent assembly line, state transitions, and concurrency model.
* **Chapter 4 (Implementation):** Documents the pure-Python tokenizer FSM, streaming API, and telemetry harness.
* **Chapter 5 (Evaluation & Results):** Analyzes experimental data from W3C compliance, adversarial robustness, benchmarks, real-world sites, and ablation studies.
* **Chapter 6 (Discussion & Limitations):** Discusses the structural subset boundary vs the Adoption Agency Algorithm (AAA) and economic/carbon metrics.
* **Chapter 7 (Conclusion & Future Work):** Summarizes findings and outlines future extensions.
