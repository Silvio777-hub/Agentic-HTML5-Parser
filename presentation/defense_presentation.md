# MSc Thesis Defense Presentation
## Trustworthy HTML5 Parser Development via Agentic AI: A Multi-Agent, Self-Healing Pipeline
**Author:** Opoka JM Silvio  
**Degree:** MSc in Computer Science | Academic Year 2026/2027  
**Time Allotted:** 20 Minutes (15 min Presentation + 5 min Q&A)

---

## Slide 1: Title & Welcome (0:00 - 0:45)
- **Title:** Trustworthy HTML5 Parser Development via Agentic AI
- **Subtitle:** A Partially Ordered, Multi-Agent Assembly Line with Closed-Loop Self-Healing
- **Candidate:** Opoka JM Silvio
- **Department:** Computer Science & Artificial Intelligence
> **Speaker Notes:**
> "Good morning/afternoon, esteemed committee members. Today I am presenting my MSc research on developing trustworthy, resilient software components using autonomous multi-agent AI systems, applied specifically to the domain of HTML5 specification parsing."

---

## Slide 2: The Problem: Monolithic LLM Code Generation (0:45 - 1:45)
- Traditional LLM Code Generation ("Single Prompt Approach"):
  - **Context Drift:** Monolithic prompts lose track of subtle edge-case constraints.
  - **Silent Hallucination:** Generates syntactically plausible code that subtly violates specs.
  - **Lack of Auditability:** No intermediate artifacts; all-or-nothing black box.
  - **Brittleness:** Fails on adversarial inputs, circular references, and malformed structures.
> **Speaker Notes:**
> "If you ask a state-of-the-art LLM to 'write an HTML5 parser in Python', it produces a monolithic 300-line script that crashes on deeply nested tables, unclosed tags, or XSS vectors. There is no verification gating, no error diagnosis, and zero audit trail."

---

## Slide 3: The Target Domain: Why HTML5 Parsing? (1:45 - 2:45)
- HTML5 is **not** context-free (CFG); it cannot be parsed by standard LALR/Yacc grammars.
- W3C/WHATWG Specification requires:
  - 80+ distinct Tokenizer Finite State Machine states.
  - Complex tag closure rules (e.g., `<p>` implicitly closing before block elements).
  - Error recovery without crashing (graceful degradation).
- **Research Question:** *Can a multi-agent assembly line autonomously synthesize, verify, stress-test, and self-heal an HTML5 parser with verifiable guarantees?*
> **Speaker Notes:**
> "HTML5 parsing is uniquely suited as a rigorous benchmark for agentic AI because it combines formal state transitions with real-world messiness: web markup is notoriously malformed, yet standard parsers must never crash."

---

## Slide 4: Core Innovation: Partially Ordered 7-Agent Assembly Line (2:45 - 4:00)
- Division of Labor into Specialized Personas:
  1. `SpecAgentAI` (The Architect) $\rightarrow$ `spec.yml`
  2. `CodegenAgentAI` (Lead Implementer) $\rightarrow$ `code.patch`
  3. `CritiqueAgentAI` (Code Reviewer) $\rightarrow$ `approval.json`
  4. `RedTeamAgentAI` (Ethical Hacker) $\rightarrow$ `test_red_team.py`
  5. `TestAgentAI` (QA Conformance) $\rightarrow$ `test_report.json`
  6. `MonitorAgentAI` (DevOps Watchdog) $\rightarrow$ `health_report.json`
  7. `RepairAgentAI` (Auto-Debugger & Mechanic) $\rightarrow$ `repair_N.patch`
> **Speaker Notes:**
> "Rather than one giant prompt, we model software engineering as an assembly line. Every agent has a narrow contract and produces a persistent, auditable intermediate artifact."

---

## Slide 5: System Architecture Diagram (4:00 - 5:15)
```
Input Spec -> [1. SpecAgent] -> spec.yml
                     |
                     v
              [2. CodegenAgent] -> code.patch
                     |
        +------------+------------+ (ThreadPoolExecutor - 42% Speedup)
        |                         |
        v                         v
 [3. CritiqueAgent]        [4. RedTeamAgent]
   approval.json            test_red_team.py
        |                         |
        +------------+------------+
                     |
                     v
              [5. TestAgent] -> test_report.json
                     |
                     v
             [6. MonitorAgent] -> health_report.json
                     |
               [All Pass?]
               /         \
         YES /             \ NO (Failures)
            v               v
    SUCCESSFUL BUILD   [7. RepairAgent] -> repair_N.patch (Loop <= 3)
```
> **Speaker Notes:**
> "Notice two key architectural properties: First, Stage 3 is parallelized using ThreadPoolExecutor, cutting evaluation time by 42%. Second, the loop back from RepairAgent is bounded to at most 3 cycles to prevent infinite iteration divergence."

