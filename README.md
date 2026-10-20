# Agentic AI HTML5 Parser — Complete Implementation Guide

> **Author:** Opoka JM Silvio | **Degree:** MSc Computer Science | **Academic Year:** 2026/2027
> **Python:** 3.9+ (tested on 3.11 and 3.13) | **Model:** Claude 3.5 Sonnet | **Port:** 8082 (default)

---

## Project Overview

This project implements a **trustworthy HTML5 parser development pipeline** using **agentic AI** (Claude 3.5 Sonnet). The system orchestrates **7 specialized AI agents** that collaboratively design, implement, test, and self-repair an HTML5 parser component — benchmarked against BeautifulSoup4 and lxml, validated against the W3C `html5lib` official test suite, and protected by a Robustness Wrapper security layer.

### Key Innovation: Artifact-Based Agentic Assembly Line

Rather than treating AI as a black-box code generator, this system:
- Breaks development into **discrete AI-assisted stages** (Spec → Code → Review → Test → Attack → Monitor → Repair)
- Uses **intermediate artifacts** (specs, patches, tests) for full transparency and auditability
- Implements **iterative self-repair loops** driven by real execution traces and test failures
- Achieves **100% compliance on core subset specifications** (`sample_compliance_tests.dat`) and **100% adversarial resilience** (15/15 attack vectors)
- Employs **concurrency via ThreadPoolExecutor** for independent agent evaluations (Critique & Red-Team)
- Provides a **live interactive web dashboard** with DOM Tree Inspector at `http://localhost:8082/dashboard/`

> **Detailed Architecture Reference:** See [ARCHITECTURE.md](ARCHITECTURE.md) for full system diagrams, concurrency specifications, and agent contracts.

---

## 7 Core AI Agents

### 1. SpecAgentAI — The Architect (`src/claude_integration.py`)
**Responsibility:** Reads the W3C HTML5 specification and converts complex rules into a structured engineering blueprint.

**Input:**
- Human-written HTML5 subset description
- Parser interface contract

**Output:**
- `spec.yml` — YAML specification containing tokenizer states, parsing rules, implicit tag closure behaviours, and expected test cases

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

### 2. CodegenAgentAI — The Lead Coder (`src/claude_integration.py`)
**Responsibility:** Translates the specification blueprint into clean, compliant Python parsing code.

**Input:**
- YAML specification from SpecAgentAI
- Current parser implementation
- List of features to implement

**Output:**
- `code.patch` — Unified diff patch with tokenizer enhancements, tree construction logic, implicit closure handling, and inline documentation

---

### 3. CritiqueAgentAI — The Code Reviewer (`src/claude_integration.py`)
**Responsibility:** Reviews generated code against the specification for quality, performance, and style.

**Input:**
- Generated patch from CodegenAgentAI
- Original specification
- Test execution results

**Output:**
- Approval decision (approve/reject)
- Issues found (if any)
- Confidence score (0–100%)
- Improvement recommendations

**Runs in parallel** with RedTeamAgentAI via `ThreadPoolExecutor` (≈42% wall-clock speedup).

---

### 4. TestAgentAI — The QA Engineer (`src/claude_integration.py`)
**Responsibility:** Runs the official W3C `html5lib-tests` compliance suite and reports exact failure diffs.

**Input:**
- YAML specification
- Parser interface documentation

**Output:**
- `test_parser.py` — pytest test suite covering tokenization, tree construction, implicit closure, edge cases, with docstrings

**Test Coverage:**
- ✓ Basic functionality
- ✓ Attribute parsing
- ✓ Nested structures
- ✓ Self-closing tags
- ✓ Error handling

---

### 5. RedTeamAgentAI — The Ethical Hacker (`src/claude_integration.py`)
**Responsibility:** Attacks the parser with 15 adversarial, malicious, and malformed HTML inputs.

**Input:**
- Parser interface
- Known vulnerability patterns

**Output:**
- `test_red_team.py` — adversarial test suite including deeply nested structures (200+ levels), script injection, unclosed tags, long attributes (5000 chars), Unicode/emoji, zero-width spaces

