# 🤝 Contributing Guide — Agentic AI HTML5 Parser

> **Project:** MSc Thesis — *"Trustworthy HTML5 Parser Development via Agentic AI"*
> **Author:** Opoka JM Silvio | `opoka2010@gmail.com`
> **Repo:** https://github.com/Silvio777-hub/Agentic-HTML5-Parser

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Agentic-HTML5-Parser.git
   cd Agentic-HTML5-Parser
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Verify everything works** (no API key needed):
   ```bash
   python cli.py test          # 207 tests — all should pass
   python cli.py adversarial   # 15/15 red-team vectors
   python cli.py compliance    # W3C compliance sample
   ```

---

## Development Workflow

### Running the Full Test Suite
```bash
python -m pytest tests/ -v              # All 207 tests with verbose output
python -m pytest tests/ -q              # Quick summary only
python -m pytest tests/ --cov=src --cov-report=html  # With HTML coverage report
```

### Running the Full Evaluation Pipeline
```bash
python cli.py test         # 207 unit, streaming, DOM selector, and offline agent tests
python cli.py compliance   # W3C compliance suite (bundled sample tests)
python cli.py adversarial  # 15 red-team attack vectors
python cli.py benchmark    # Latency benchmarks vs BeautifulSoup4 and lxml
python cli.py ablation     # Empirical ablation study (which agents matter most)
python cli.py charts       # Generate 7 publication-ready 300-DPI figures
python cli.py carbon       # Green AI carbon footprint estimate
python cli.py audit        # Static AST security scan + STRIDE threat model
python cli.py dashboard    # Launch interactive web dashboard at http://localhost:8080/dashboard/
```

### Running Without an API Key (Mock Mode)
All evaluation scripts work without an Anthropic API key. Set `LLM_PROVIDER=mock` in your `.env` file for local testing. The API key is only needed for `python orchestrator.py` (the live 7-agent pipeline).

---

## Project Structure

| Path | Description |
|---|---|
| `src/parser.py` | Core HTML5 tokenizer (FSM) and DOM tree builder — zero external dependencies |
| `src/claude_integration.py` | All 7 Claude-powered AI agent classes |
| `src/parallel_runner.py` | ThreadPoolExecutor parallel dispatcher |
| `src/cache.py` | SHA-256 response cache (zero-cost repeat calls) |
| `src/llm_provider.py` | Multi-model abstraction (Claude, GPT-4o, Ollama, Mock) |
| `src/plugin_manager.py` | Plugin loader and hook dispatcher |
| `tests/` | 207 automated tests across 10 test modules |
| `scripts/` | Evaluation, benchmark, and automation scripts |
| `data/` | JSON result files (auto-generated) |
| `figures/` | 300-DPI publication figures (auto-generated) |
| `dashboard/index.html` | 5-tab interactive web dashboard |
| `plugins/example_lint/` | Example plugin demonstrating the hook API |

For full details see [architecture.md](architecture.md) and [quickstart.md](quickstart.md).

---

## Code Style

- **Python 3.9+ compatible** — no walrus operator in public API, no `match` statements
- **Type hints** on all public functions and class methods
- **Docstrings** (Google style) on all classes and public functions
- **`src/parser.py` must remain zero-dependency** — only Python standard library imports allowed
- Line length: **120 characters maximum** (enforced by `flake8` and `ruff`)
- Run linting before committing:
  ```bash
  python -m flake8 src/ --max-line-length=120
  ```

---

## How to Add a New Test

1. Identify which test module is most relevant (see `tests/` listing above)
2. Add your test function following the existing pattern:
   ```python
   def test_my_new_case():
       """One-line description of what this test verifies."""
       from src.parser import parse
       tree = parse("<your>html<here>")
       assert tree.children[0].name == "expected_tag"
   ```
3. Run the full suite to confirm **207 + N tests** all pass:
   ```bash
   python -m pytest tests/ -v
   ```
4. Update the test count in `README.md` and `CONTRIBUTING.md` if you are adding a permanent test.

---

## How to Add a New Plugin

Plugins extend the pipeline with custom hooks (e.g., a linter, a formatter, a logger).

1. Create a folder under `plugins/`:
   ```
   plugins/my_plugin/
   ├── plugin.yml     # Plugin manifest
   └── my_rule.py    # Hook implementation
   ```

2. Write the manifest `plugin.yml`:
   ```yaml
   name: my_plugin
   version: 1.0.0
   hooks:
     - on_token        # Called after each token is emitted
     - on_tree_built   # Called after DOM tree is fully constructed
   ```

3. Implement the hook in `my_rule.py`:
   ```python
   def on_token(token):
       """Called for every token produced by the tokenizer."""
       pass  # Your logic here

   def on_tree_built(tree):
       """Called after the full DOM tree is constructed."""
       pass  # Your logic here
   ```

4. Load the plugin via `src/plugin_manager.py`:
   ```python
   from src.plugin_manager import PluginManager
   pm = PluginManager()
   pm.load("plugins/my_plugin")
   ```

See `plugins/example_lint/` for a complete working example.

---

## Submitting a Pull Request

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-improvement
   ```

2. **Make your changes** and ensure all tests still pass:
   ```bash
   python -m pytest tests/ -v
   python -m flake8 src/ --max-line-length=120
   ```

3. **Commit with a descriptive message** using the conventional commit format:
   ```
   feat(parser): add support for <template> element handling
   fix(tests): correct expected node count in test_integration.py
   docs(readme): update port references to 8080
   ```

4. **Push and open a Pull Request** against `main`:
   - Describe what you changed and why
   - Reference any related issue numbers
   - Ensure all GitHub Actions CI checks pass (tests, linting, adversarial suite)

5. **CI must pass** — the pipeline runs on Ubuntu and Windows across Python 3.9, 3.11, and 3.13.

---

## Reporting Issues

- **Bugs:** Open a [GitHub Issue](https://github.com/Silvio777-hub/Agentic-HTML5-Parser/issues) with a minimal reproducible example
- **Security vulnerabilities:** See [SECURITY.md](SECURITY.md) — do NOT open a public issue
- **Feature requests:** Open a GitHub Issue with the `enhancement` label

---

## Code of Conduct

Be respectful, constructive, and collaborative. This is an academic research project — contributions that improve reproducibility, robustness, or documentation are especially welcome.