---

## Slide 6: Agent 1: SpecAgentAI (5:15 - 5:45)
- **Role:** The Architect.
- **Input:** Natural language subset request (e.g. paragraph implicit closure, void tags).
- **Output Artifact:** `spec.yml`.
- **Key Function:** Extracts formal FSM transition states and tag nesting constraints into machine-readable YAML.
> **Speaker Notes:**
> "SpecAgent acts as the translation layer between fuzzy human requirements and structured intermediate representations."

---

## Slide 7: Agent 2: CodegenAgentAI (5:45 - 6:15)
- **Role:** Lead Implementer.
- **Input:** `spec.yml` and existing parser code.
- **Output Artifact:** `code.patch` (Unified Diff).
- **Design Decision:** Generates standard unified diffs applicable via `git apply`, rather than full file overwrites.
> **Speaker Notes:**
> "By restricting Codegen to unified diffs, we ensure that existing working functionality is preserved and changes remain inspectable."

---

## Slide 8: Agents 3 & 4: Concurrent Critique & Red-Team (6:15 - 7:15)
- Dispatched simultaneously via `ThreadPoolExecutor`:
  - **CritiqueAgentAI:** Reviews code for PEP 8, banned functions (`eval`, `exec`), and spec fidelity. Produces `approval.json`.
  - **RedTeamAgentAI:** The ethical hacker. Generates 15 attack vectors (deep nesting, XSS injections, Unicode RTL, zero-width spaces). Produces `test_red_team.py`.
- **Empirical Speedup:** Reduces verification stage wall-clock time from 8.2s to 4.8s (42% speedup).
> **Speaker Notes:**
> "Critique looks for code hygiene, while Red-Team aggressively attempts to break the parser. Running them in parallel proves the efficiency of partially ordered agent workflows."

---

## Slide 9: Agents 5 & 6: Test & Monitor Gating (7:15 - 8:00)
- **TestAgentAI:** Programmatically runs `pytest` across unit, boundary, and red-team suites.
- **MonitorAgentAI:** Analyzes `parse_with_trace()` runtime execution data:
  - Memory consumption (KB).
  - Maximum AST recursion depth.
  - Per-stage latency (tokenizer vs parser).
- Produces `health_report.json` to gate production deployment.
> **Speaker Notes:**
> "Even if tests pass, MonitorAgent checks whether recursion depth spiked dangerously or if memory leaked. Quality gating goes beyond boolean pass/fail."

---

## Slide 10: Agent 7: Autonomous Self-Healing Loop (8:00 - 9:00)
- **RepairAgentAI:** Activated only when test or health failures occur.
- Consumes:
  1. Failed test assertion diffs.
  2. Runtime execution trace (failing token and FSM state).
  3. Active parser source code.
- Generates targeted `repair_N.patch`.
- Bounded to $\le 3$ iterations.
> **Speaker Notes:**
> "RepairAgent does not guess randomly. It acts like a senior debugger with the stack trace, the exact failing character, and the AST state."

---

## Slide 11: The Generated Artifact: Pure-Python HTML5 Engine (9:00 - 9:45)
- Handcrafted Pure-Python implementation with **zero runtime dependencies**:
  - `tokenize()`: Explicit FSM character-by-character scanner.
  - `parse()`: DOM tree constructor with LIFO stack closure.
  - `tokenize_stream()` & `parse_stream()`: Incremental generator API for streaming payloads.
  - CSS Query Engine: `.find()`, `.find_all()`, `.select()`, `.select_one()`.
  - Reverse HTML Emitter: `.to_html(pretty=True)`.
  - Plugin architecture: Hook lifecycle registry (`plugins/*/plugin.yml`).
> **Speaker Notes:**
> "The engine generated by this pipeline is production-grade, fully pure-Python, and requires zero external pip packages to parse HTML."

---

## Slide 12: Live Quality Dashboard Demo (9:45 - 11:00)
- Local HTTP Server & Playground (`scripts/serve_dashboard.py`):
  - **Tab 1: Compliance Suite:** W3C test table with modal DOM Tree Inspector.
  - **Tab 2: Parser Playground:** Live HTML parser with token streams & execution traces.
  - **Tab 3: Differential DOM Visualizer:** Compares AST side-by-side with BeautifulSoup4.
  - **Tab 4: Live Pytest Runner:** One-click real-time execution of all 139 tests.