**Result: 100% Resilience Rate (15/15 attacks survived)**

---

### 6. MonitorAgentAI — The DevOps Safety Watchdog (`src/claude_integration.py`)
**Responsibility:** Watches parser execution traces for anomalies — memory spikes, timeout violations, infinite loops.

**Input:**
- Parser execution traces (from `parse_with_trace()`)
- Performance metrics (timing, memory, recursion depth)

**Output:**
- Health assessment (healthy/unhealthy)
- Identified bottlenecks
- Recommendations

**Monitoring Points:**
- ✓ Recursion depth violations
- ✓ Memory exhaustion
- ✓ Timeout violations (< 50ms target)
- ✓ Inefficient algorithms
- ✓ State machine errors

---

### 7. RepairAgentAI — The Master Mechanic (`src/claude_integration.py`)
**Responsibility:** Analyses failing test traces and autonomously writes unified `.patch` diffs to self-heal bugs.

**Input:**
- Failing test names and error messages
- Execution trace showing failure point
- Current implementation

**Output:**
- `repair_N.patch` — Targeted fix with root-cause analysis, minimal changes, explanatory comments

**Repair Strategy:**
- Analyse failing test evidence
- Identify root cause from trace
- Generate minimal, focused patch
- Hard cap: **3 repair iterations max** (prevents infinite loops)

---

## Pipeline Workflow

```
┌─────────────────────────────────────────────┐
│  Human-defined HTML5 Subset + Interface     │
└────────────────────┬────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  SpecAgentAI    │  → spec.yml
            │ (Architect)     │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ CodegenAgentAI  │  → code.patch
            │ (Lead Coder)    │
            └────────┬────────┘
                     │
          ┌──────────┴──────────┐  ← Parallel via ThreadPoolExecutor
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ CritiqueAgentAI │   │ RedTeamAgentAI  │
│ (Code Reviewer) │   │ (Ethical Hacker)│
└────────┬────────┘   └────────┬────────┘
          └──────────┬──────────┘
                     ▼
            ┌─────────────────┐
            │  TestAgentAI    │  → test_report.json
            │  (QA Engineer)  │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ MonitorAgentAI  │  → health report
            │  (Watchdog)     │
            └────────┬────────┘
                     │
         ┌───────────▼───────────┐
         │    Tests Passed?      │──NO──┐
         └───────────┬───────────┘      │
                     │ YES              ▼
                     ▼       ┌─────────────────┐
              ┌──────────┐   │  RepairAgentAI  │ → repair_N.patch
              │ SUCCESS  │   │  (Mechanic)     │ (max 3 iterations)
              └──────────┘   └────────┬────────┘
                                      │
                              ┌───────▼────────┐
                              │ Re-run tests   │
                              └────────────────┘
```

---

## Complete Project Structure

