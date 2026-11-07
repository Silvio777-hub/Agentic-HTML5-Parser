# Agentic AI HTML5 Parser â€” Complete Implementation Guide

> **Author:** Opoka JM Silvio | **Degree:** MSc Computer Science | **Academic Year:** 2026/2027
> **Python:** 3.9+ (tested on 3.11 and 3.13) | **Model:** Claude 3.5 Sonnet | **Port:** 8080 (default)

[![CI Pipeline](https://github.com/Silvio777-hub/Agentic-HTML5-Parser/actions/workflows/ci.yml/badge.svg)](https://github.com/Silvio777-hub/Agentic-HTML5-Parser/actions/workflows/ci.yml)

---

## âš¡ Quick Start

```bash
git clone https://github.com/Silvio777-hub/Agentic-HTML5-Parser.git
cd Agentic-HTML5-Parser
pip install -r requirements.txt
python cli.py test          # 207/207 unit tests
python cli.py adversarial   # 15/15 attack vectors
python cli.py compliance    # W3C compliance suite
python cli.py repl          # Interactive terminal REPL with live telemetry & security scan
python cli.py dashboard     # Live DOM Inspector at http://localhost:8080/dashboard/
```

â†’ See [quickstart.md](quickstart.md) for full setup instructions including the LLM pipeline.

---

## ðŸ“Š Key Results

| Metric | Result |
|---|---|
| Automated Tests | âœ… **207/207 passed** |
| Adversarial Resilience | âœ… **15/15 (100%)** |
| W3C Upstream Robustness | âœ… **1,441/1,441 (100%)** (459 strict matches, 31.85%) |
| W3C 6-Bucket Functional Matrix | âœ… **31/31 (100%)** |
| Parallel Stage Speedup | **~42% wall-clock reduction** (Critique + Red-Team concurrent) |
| Self-Repair Loops | **3 iterations max** â€” automated trace-guided patching |
| Parser Benchmark vs BeautifulSoup4 | **352 ms/doc** vs 237 ms/doc (pure Python, no C extensions) |
| Parser Benchmark vs lxml (C) | 83Ã— slower â€” expected; lxml uses native C code |

---

## Project Overview

This project implements a **trustworthy HTML5 parser development pipeline** using **agentic AI** (Claude 3.5 Sonnet). The system orchestrates **7 specialized AI agents** that collaboratively design, implement, test, and self-repair an HTML5 parser component â€” benchmarked against BeautifulSoup4 and lxml, validated against the W3C `html5lib` official test suite.

### Key Innovation: Artifact-Based Agentic Assembly Line

Rather than treating AI as a black-box code generator, this system:
- Breaks development into **discrete AI-assisted stages** (Spec â†’ Code â†’ Review â†’ Test â†’ Attack â†’ Monitor â†’ Repair)
- Uses **intermediate artifacts** (specs, patches, tests) for full transparency and auditability
- Implements **iterative self-repair loops** driven by real execution traces and test failures
- Achieves **100% crash-free robustness** on 1,441 upstream W3C html5lib tests (459/1,441 strict tree matches, 31.85%), **100% adversarial resilience** (15/15 attack vectors), and **100% functional matrix** (31/31 buckets)
- Employs **concurrency via ThreadPoolExecutor** for independent agent evaluations (Critique & Red-Team)
- Provides a **live interactive web dashboard** with DOM Tree Inspector at `http://localhost:8080/dashboard/`

> âš ï¸ **Scope Note:** The parser implements an HTML5 structural subset. Full WHATWG spec compliance (adoption agency algorithm, full foster parenting, foreign content) is identified as future work. See [architecture.md](architecture.md) for scope details.

> ðŸ“ **Architecture Reference:** See [architecture.md](architecture.md) for full system diagrams, concurrency specifications, and agent contracts.

---

## 7 Core AI Agents

### 1. SpecAgentAI â€” The Architect (`src/claude_integration.py`)
**Responsibility:** Reads the W3C HTML5 specification and converts complex rules into a structured engineering blueprint.

**Input:**
- Human-written HTML5 subset description
- Parser interface contract

**Output:**
- `spec.yml` â€” YAML specification containing tokenizer states, parsing rules, implicit tag closure behaviours, and expected test cases

```yaml
# Example spec.yml output
name: HTML5 Parser Subset
version: 0.1.0
tokenizer_states:
  DATA: "Reading normal character data"
  TAG_OPEN: "After encountering '<'"
  TAG_NAME: "Reading tag name"
parsing_rules:
  p:
    closes_before: [div, blockquote, section]
    can_contain: [inline, text]
test_cases:
  - html: "<p>Test<div>Block</div>"
    expect_closure: "p closes before div"
```

---

### 2. CodegenAgentAI â€” The Lead Coder (`src/claude_integration.py`)
**Responsibility:** Translates the specification blueprint into clean, compliant Python parsing code.

**Input:**
- YAML specification from SpecAgentAI
- Current parser implementation
- List of features to implement

**Output:**
- `code.patch` â€” Unified diff patch with tokenizer enhancements, tree construction logic, implicit closure handling, and inline documentation

---

### 3. CritiqueAgentAI â€” The Code Reviewer (`src/claude_integration.py`)
**Responsibility:** Reviews generated code against the specification for quality, performance, and style.

**Input:**
- Generated patch from CodegenAgentAI
- Original specification
- Test execution results

**Output:**
- Approval decision (approve/reject)
- Issues found (if any)
- Confidence score (0â€“100%)
- Improvement recommendations

**Runs in parallel** with RedTeamAgentAI via `ThreadPoolExecutor` (â‰ˆ42% wall-clock speedup).

---

### 4. TestAgentAI â€” The QA Engineer (`src/claude_integration.py`)
**Responsibility:** Runs the official W3C `html5lib-tests` compliance suite and reports exact failure diffs.

**Input:**
- YAML specification
- Parser interface documentation

**Output:**
- `test_parser.py` â€” pytest test suite covering tokenization, tree construction, implicit closure, edge cases, with docstrings

**Test Coverage:**
- âœ“ Basic functionality
- âœ“ Attribute parsing
- âœ“ Nested structures
- âœ“ Self-closing tags
- âœ“ Error handling

---

### 5. RedTeamAgentAI â€” The Ethical Hacker (`src/claude_integration.py`)
**Responsibility:** Attacks the parser with 15 adversarial, malicious, and malformed HTML inputs.

**Input:**
- Parser interface
- Known vulnerability patterns

**Output:**
- `test_red_team.py` â€” adversarial test suite including deeply nested structures (200+ levels), script injection, unclosed tags, long attributes (5000 chars), Unicode/emoji, zero-width spaces

**Result: 100% Resilience Rate (15/15 attacks survived)**

---

### 6. MonitorAgentAI â€” The DevOps Safety Watchdog (`src/claude_integration.py`)
**Responsibility:** Watches parser execution traces for anomalies â€” memory spikes, timeout violations, infinite loops.

**Input:**
- Parser execution traces (from `parse_with_trace()`)
- Performance metrics (timing, memory, recursion depth)

**Output:**
- Health assessment (healthy/unhealthy)
- Identified bottlenecks
- Recommendations

**Monitoring Points:**
- âœ“ Recursion depth violations
- âœ“ Memory exhaustion
- âœ“ Timeout violations (< 50ms target)
- âœ“ Inefficient algorithms
- âœ“ State machine errors

---

### 7. RepairAgentAI â€” The Master Mechanic (`src/claude_integration.py`)
**Responsibility:** Analyses failing test traces and autonomously writes unified `.patch` diffs to self-heal bugs.

**Input:**
- Failing test names and error messages
- Execution trace showing failure point
- Current implementation

**Output:**
- `repair_N.patch` â€” Targeted fix with root-cause analysis, minimal changes, explanatory comments

**Repair Strategy:**
- Analyse failing test evidence
- Identify root cause from trace
- Generate minimal, focused patch
- Hard cap: **3 repair iterations max** (prevents infinite loops)

---

## Pipeline Workflow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Human-defined HTML5 Subset + Interface     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚  SpecAgentAI    â”‚  â†’ spec.yml
            â”‚ (Architect)     â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚ CodegenAgentAI  â”‚  â†’ code.patch
            â”‚ (Lead Coder)    â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â† Parallel via ThreadPoolExecutor
          â–¼                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ CritiqueAgentAI â”‚   â”‚ RedTeamAgentAI  â”‚
â”‚ (Code Reviewer) â”‚   â”‚ (Ethical Hacker)â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â–¼
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚  TestAgentAI    â”‚  â†’ test_report.json
            â”‚  (QA Engineer)  â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â–¼
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚ MonitorAgentAI  â”‚  â†’ health report
            â”‚  (Watchdog)     â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
         â”‚    Tests Passed?      â”‚â”€â”€NOâ”€â”€â”
         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â”‚
                     â”‚ YES              â–¼
                     â–¼       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚  RepairAgentAI  â”‚ â†’ repair_N.patch
              â”‚ SUCCESS  â”‚   â”‚  (Mechanic)     â”‚ (max 3 iterations)
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                      â”‚
                              â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                              â”‚ Re-run tests   â”‚
                              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Complete Project Structure

```
Agentic AI HTML5 Parser/
â”‚
â”œâ”€â”€ src/                            â† CORE ENGINE & AGENT LOGIC
â”‚   â”œâ”€â”€ parser.py                   # Pure-Python HTML5 Tokenizer (FSM), DOM Tree builder & Streaming API
â”‚   â”œâ”€â”€ claude_integration.py       # All 7 Claude-powered AI Agent classes
â”‚   â”œâ”€â”€ cache.py                    # SHA-256 On-Disk ResponseCache ($0.00 repeat cost, 0.00s latency on hit)
â”‚   â”œâ”€â”€ parallel_runner.py          # ThreadPoolExecutor parallel dispatcher (42% speedup)
â”‚   â”œâ”€â”€ llm_provider.py             # Multi-model abstraction (Claude 3.5, GPT-4o, local Ollama, Mock)
â”‚   â”œâ”€â”€ plugin_manager.py           # Plugin loader and hook dispatcher
â”‚   â””â”€â”€ utils.py                    # ArtifactManager, PatchManager, ReportGenerator
â”‚
â”œâ”€â”€ scripts/                        â† AUTOMATION, BENCHMARKS & RESEARCH TOOLS
â”‚   â”œâ”€â”€ serve_dashboard.py          # HTTP server + Live POST /api/parse REST endpoint
â”‚   â”œâ”€â”€ run_compliance.py           # W3C html5lib-tests compliance runner
â”‚   â”œâ”€â”€ run_upstream_matrix.py      # 6-bucket functional matrix across 1,441 upstream tests
â”‚   â”œâ”€â”€ setup_upstream_tests.py     # 1-click downloader for 1,000+ W3C tests
â”‚   â”œâ”€â”€ compare_benchmarks.py       # Latency & memory benchmark vs BeautifulSoup4, html5lib, lxml
â”‚   â”œâ”€â”€ run_adversarial.py          # 15 red-team attack vectors (100% resilience)
â”‚   â”œâ”€â”€ run_ablation_study.py       # Empirical ablation: proves each agent's contribution
â”‚   â”œâ”€â”€ generate_thesis_charts.py   # Auto-generates 7 publication-ready 300-DPI figures
â”‚   â”œâ”€â”€ eval_real_world_pages.py    # 12-site real-world corpus evaluation (1991â€“2026)
â”‚   â”œâ”€â”€ estimate_carbon.py          # Green AI energy consumption & CO2 calculator
â”‚   â”œâ”€â”€ repair_pattern_mining.py    # Statistical failure taxonomy miner
â”‚   â”œâ”€â”€ demo_self_repair.py         # Live self-healing demo (inject bug â†’ auto-patch)
â”‚   â”œâ”€â”€ run_security_audit.py       # AST static scanner + 6-point STRIDE threat model
â”‚   â”œâ”€â”€ compile_thesis_docx.py      # Compiles all thesis chapters into Master_Thesis_Silvio.docx (local only)
â”‚   â”œâ”€â”€ generate_future_docx.py     # Generates Future Works research roadmap document (local only)
â”‚   â””â”€â”€ generate_viva_docx.py       # Generates VIVA.docx oral defense master Q&A guide (local only)
â”‚
â”œâ”€â”€ dashboard/                      â† INTERACTIVE 5-TAB WEB DASHBOARD
â”‚   â””â”€â”€ index.html                  # Bootstrap 5: Compliance Â· Benchmark Â· Adversarial Â· Ablation Â· Real-World
â”‚
â”œâ”€â”€ tests/                          â† AUTOMATED TEST SUITE (207 tests, 100% passing)
â”‚   â”œâ”€â”€ conftest.py                 # Shared pytest fixtures
â”‚   â”œâ”€â”€ test_agent_pipeline_offline.py # Offline integration tests for all 7 Claude agents
â”‚   â”œâ”€â”€ test_integration.py         # 32 tests: Tokenizer, Parser, Implicit Closure, Traces, Edge Cases
â”‚   â”œâ”€â”€ test_streaming.py           # 2 tests: tokenize_stream() and parse_stream() generators
â”‚   â”œâ”€â”€ test_dom_query_and_html_emitter.py  # DOM query API & HTML serializer
â”‚   â”œâ”€â”€ test_entity_decoding.py     # HTML entity decoding (named, numeric, hex)
â”‚   â”œâ”€â”€ test_new_features.py        # Plugin system, Multi-LLM provider, Parallel runner
â”‚   â”œâ”€â”€ test_ollama_provider.py     # Ollama local LLM provider tests
â”‚   â”œâ”€â”€ test_parallel_and_utils.py  # ThreadPool concurrency, ArtifactManager, PatchManager
â”‚   â”œâ”€â”€ test_rawtext_and_comments.py # Raw text elements (script/style) & comment nodes
â”‚   â””â”€â”€ test_whatwg_boundary.py     # WHATWG boundary conditions & edge cases
â”‚
â”œâ”€â”€ data/                           â† EXPERIMENTAL RESULTS & AUDIT ARTIFACTS
â”‚   â”œâ”€â”€ sample_compliance_tests.dat # 10 bundled W3C test cases in official .dat format
â”‚   â”œâ”€â”€ tests1.dat                  # Additional W3C tree-construction test cases
â”‚   â”œâ”€â”€ compliance_results.json     # W3C upstream compliance results (1,441 tests, 100% robustness)
â”‚   â”œâ”€â”€ upstream_matrix_report.json # 6-bucket functional matrix report (31/31 passes)
â”‚   â”œâ”€â”€ real_world_results.json     # 12-site real-world corpus results (100% parse success)
â”‚   â”œâ”€â”€ benchmark_results.json      # Latency, throughput, peak memory benchmarks
â”‚   â”œâ”€â”€ adversarial_results.json    # Red-team stress test results (15/15 passed)
â”‚   â”œâ”€â”€ ablation_study_results.json # Multi-agent contribution experiment results
â”‚   â”œâ”€â”€ repair_patterns_analysis.json # Statistical distribution of recurring failure modes
â”‚   â”œâ”€â”€ carbon_footprint_report.json  # Green AI energy & CO2 measurements
â”‚   â”œâ”€â”€ security_audit_report.json    # AST code scan findings & STRIDE matrix
â”‚   â””â”€â”€ self_repair_demo_result.json  # Audit trail of live self-healing run
â”‚
â”œâ”€â”€ figures/                        â† 7 Ã— 300-DPI PUBLICATION FIGURES
â”‚   â”œâ”€â”€ 01_latency_vs_parsers.png          # Comparative latency bar chart (our parser vs BS4, lxml)
â”‚   â”œâ”€â”€ 02_memory_consumption.png          # Peak memory comparison across parsers
â”‚   â”œâ”€â”€ 03_repair_pattern_distribution.png # Error taxonomy pie chart (self-repair loop)
â”‚   â”œâ”€â”€ 04_parallel_speedup.png            # ThreadPool 42% wall-clock speedup demonstration
â”‚   â”œâ”€â”€ 05_ablation_comparison.png         # Per-agent ablation comparison (7-agent vs subsets)
â”‚   â”œâ”€â”€ 06_w3c_compliance_progression.png  # W3C match progression: 0% â†’ 31.85% over iterations
â”‚   â””â”€â”€ 07_real_world_corpus_profile.png   # 12-site real-world corpus parse success profile
â”‚
â”œâ”€â”€ presentation/                   â† THESIS DEFENSE MATERIALS
â”‚   â”œâ”€â”€ defense_presentation.md     # 25-slide Markdown deck with speaker notes
â”‚   â”œâ”€â”€ defense_qa_prep.md          # Viva voce cheat sheet â€” 25 likely examiner questions + answers
â”‚   â””â”€â”€ slides.html                 # Interactive 17-slide HTML5 defense deck (open in any browser)
â”‚
â”œâ”€â”€ plugins/example_lint/           â† PLUGIN SYSTEM EXAMPLE
â”‚   â”œâ”€â”€ plugin.yml                  # Plugin manifest (name, version, hook points)
â”‚   â””â”€â”€ lint_rule.py                # Example lint rule demonstrating the plugin API
â”‚
â”œâ”€â”€ cache/                          â† SHA-256 RESPONSE CACHE
â”‚   â””â”€â”€ .gitkeep                    # Cached LLM responses stored here (replay = $0.00, 0.00s latency)
â”‚
â”œâ”€â”€ .github/workflows/ci.yml        â† GITHUB ACTIONS CI/CD PIPELINE
â”‚
â”œâ”€â”€ cli.py                          # Master CLI (one command to run everything)
â”œâ”€â”€ orchestrator.py                 # Full pipeline orchestrator with 3-iteration repair loop
â”œâ”€â”€ config.py                       # Configuration: API keys, model names, paths
â”œâ”€â”€ Dockerfile                      # Multi-stage Python container
â”œâ”€â”€ docker-compose.yml              # Docker Compose (port 8080)
â”œâ”€â”€ pyproject.toml                  # PEP 517/518 project metadata & pytest configuration
â”œâ”€â”€ requirements.txt                # Python dependencies
â”œâ”€â”€ architecture.md                 # Full system diagrams, concurrency specs, agent contracts
â”œâ”€â”€ quickstart.md                   # Step-by-step setup guide including LLM pipeline
â”œâ”€â”€ CONTRIBUTING.md                 # Contribution guidelines
â”œâ”€â”€ demo_walkthrough.ipynb          # Interactive Jupyter notebook walkthrough
â”œâ”€â”€ .env.example                    # API key template â€” copy to .env and fill in keys
â””â”€â”€ README.md                       # This file
```


---

## ðŸ”‘ Environment Setup (API Keys)

### Step 1 â€” Copy the environment template

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

### Step 2 â€” Edit `.env` and add your keys

Open `.env` in any text editor and fill in:
```env
# Required: Claude AI (SpecAgentAI, CodegenAgentAI, etc.)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Optional: GPT-4o fallback model support
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE

# Optional: Local Ollama (runs Llama 3 locally, no API cost)
OLLAMA_BASE_URL=http://localhost:11434
```

> **Where to get your Anthropic key:** https://console.anthropic.com
> **Note:** The pipeline works **without an API key** in Mock mode for local testing.

### Step 3 â€” Verify configuration

```powershell
python config.py
```
Expected output: `All directories created successfully.`

---

## âš™ï¸ Installation and Setup

### Prerequisites
- Python 3.9+ (tested on **3.11** and **3.13**)
- Docker Desktop (optional, for containerised deployment)
- Git

### Install Python Dependencies

```powershell
pip install -r requirements.txt
pip install matplotlib python-docx
```

### Verify All Packages Are Installed

```powershell
python -c "import anthropic, lxml, pytest, matplotlib, docx; print('[OK] All core packages present')"
```

### Quick Parser Smoke Test

```powershell
python -c "from src.parser import parse; t = parse('<p>Hello<div>World</div>'); print('[OK] Parser working, root node:', t.name)"
```

---

## ðŸš€ Running the Project

### Option A â€” Run Directly with Python (Recommended)

#### Step 1: Start the Live Dashboard & API Server
```powershell
python scripts/serve_dashboard.py --no-browser --port 8080
```

Then open: **http://localhost:8080/dashboard/**

> **Note:** Port 8080 or 8081 may be occupied by other services on your machine.
> Use `--port 8090` (or any other free port).

#### Verify the server is listening
```powershell
netstat -ano | findstr ":8080"
```
Expected output: `TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING`

---

### Option B â€” Run with Docker

#### Step 1: Build and start the container (first run downloads ~500MB)
```powershell
docker compose up -d --build
```

#### Step 2: Confirm container is running
```powershell
docker ps --filter "name=agentic_html5_parser_dashboard"
```

#### Step 3: Stream live container logs
```powershell
docker compose logs -f
```

#### Step 4: Stop the container
```powershell
docker compose down
```

#### Rebuild after code changes (uses cached layers â€” much faster)
```powershell
docker compose up -d --build
```

> **Port conflict?** If port 8080 is occupied (another container/service), edit
> `docker-compose.yml` line 16 and change `"8080:8080"` â†’ `"8082:8080"`,
> then run `docker compose up -d`.

> **Slow first build?** Docker downloads the Python 3.11-slim base image (~200MB)
> and all pip packages on first run. Subsequent builds use the layer cache and
> complete in under 30 seconds.

---

## ðŸ§ª Running the Automated Test Suite

### Run All 207 Tests
```powershell
python -m pytest tests/ -v
```
Expected: `207 passed in ~80s`

### Run with Coverage Report (creates `htmlcov/index.html`)
```powershell
python -m pytest tests/ --cov=src --cov-report=html -v
```

### Run Only Integration Tests (32 tests)
```powershell
python -m pytest tests/test_integration.py -v
```

### Run Only Streaming Tests (2 tests)
```powershell
python -m pytest tests/test_streaming.py -v
```

### Run Tests with Short Summary (quick check)
```powershell
python -m pytest tests/ -q
```

---

## ðŸŽ›ï¸ Master CLI â€” All Commands

The [`cli.py`](cli.py) is your single command-centre for the entire project:

```powershell
# Run EVERYTHING: tests, benchmarks, adversarial, ablation, charts, carbon, audit
python cli.py all

# Start the live interactive dashboard & API server
python cli.py dashboard

# Run W3C html5lib compliance suite (10 sample tests bundled)
python cli.py compliance

# Benchmark: compare latency & memory vs BeautifulSoup4, html5lib, lxml
python cli.py benchmark

# Adversarial: 15 red-team attack vectors (100% resilience expected)
python cli.py adversarial

# Ablation study: measure parser quality with each agent individually removed
python cli.py ablation

# Generate all 7 publication-ready 300-DPI figures into figures/
python cli.py charts

# Estimate computational carbon footprint & energy in Joules (Green AI)
python cli.py carbon

# Static security audit: AST scanner + 6-point STRIDE threat model check
python cli.py audit

# Live self-healing demo: inject a bug â†’ watch it auto-patch itself
python cli.py repair-demo

# Compile thesis to DOCX (local only â€” thesis/ folder is gitignored)
python scripts/compile_thesis_docx.py
```

---

## ðŸ“Š Individual Research & Experiment Scripts

Run any experiment directly without the CLI wrapper:

```powershell
# W3C Compliance: run bundled sample tests
python scripts/run_compliance.py --sample

# W3C 6-Bucket Functional Matrix: test all 31 parser capability categories
python scripts/run_upstream_matrix.py

# Real-World Corpus: parse 12 historical websites (1991â€“2026)
python scripts/eval_real_world_pages.py

# Download the FULL W3C upstream test suite (1,000+ official tests)
python scripts/setup_upstream_tests.py

# Benchmark: latency, throughput, peak memory vs BeautifulSoup4 & lxml
python scripts/compare_benchmarks.py

# Adversarial: 15 red-team attack vectors with detailed pass/fail per vector
python scripts/run_adversarial.py

# Ablation: empirical proof of each agent's individual contribution
python scripts/run_ablation_study.py

# Charts: generate all 7 publication-ready figures (saves to figures/)
python scripts/generate_thesis_charts.py

# Carbon: Green AI energy & CO2 footprint calculation
python scripts/estimate_carbon.py

# Security: AST static scan + STRIDE threat model validation
python scripts/run_security_audit.py

# Repair patterns: mine and classify recurring failure modes statistically
python scripts/repair_pattern_mining.py

# Self-repair demo: intentionally break the parser â†’ watch it self-heal
python scripts/demo_self_repair.py
```

---

## ðŸ“ Where to Find All Results

After running experiments, all outputs are auto-saved:

| Output File | Location | Generated By |
|---|---|---|
| W3C compliance results | `data/compliance_results.json` | `python cli.py compliance` |
| Benchmark results | `data/benchmark_results.json` | `python cli.py benchmark` |
| Adversarial results | `data/adversarial_results.json` | `python cli.py adversarial` |
| Ablation study results | `data/ablation_study_results.json` | `python cli.py ablation` |
| Carbon footprint report | `data/carbon_footprint_report.json` | `python cli.py carbon` |
| Security audit report | `data/security_audit_report.json` | `python cli.py audit` |
| Self-repair demo result | `data/self_repair_demo_result.json` | `python cli.py repair-demo` |
| Repair patterns analysis | `data/repair_patterns_analysis.json` | `scripts/repair_pattern_mining.py` |
| Publication figures (7 PNGs) | `figures/` | `python cli.py charts` |
| LLM response cache | `cache/*.json` | Automatic on every LLM call |
| Test coverage HTML | `htmlcov/index.html` | `pytest --cov=src --cov-report=html` |

### Reading results on Windows (PowerShell)
```powershell
# View compliance results
Get-Content data\compliance_results.json

# View benchmark results
Get-Content data\benchmark_results.json

# View latest pipeline report (replace <run_id> with actual folder name)
Get-ChildItem runs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content runs\<run_id>\reports\pipeline_report.json
```

---

## ðŸŒ Live Dashboard URLs

| URL | Description |
|---|---|
| `http://localhost:8080/dashboard/` | Main dashboard: compliance panels, benchmark charts, DOM Inspector |
| `POST http://localhost:8080/api/parse` | REST API: send HTML, receive parsed DOM tree + trace |

### Test the REST API from PowerShell
```powershell
$body = '{"html": "<p>Hello <b>World</b></p>"}'
Invoke-WebRequest -Uri "http://localhost:8080/api/parse" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -ExpandProperty Content
```

---

## ðŸ” Diagnostic Commands

```powershell
# Check which ports are currently in use
netstat -ano | findstr ":8080"
netstat -ano | findstr ":8080"

# Check all running Docker containers and their port bindings
docker ps -a

# Check Docker and Compose versions
docker --version
docker compose version

# Verify Python packages installed correctly
python -c "import anthropic, lxml, pytest, matplotlib, docx; print('[OK] All core packages present')"

# Quick parser smoke test (TreeNode uses .name not .tag)
python -c "from src.parser import parse; t = parse('<p>Hello<div>World</div>'); print('[OK] Root node name:', t.name)"

# Quick tokenizer test
python -c "from src.parser import tokenize; tokens = tokenize('<p class=\"x\">Hi</p>'); print('[OK] Tokens:', len(tokens))"

# Check cache is working (run twice â€” second call should show 0.00s latency)
python -c "from src.cache import ResponseCache; c = ResponseCache(); print('[OK] Cache dir:', c.cache_dir)"

# Verify the streaming API works
python -c "from src.parser import tokenize_stream; tokens = list(tokenize_stream('<p>Test</p>')); print('[OK] Streamed tokens:', len(tokens))"
```

---

## ðŸ” CI/CD Pipeline (GitHub Actions)

The project includes a full automated CI pipeline at [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

On every push and pull request, it automatically:
1. Installs all dependencies
2. Runs linting with `flake8`
3. Executes all 207 pytest tests across 10 test files
4. Generates a code coverage report

To check CI status locally before pushing:
```powershell
# Lint check
python -m flake8 src/ --max-line-length=120

# Full test run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

---

## ðŸ’¡ Using the Parser in Your Own Code

```python
from src.parser import tokenize, parse, parse_with_trace

html = "<p>Hello<div>World</div></p>"

# 1. Tokenization only
tokens = tokenize(html)
for token in tokens:
    print(token)

# 2. Full parse â†’ returns TreeNode (use .name not .tag)
tree = parse(html)
print("Root node:", tree.name)          # e.g. "document"
print("Children:", tree.children)
print("Serialized:", tree.serialize())

# 3. Parse with execution trace (for monitoring and repair)
result = parse_with_trace(html)
print("Trace events:", len(result['trace']['events']))
print("Duration:", result['trace']['duration'], "s")
print("DOM tree:", result['dom_tree'])

# 4. Streaming API (memory-efficient for large documents)
from src.parser import tokenize_stream, parse_stream
for token in tokenize_stream(html):
    print("Stream token:", token)
```

---

## ðŸ¤– Running Individual AI Agents

```python
from src.claude_integration import SpecAgentAI, CodegenAgentAI, RepairAgentAI

# Generate a specification
spec_agent = SpecAgentAI()
spec_yaml = spec_agent.generate_specification(
    html_subset="<p>, <div>, implicit closure",
    parser_interface="tokenize() and parse()"
)
print(spec_yaml)

# Run the full pipeline orchestrator
from orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
report = orchestrator.run(
    html_subset="<p>, <div>, <section>, implicit tag closure",
    parser_interface="tokenize(html), parse(html), parse_with_trace(html)"
)
print("Status:", report['status'])
print("Run ID:", report['run_id'])
```

---

## ðŸ”¬ Key Technical Results

| Metric | Result |
|---|---|
| Automated tests passing | **207 / 207 (100%)** |
| W3C html5lib upstream robustness | **1,441 / 1,441 tests (100%)** |
| W3C strict tree equivalence | **459 / 1,441 tests (31.85%)** |
| W3C 6-bucket functional matrix | **31 / 31 tests (100%)** |
| Adversarial resilience rate | **15/15 attack vectors (100%)** |
| LLM response cache hit cost | **\$0.00 / 0.00s latency** |
| Parallel agent speedup | **~42% wall-clock reduction** |
| Max repair iterations (safety cap) | **3 iterations** |
| Dashboard API latency | **< 50ms per parse** |
| Supported LLM providers | **3 (Claude, GPT-4o, Ollama)** |

---

## ðŸ› ï¸ Troubleshooting

### "ANTHROPIC_API_KEY not set"
1. Get your key from https://console.anthropic.com
2. Create `.env`: `Copy-Item .env.example .env`
3. Edit `.env` and add: `ANTHROPIC_API_KEY=sk-ant-...`
4. Verify: `python config.py`

### "ModuleNotFoundError"
```powershell
pip install -r requirements.txt
pip install matplotlib python-docx
python -c "import anthropic; print('OK')"
```

### Port already in use (OSError: [WinError 10048])
```powershell
# Find which process is using port 8080
netstat -ano | findstr ":8080"
# Start on a different port instead
python scripts/serve_dashboard.py --no-browser --port 8090
```

### Docker build stuck on "exporting layers"
This is a known Windows Docker Desktop issue with large images (numpy/matplotlib).
**Solution:** Run directly with Python instead:
```powershell
pip install -r requirements.txt
pip install matplotlib python-docx
python scripts/serve_dashboard.py --no-browser --port 8080
```

### TreeNode AttributeError: 'TreeNode' has no attribute 'tag'
The node attribute is **`.name`**, not `.tag`:
```python
# WRONG âŒ
tree.tag

# CORRECT âœ…
tree.name
```

### Slow AI agent responses
- Use the **Mock provider** for local testing (no API key needed): set `LLM_PROVIDER=mock` in `.env`
- Reduce `MAX_TOKENS` in `config.py`
- The **response cache** in `cache/` means repeated identical prompts cost \$0.00

---

## ðŸ” Security Considerations

1. **API Key Protection:** Never commit `.env` to version control (it is in `.gitignore`)
2. **Input Validation:** Parser validates and sanitises all HTML before processing
3. **Resource Limits:** Robustness Wrapper enforces timeout (50ms) and memory caps
4. **Bounded Repair Loop:** Hard cap of 3 iterations prevents infinite LLM loops
5. **Static Analysis:** `run_security_audit.py` performs AST-level vulnerability scanning
6. **STRIDE Threat Model:** 6-point threat model validated against the full pipeline

---

## ðŸ“š Academic & Technical References

### Standards & Specifications
- **WHATWG:** [HTML Living Standard](https://html.spec.whatwg.org/) â€” Section 8: Parsing HTML documents, tokenisation state machine, and tree construction dispatch.
- **W3C:** [html5lib-tests Official Test Suite](https://github.com/html5lib/html5lib-tests) â€” Conformance test vectors covering tokenizer states, tree construction, and entity decoding.
- **RFC 8259:** [The JavaScript Object Notation (JSON) Data Interchange Format](https://tools.ietf.org/html/rfc8259) â€” Standard for intermediate AST and execution trace serialization.

### Software Architecture & Compiler Engineering
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
- McKeeman, W. M. (1998). *Differential Testing for Software*. Digital Technical Journal, 10(1), 100â€“107.
- Angluin, D. (1987). *Learning regular sets from queries and counterexamples*. Information and Computation, 75(2), 87â€“106.

### Agentic AI & Automated Program Repair
- Anthropic. (2024). *The Claude 3.5 Sonnet Model Card and API Technical Specification*. Anthropic PBC.
- Schwartz, R., Dodge, J., Smith, N. A., & Etzioni, O. (2020). *Green AI*. Communications of the ACM, 63(12), 54â€“63.
- Monperrus, M. (2018). *Automatic software repair: a bibliography*. ACM Computing Surveys (CSUR), 51(1), 1â€“24.

### Benchmark Baselines & Industrial Parsers
- Leonard, R. (2023). *Beautiful Soup 4 Documentation*. Crummy Software.
- Behnel, S., et al. (2023). *lxml â€” Processing XML and HTML with Python*. lxml.de.
---

**Last Updated:** November 2026
**Python Version:** 3.9+ (tested on 3.11 and 3.13.1)
**Primary AI Model:** Claude 3.5 Sonnet (+ GPT-4o and local Ollama Llama 3 fallback)
**Docker Base Image:** Python 3.11-slim Â· Default Port: 8080
**Test Suite:** 207 automated tests Â· 100% passing

---

## âš ï¸ Limitations & Future Work

### Current Scope
This parser implements an **HTML5 structural subset** designed to validate the agentic pipeline methodology. The following WHATWG specification features have been implemented or identified as future work:

| Feature | Status | Notes |
|---|---|---|
| Core tag tree construction | âœ… Implemented | Tags, attributes, nesting, text nodes |
| Implicit tag closures (p, li, heading) | âœ… Implemented | p closes before div/h1â€“h6 etc. |
| Void/self-closing elements | âœ… Implemented | br, img, hr, input etc. |
| Raw text elements (script, style) | âœ… Implemented | Content treated as raw text |
| DOCTYPE handling | âœ… Implemented | Basic doctype recognition |
| Comment nodes | âœ… Implemented | Standard, bogus comments |
| Table auto-wrapping (tbody, tr) | âœ… Implemented | Basic table structure |
| **Adoption Agency Algorithm** | âž¡ï¸ Future Work | Complex misnested formatting elements |
| **Foster Parenting** | âž¡ï¸ Future Work | Text/elements misplaced in tables |
| **Foreign Content** (SVG, MathML) | âž¡ï¸ Future Work | Requires namespace handling |
| **Full Tokenizer States** (80+) | âž¡ï¸ Future Work | Only core states implemented |

### Research Future Work Axes (13 Axes)

The thesis identifies **13 research axes** for extending this agentic framework beyond its current scope:

| Axis | Title | Description |
|---|---|---|
| 1 | **Adoption Agency Algorithm** | Full WHATWG Â§8.13 adoption agency for misnested formatting elements |
| 2 | **Foster Parenting & Misplaced Content** | Relocate table-misplaced text/elements per WHATWG Â§8.14 |
| 3 | **Foreign Content Namespaces** | SVG and MathML namespace integration with correct tokenizer switching |
| 4 | **Full 80+ Tokenizer States** | Complete WHATWG tokenizer state machine beyond the implemented core states |
| 5 | **Streaming & Incremental Parsing** | Chunk-by-chunk parsing for large documents and live network streams |
| 6 | **Adversarial Robustness & Fuzzing** | Property-based fuzzing with coverage-guided mutation and grammar-based adversarial inputs |
| 7 | **Neural-Symbolic Grammar Induction** | Active Automata Learning (L*/TTT) to infer minimal DFAs from parser traces; replace hand-coded FSM transitions with learned grammars |
| 8 | **Green AI Scheduling & Carbon-Aware Routing** | Dynamic agent scheduling driven by real-time grid carbon intensity; defer non-critical repairs to low-carbon windows |
| 9 | **Automated Exploit Synthesis & Zero-Day Quarantine** | Automated exploit generation from repair patches to discover zero-day parse differentials; quarantine unsafe subtrees before repair |
| 10 | **SIMD/AVX-512 & GPU Tokenizer Synthesis** | Vectorised byte-scanning kernels via SIMD/AVX-512 or GPU compute shaders; target sub-millisecond tokenisation for 10 MB+ documents |
| 11 | **WHATWG Living Standard Autonomous Tracking** | CI pipeline that diffs each WHATWG Living Standard commit, detects spec changes affecting the FSM, and auto-generates patch PRs |
| 12 | **Differential Shadow Execution & Web-Scale Oracle Mining** | Shadow-execute the agentic parser alongside reference browsers; mine correctness oracles from billions of real-world HTML documents at web scale |
| 13 | **Distributed Multi-Agent Consensus via CRDTs** | Replace single-leader repair with a CRDT-based distributed consensus protocol so multiple RepairAgentAI replicas agree on the canonical AST without locks |

### Why This Scope Is Academically Valid
The research contribution is the **agentic pipeline methodology** â€” not the completeness of the parser itself. The parser serves as the target system demonstrating that the multi-agent assembly line can:
1. Interpret a specification via `SpecAgentAI`
2. Generate conformant code via `CodegenAgentAI`
3. Validate quality via `CritiqueAgentAI`
4. Probe for failures via `RedTeamAgentAI`
5. Detect anomalies via `MonitorAgentAI`
6. Autonomously repair bugs via `RepairAgentAI`

Full WHATWG compliance is left as future work and is acknowledged in Chapter 6 of the thesis.
