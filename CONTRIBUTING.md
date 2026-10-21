# 🤝 Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Agentic-HTML5-Parser.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests to confirm everything works: `python cli.py test`

## Development Workflow

### Running the Test Suite
```bash
python -m pytest tests/ -v
```

### Running All Evaluation Scripts
```bash
python cli.py test         # 34 unit & streaming tests
python cli.py compliance   # W3C compliance suite
python cli.py adversarial  # Red-team attack vectors
python cli.py benchmark    # Latency benchmarks
```

## Project Structure

See [QUICKSTART.md](QUICKSTART.md) and [ARCHITECTURE.md](ARCHITECTURE.md) for full documentation.

## Code Style

- Python 3.9+ compatible code
- Type hints on all public functions
- Docstrings on all classes and functions
- Keep `src/parser.py` zero-dependency (no imports outside standard library)

## Submitting a Pull Request

1. Create a feature branch: `git checkout -b feature/my-improvement`
2. Commit with a descriptive message
3. Push and open a Pull Request against `main`
4. Ensure all CI checks pass