```
Agentic AI HTML5 Parser/
│
├── src/                            ← CORE ENGINE & AGENT LOGIC
│   ├── parser.py                   # Pure-Python HTML5 Tokenizer (FSM), DOM Tree builder & Streaming API
│   ├── claude_integration.py       # All 7 Claude-powered AI Agent classes
│   ├── cache.py                    # SHA-256 On-Disk ResponseCache ($0.00 repeat cost, 0.00s latency on hit)
│   ├── parallel_runner.py          # ThreadPoolExecutor parallel dispatcher (42% speedup)
│   ├── llm_provider.py             # Multi-model abstraction (Claude 3.5, GPT-4o, local Ollama, Mock)
│   └── utils.py                    # ArtifactManager, PatchManager, ReportGenerator
│
├── scripts/                        ← AUTOMATION, BENCHMARKS & RESEARCH TOOLS
│   ├── serve_dashboard.py          # HTTP server + Live POST /api/parse REST endpoint
│   ├── run_compliance.py           # W3C html5lib-tests compliance runner
│   ├── setup_upstream_tests.py     # 1-click downloader for 1,000+ W3C tests
│   ├── compare_benchmarks.py       # Latency & memory benchmark vs BeautifulSoup4, html5lib, lxml
│   ├── run_adversarial.py          # 15 red-team attack vectors (100% resilience)
│   ├── run_ablation_study.py       # Empirical ablation: proves each agent's contribution
│   ├── generate_thesis_charts.py   # Auto-generates 5 publication-ready 300-DPI figures
│   ├── estimate_carbon.py          # Green AI energy consumption & CO2 calculator
│   ├── repair_pattern_mining.py    # Statistical failure taxonomy miner
│   ├── demo_self_repair.py         # Live self-healing demo (inject bug → auto-patch)
│   └── run_security_audit.py       # AST static scanner + 6-point STRIDE threat model
│
├── dashboard/                      ← INTERACTIVE WEB DASHBOARD
│   └── index.html                  # Bootstrap 5 live dashboard with DOM Tree Inspector modal
│
├── tests/                          ← AUTOMATED TEST SUITE (34 tests, 100% passing)
│   ├── test_integration.py         # 32 tests: Tokenizer, Parser, Implicit Closure, Traces, Edge Cases
│   └── test_streaming.py           # 2 tests: tokenize_stream() and parse_stream() generators
│
├── data/                           ← EXPERIMENTAL RESULTS & AUDIT ARTIFACTS
│   ├── sample_compliance_tests.dat # 10 bundled W3C test cases in official .dat format
│   ├── compliance_results.json     # W3C compliance output (100% pass rate)
│   ├── benchmark_results.json      # Latency, throughput, peak memory benchmarks
│   ├── adversarial_results.json    # Red-team stress test results (15/15 passed)
│   ├── ablation_study_results.json # Multi-agent contribution experiment results
│   ├── repair_patterns_analysis.json # Statistical distribution of recurring failure modes
│   ├── carbon_footprint_report.json  # Green AI energy & CO2 measurements
│   ├── security_audit_report.json    # AST code scan findings & STRIDE matrix
│   └── self_repair_demo_result.json  # Audit trail of live self-healing run
│
├── figures/                        ← 300-DPI PUBLICATION FIGURES
│   ├── 01_latency_vs_parsers.png   # Comparative latency bar chart
│   ├── 02_memory_consumption.png   # Peak memory comparison
│   ├── 03_repair_pattern_distribution.png  # Error taxonomy pie chart
│   ├── 04_parallel_speedup.png     # ThreadPool speedup demonstration
│   └── 05_ablation_comparison.png  # Per-agent ablation comparison
│
├── thesis/                         ← THESIS CHAPTER DRAFTS
│   ├── 01_introduction.md
│   ├── 02_background_and_related_work.md
│   ├── 03_system_architecture.md
│   ├── 04_implementation.md
│   ├── 05_evaluation_and_results.md
│   ├── 06_discussion_and_limitations.md
│   ├── 07_conclusion_and_future_work.md
│   └── README_THESIS_GUIDE.md
│
├── presentation/                   ← DEFENSE PRESENTATION
│   ├── defense_presentation.md     # 25-slide deck with speaker notes
│   └── defense_presentation.docx   # Word version
│
├── cache/                          ← SHA-256 RESPONSE CACHE
│   └── *.json                      # Cached LLM responses (replay = $0.00 cost, 0.00s latency)
│
├── .github/workflows/ci.yml        ← GITHUB ACTIONS CI/CD PIPELINE
│
├── cli.py                          # Master CLI (one command to run everything)
├── orchestrator.py                 # Full pipeline orchestrator with 3-iteration repair loop
├── config.py                       # Configuration: API keys, model names, paths
├── Dockerfile                      # Multi-stage Python container
├── docker-compose.yml              # Docker Compose (port 8082)
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template — copy to .env and fill in keys
└── README.md                       # This file
```

---

## 🔑 Environment Setup (API Keys)

### Step 1 — Copy the environment template

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

### Step 2 — Edit `.env` and add your keys

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

### Step 3 — Verify configuration

```powershell
python config.py
```
Expected output: `All directories created successfully.`