> **Speaker Notes:**
> *[Switch to Browser on localhost:8080/dashboard/]*
> "Let me show you our Quality Dashboard. Here in Tab 2, I can input malformed markup and see the real-time token stream and latency. In Tab 3, we run differential verification against BeautifulSoup4. In Tab 4, we trigger the live test runner directly from the browser."

---

## Slide 13: Empirical Evaluation 1: Automated Unit Tests (11:00 - 11:45)
- Automated Test Suite:
  - **139 / 139 Tests Passing (100.0%)** across 9 comprehensive test files.
  - Coverage: Tokenizer FSM, tag attributes, implicit closure, entity decoding, DOM query API, streaming, error recovery, and plugin hooks.
  - Execution time: ~18.6 seconds total.
> **Speaker Notes:**
> "We maintain a 100% pass rate across 139 automated tests, including rigorous boundary testing."

---

## Slide 14: Empirical Evaluation 2: W3C Upstream Compliance (11:45 - 12:30)
- Evaluated against official W3C `html5lib-tests` (tree-construction suite):
  - **Total Tests Evaluated:** 1,441 test cases.
  - **Crash-Free Robustness:** **100.0% (1,441 / 1,441)** — Zero unhandled exceptions or segfaults.
  - **Structural Subset Strict Match:** Matches reference tree across structural element subsets.
> **Speaker Notes:**
> "When tested against over 1,400 upstream W3C test cases, the parser survived every single one without a crash or infinite hang."

---

## Slide 15: Empirical Evaluation 3: Adversarial Red-Team (12:30 - 13:00)
- 15 Malicious Attack Vectors:
  - Deep Nesting: 200–1000 nested tags (Zero stack overflow).
  - Implicit Cascade: `<p>1<p>2<p>3<div>End</div>` (Correct LIFO unwinding).
  - XSS Injection Vectors: `<script>` with embedded operators and unclosed tags.
  - Unicode RTL, Arabic, and zero-width spaces in tag names.
  - **Resilience Rate: 15/15 (100.0% Survival)**.
> **Speaker Notes:**
> "Our Red-Team agent probed every classic parser exploit vector. The engine survived 100% of these stress tests."

---

## Slide 16: Empirical Evaluation 4: Real-World Website Benchmark (13:00 - 13:30)
- Tested against 5 production website architectures:
  1. Wikipedia (Encyclopedic prose, infoboxes, complex tables).
  2. Hacker News (Deeply nested table layouts, vote buttons).
  3. Python Official Documentation (Code snippets, definition lists).
  4. GitHub Markdown Views (Badges, tables, task lists).
  5. MDN Web Docs (Modern HTML5 `<article>`, `<nav>`, `<aside>`).
- **Result:** 5/5 pages parsed with 100% crash-free execution and complete link/heading extraction.
> **Speaker Notes:**
> "To answer the supervisory question 'Does this work on real web pages?', we evaluated 5 major production sites with 100% success."

---

## Slide 17: Empirical Evaluation 5: Multi-Agent Ablation Study (13:30 - 14:00)
- What happens when we remove specific agents?
  - **Baseline (Full Pipeline):** 100% Unit, 100% Adversarial.
  - **Without CritiqueAgent:** Code quality score drops by 24%; subtle style regressions.
  - **Without RedTeamAgent:** Adversarial resilience drops from 100% to 68%.
  - **Without RepairAgent:** First-pass failure recovery drops to 0%.
- **Finding:** Every agent in the 7-agent assembly line contributes empirically to safety and correctness.
> **Speaker Notes:**
> "Ablation experiments prove that the multi-agent setup is not redundant overhead: removing RedTeam drops resilience to 68%, and removing Repair eliminates self-healing."

---

## Slide 18: Performance & Green AI: SHA-256 On-Disk Caching (14:00 - 14:30)
- Carbon & Economic Analysis:
  - Uncached LLM Pipeline: \$0.06 per run, ~8.2s latency, ~1.4 Joules.
  - Cached LLM Pipeline (SHA-256 key): **\$0.00 cost**, **0.00s latency**, **0.00g $CO_2$**.
  - Repeatability: Enables deterministic regression testing without hitting remote API rate limits.
> **Speaker Notes:**
> "We implemented an on-disk SHA-256 response cache. Repeat pipeline runs cost zero dollars and consume zero API tokens, addressing the Green AI challenge."

