# 🚀 QUICKSTART — Agentic AI HTML5 Parser

> Run the entire thesis project in under 5 minutes.

---

## 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or higher (tested: 3.11, 3.13) |
| Git | Any recent version |
| pip | Bundled with Python |

---

## 2. Install Dependencies

```bash
git clone https://github.com/Silvio777-hub/Agentic-HTML5-Parser.git
cd Agentic-HTML5-Parser
pip install -r requirements.txt
```

---

## 3. Configure API Key (Optional — only for full LLM pipeline)

Copy the example environment file and add your Anthropic API key:

```bash
cp .env.example .env
# Open .env and replace: ANTHROPIC_API_KEY=your_api_key_here
```

> **Note:** All evaluation scripts (tests, benchmarks, compliance, dashboard) work **without** an API key.  
> The API key is only required to run the live 7-agent LLM pipeline via `python orchestrator.py`.

---

## 4. Verify Everything Works (No API Key Required)

Run all commands via the unified CLI:

```bash
# Run all 34 automated unit & streaming tests
python cli.py test

# Run W3C compliance test harness
python cli.py compliance

# Run all 15 red-team adversarial attack vectors
python cli.py adversarial

# Run latency/memory benchmark vs BeautifulSoup4, html5lib, lxml
python cli.py benchmark

# Run the empirical ablation study
python cli.py ablation

# Generate all 5 publication-quality figures (saves to figures/)
python cli.py charts

# Launch the interactive web dashboard (DOM Tree Inspector)
python cli.py dashboard
```

After launching the dashboard, open your browser at: **http://localhost:8080/dashboard/**

---

## 5. Run the Full 7-Agent LLM Pipeline (Requires API Key)

```bash
python orchestrator.py
```

This executes the complete agentic assembly line:

```
SpecAgentAI → CodegenAgentAI → [CritiqueAgentAI || RedTeamAgentAI] → TestAgentAI → MonitorAgentAI → RepairAgentAI
```

All intermediate artifacts (`spec.yml`, `code.patch`, `test_report.json`, etc.) are saved to `runs/<timestamp>/`.

---

## 6. Run the Official W3C html5lib Compliance Suite

```bash
# Step 1: Download the official test suite (~1,000+ tests)
python scripts/setup_upstream_tests.py

# Step 2: Run compliance against all .dat files
python scripts/run_compliance.py
```

---

## 7. Project Structure at a Glance

```
├── src/                  # Core parser engine & AI agent classes
│   ├── parser.py         # HTML5 tokenizer + DOM tree builder
│   ├── claude_integration.py  # All 7 Claude-powered AI agents
│   ├── parallel_runner.py     # ThreadPoolExecutor concurrency
│   ├── cache.py          # SHA-256 response cache (zero repeat cost)
│   └── llm_provider.py   # Multi-model abstraction layer
│
├── scripts/              # Evaluation & automation scripts
│   ├── run_compliance.py       # W3C compliance runner
│   ├── compare_benchmarks.py   # Latency & memory benchmarks
│   ├── run_adversarial.py      # 15 red-team attack vectors
│   ├── run_ablation_study.py   # Empirical ablation experiments
│   ├── setup_upstream_tests.py # Downloads official W3C tests
│   └── serve_dashboard.py      # HTTP server + REST API
│
├── tests/                # 34 automated tests (pytest)
├── data/                 # Results JSON files (auto-generated)
├── figures/              # 300-DPI publication figures (auto-generated)
├── dashboard/            # Interactive web dashboard HTML
├── orchestrator.py       # Main 7-agent pipeline runner
├── cli.py                # Unified CLI entry point
├── config.py             # Configuration constants
└── architecture.md       # Detailed system design documentation
```

---

## 8. Key Results Summary

| Metric | Result |
|---|---|
| Automated Tests | **34/34 passed** |
| Adversarial Resilience | **15/15 attacks survived (100%)** |
| W3C Core Subset Compliance | **10/10 (100%)** |
| Benchmark vs BeautifulSoup4 | Comparable latency; pure Python implementation |
| Parallel Stage Speedup | ~42% wall-clock reduction (Critique + Red-Team concurrent) |
| Self-Repair Iterations | Max 3 loops; demo shows automated bug fix |

---

## 9. Common Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: anthropic` | Run `pip install -r requirements.txt` |
| Dashboard shows no data | Run `python cli.py compliance` first to generate `data/compliance_results.json` |
| `html5lib-tests not found` | Run `python scripts/setup_upstream_tests.py` |
| Port 8080 already in use | Use `python cli.py dashboard --port 8090` |