---

## ⚙️ Installation and Setup

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

## 🚀 Running the Project

### Option A — Run Directly with Python (Recommended)

#### Step 1: Start the Live Dashboard & API Server
```powershell
python scripts/serve_dashboard.py --no-browser --port 8082
```

Then open: **http://localhost:8082/dashboard/**

> **Note:** Port 8080 or 8081 may be occupied by other services on your machine.
> Use `--port 8082` (or any other free port).

#### Verify the server is listening
```powershell
netstat -ano | findstr ":8082"
```
Expected output: `TCP    0.0.0.0:8082    0.0.0.0:0    LISTENING`

---

### Option B — Run with Docker

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

#### Rebuild after code changes (uses cached layers — much faster)
```powershell
docker compose up -d --build
```

> **Port conflict?** If port 8080 is occupied (another container/service), edit
> `docker-compose.yml` line 16 and change `"8080:8080"` → `"8082:8080"`,
> then run `docker compose up -d`.

> **Slow first build?** Docker downloads the Python 3.11-slim base image (~200MB)
> and all pip packages on first run. Subsequent builds use the layer cache and
> complete in under 30 seconds.

---

## 🧪 Running the Automated Test Suite

### Run All 34 Tests
```powershell
python -m pytest tests/ -v
```
Expected: `34 passed in ~1.6s`

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

## 🎛️ Master CLI — All Commands

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

# Generate all 5 publication-ready 300-DPI thesis figures into figures/
python cli.py charts

# Estimate computational carbon footprint & energy in Joules (Green AI)
python cli.py carbon

# Static security audit: AST scanner + 6-point STRIDE threat model check
python cli.py audit

# Live self-healing demo: inject a bug → watch it auto-patch itself
python cli.py repair-demo

# Verify all 7 thesis chapters in thesis/
python cli.py build-thesis
```

---

## 📊 Individual Research & Experiment Scripts

Run any experiment directly without the CLI wrapper:

```powershell
# W3C Compliance: run bundled sample tests
python scripts/run_compliance.py --sample

# Download the FULL W3C upstream test suite (1,000+ official tests)
python scripts/setup_upstream_tests.py

# Benchmark: latency, throughput, peak memory vs BeautifulSoup4 & lxml
python scripts/compare_benchmarks.py

# Adversarial: 15 red-team attack vectors with detailed pass/fail per vector
python scripts/run_adversarial.py

# Ablation: empirical proof of each agent's individual contribution
python scripts/run_ablation_study.py

# Charts: generate all 5 thesis publication figures (saves to figures/)
python scripts/generate_thesis_charts.py

# Carbon: Green AI energy & CO2 footprint calculation
python scripts/estimate_carbon.py

# Security: AST static scan + STRIDE threat model validation
python scripts/run_security_audit.py

# Repair patterns: mine and classify recurring failure modes statistically
python scripts/repair_pattern_mining.py

# Self-repair demo: intentionally break the parser → watch it self-heal
python scripts/demo_self_repair.py
```

---

## 📁 Where to Find All Results

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
| Thesis figures (5 PNGs) | `figures/` | `python cli.py charts` |
| Pipeline run artifacts | `runs/<run_id>/` | `orchestrator.py` |
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

## 🌐 Live Dashboard URLs

| URL | Description |
|---|---|
| `http://localhost:8082/dashboard/` | Main dashboard: compliance panels, benchmark charts, DOM Inspector |
| `POST http://localhost:8082/api/parse` | REST API: send HTML, receive parsed DOM tree + trace |

### Test the REST API from PowerShell
```powershell
$body = '{"html": "<p>Hello <b>World</b></p>"}'
Invoke-WebRequest -Uri "http://localhost:8082/api/parse" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -ExpandProperty Content
```

---

## 🔍 Diagnostic Commands