---

## Slide 19: Comparative Benchmark: Latency & Memory (14:30 - 14:45)
- Comparison vs BeautifulSoup4 (Python) and lxml (C-based):
  - Pure Python: Our parser achieves ~0.4ms average document parse latency.
  - Memory: Peak consumption remains under 2.5 MB for average documents.
  - C-extension trade-off: `lxml` is faster for massive 100MB files, but our parser requires zero compilation and zero C dependencies.
> **Speaker Notes:**
> "For pure-Python execution, our parser is extremely lightweight, keeping memory footprint minimal."

---

## Slide 20: Scope & Limitations: Structural Subset vs WHATWG AAA (14:45 - 15:15)
- Intellectual Honesty & Academic Scope:
  - **Implemented:** Structural subset (hierarchical tree, void elements, LIFO closure).
  - **Omitted (Identified Future Work):**
    - Adoption Agency Algorithm (AAA) (§13.2.6.4.7) for misnested inline formatting tags.
    - Table Foster Parenting.
    - Foreign Content XML namespaces (`<svg>`, `<math>`).
- Formally characterized in `tests/test_whatwg_boundary.py` and Chapter 6 of the thesis.
> **Speaker Notes:**
> "We deliberately scoped this project to an HTML5 structural subset. Rather than implementing the full 40-step Adoption Agency Algorithm, our parser resolves misnested tags cleanly via stack unwinding without crashes."

---

## Slide 21: Summary of Contributions (15:15 - 15:45)
1. **Partially Ordered Agent Pipeline:** Replaced black-box monolithic generation with an auditable 7-agent assembly line.
2. **Concurrent Verification Model:** Demonstrated a 42% speedup via parallel audit execution.
3. **Trace-Guided Self-Repair Loop:** Bounded iterative debugging with verifiable convergence.
4. **Standalone Pure-Python HTML5 Engine:** 139 tests, 1,441 W3C tests, 15/15 adversarial resilience.
5. **Interactive Verification Tooling:** 4-tab live Quality Dashboard, CLI runner, and Jupyter walkthrough.
> **Speaker Notes:**
> "In summary, we have demonstrated that agentic AI with structured intermediate artifacts and closed-loop feedback provides a viable, trustworthy paradigm for software engineering."

---

## Slide 22: Future Research Directions (15:45 - 16:00)
- Full WHATWG Adoption Agency Algorithm implementation via specialized Agentic FSM synthesis.
- Byzantine Multi-Model Consensus: Voting across Anthropic Claude, OpenAI GPT-4o, and Google Gemini.
- Real-time streaming self-repair in memory during socket reception.
> **Speaker Notes:**
> "Future extensions will scale this architecture to full WHATWG compliance and multi-model consensus voting."

---

## Slide 23: Conclusion (16:00)
- **Takeaway:** Trustworthy AI code generation requires structure, division of labor, adversarial testing, and closed-loop self-repair.
- **Repository:** https://github.com/Silvio777-hub/Agentic-HTML5-Parser
- **Thank you!** I welcome your questions and feedback.
> **Speaker Notes:**
> "Thank you for your time and attention. I am now open to your questions."

---

## Slide 24: Defense Backup: Viva Anticipated Questions & Answers (Q&A)
- **Q: Why not use a single prompt with few-shot examples?**
  *A:* Single prompts lack intermediate verification gates. When an error occurs in a 500-line output, the LLM cannot pinpoint the root cause without execution telemetry.
- **Q: How do you prevent the repair loop from diverging or hallucinating?**
  *A:* The loop is strictly bounded to 3 iterations, and every patch is verified against the entire regression test suite before acceptance.
- **Q: Why does your parser not implement the Adoption Agency Algorithm?**
  *A:* AAA requires cloning active formatting elements across tree boundaries. In Chapter 6, we analyze this boundary: our structural subset avoids AST bloat while guaranteeing 100% crash-free execution.

---

## Slide 25: Defense Backup: Live Terminal Quick Reference
- `python cli.py test` $\rightarrow$ 139 unit tests
- `python cli.py dashboard` $\rightarrow$ Web GUI at `localhost:8080/dashboard/`
- `python cli.py compliance` $\rightarrow$ W3C compliance runner
- `python cli.py adversarial` $\rightarrow$ Red-team exploit suite
- `python cli.py realworld` $\rightarrow$ 5 production web pages
- `python cli.py repair-demo` $\rightarrow$ Live self-repair demonstration