```powershell
# Check which ports are currently in use
netstat -ano | findstr ":8080"
netstat -ano | findstr ":8082"

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

# Check cache is working (run twice — second call should show 0.00s latency)
python -c "from src.cache import ResponseCache; c = ResponseCache(); print('[OK] Cache dir:', c.cache_dir)"

# Verify the streaming API works
python -c "from src.parser import tokenize_stream; tokens = list(tokenize_stream('<p>Test</p>')); print('[OK] Streamed tokens:', len(tokens))"
```

---

## 🔁 CI/CD Pipeline (GitHub Actions)

The project includes a full automated CI pipeline at [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

On every push and pull request, it automatically:
1. Installs all dependencies
2. Runs linting with `flake8`
3. Executes all 34 pytest tests
4. Generates a code coverage report

To check CI status locally before pushing:
```powershell
# Lint check
python -m flake8 src/ --max-line-length=120

# Full test run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

---

## 💡 Using the Parser in Your Own Code

```python
from src.parser import tokenize, parse, parse_with_trace

html = "<p>Hello<div>World</div></p>"

# 1. Tokenization only
tokens = tokenize(html)
for token in tokens:
    print(token)

# 2. Full parse → returns TreeNode (use .name not .tag)
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

## 🤖 Running Individual AI Agents

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

## 🔬 Key Technical Results

| Metric | Result |
|---|---|
| Automated tests passing | **34 / 34 (100%)** |
| W3C html5lib compliance | **10/10 sample tests (100%)** |
| Adversarial resilience rate | **15/15 attack vectors (100%)** |
| LLM response cache hit cost | **\$0.00 / 0.00s latency** |
| Parallel agent speedup | **~42% wall-clock reduction** |
| Max repair iterations (safety cap) | **3 iterations** |
| Dashboard API latency | **< 50ms per parse** |
| Supported LLM providers | **3 (Claude, GPT-4o, Ollama)** |

---

## 🛠️ Troubleshooting

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
# Find which process is using port 8082
netstat -ano | findstr ":8082"
# Start on a different port instead
python scripts/serve_dashboard.py --no-browser --port 8090
```

### Docker build stuck on "exporting layers"
This is a known Windows Docker Desktop issue with large images (numpy/matplotlib).
**Solution:** Run directly with Python instead:
```powershell
pip install -r requirements.txt
pip install matplotlib python-docx
python scripts/serve_dashboard.py --no-browser --port 8082
```

### TreeNode AttributeError: 'TreeNode' has no attribute 'tag'
The node attribute is **`.name`**, not `.tag`:
```python
# WRONG ❌
tree.tag

# CORRECT ✅
tree.name
```

### Slow AI agent responses
- Use the **Mock provider** for local testing (no API key needed): set `LLM_PROVIDER=mock` in `.env`
- Reduce `MAX_TOKENS` in `config.py`
- The **response cache** in `cache/` means repeated identical prompts cost \$0.00

---

## 🔐 Security Considerations

1. **API Key Protection:** Never commit `.env` to version control (it is in `.gitignore`)
2. **Input Validation:** Parser validates and sanitises all HTML before processing
3. **Resource Limits:** Robustness Wrapper enforces timeout (50ms) and memory caps
4. **Bounded Repair Loop:** Hard cap of 3 iterations prevents infinite LLM loops
5. **Static Analysis:** `run_security_audit.py` performs AST-level vulnerability scanning
6. **STRIDE Threat Model:** 6-point threat model validated against the full pipeline

---

## 📚 References

- [HTML5 Specification — WHATWG](https://html.spec.whatwg.org/)
- [html5lib-tests — W3C Official Test Suite](https://github.com/html5lib/html5lib-tests)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [BeautifulSoup4 (benchmark baseline)](https://www.crummy.com/software/BeautifulSoup/)
- [lxml (benchmark baseline)](https://lxml.de/)

---

**Last Updated:** October 2026
**Python Version:** 3.9+ (tested on 3.11 and 3.13.1)
**Primary AI Model:** Claude 3.5 Sonnet (+ GPT-4o and local Ollama Llama 3 fallback)
**Docker Base Image:** Python 3.11-slim · Default Port: 8082
**Test Suite:** 34 automated tests · 100% passing
