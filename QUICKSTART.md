# Quick Start Guide - Agentic AI HTML5 Parser

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd "Agentic AI HTML5 Parser"
pip install -r requirements.txt
```

### Step 2: Configure API Key
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your Groq API key
# Get it from https://console.groq.com
# GROQ_API_KEY=gsk_your-key-here
```

### Step 3: Run the Pipeline
```bash
python orchestrator.py
```

You should see output like:
```
============================================================
Pipeline Orchestrator initialized
Run ID: 20260224_123456
Run directory: runs/20260224_123456
============================================================

============================================================
STAGE 1: SPEC AGENT
============================================================

Generating specification from HTML subset...
✓ Specification generated (4523 chars)
  Rules: 12
```

## What Just Happened?

The orchestrator executed all 7 agents:

1. **Spec Agent** - Converted HTML subset into `spec/spec.yml`
2. **Codegen Agent** - Generated `patches/code.patch`
3. **Critique Agent** - Validated the patch
4. **Test Agent** - Created `tests/test_parser.py`
5. **Red-Team Agent** - Created `tests/test_red_team.py`
6. **Test Execution** - Ran 32 integration tests
7. **Monitor Agent** - Analyzed execution metrics
8. **Repair Agent** (if needed) - Fixed any failures

## View Results

```bash
# Check the run directory
ls runs/20260224_123456/

# View generated specification
cat runs/20260224_123456/spec/spec.yml

# View pipeline report
cat runs/20260224_123456/reports/pipeline_report.json

# View test results
cat runs/20260224_123456/reports/test_report.json
```

## Understanding the Output

### spec.yml (Specification)
```yaml
name: HTML5 Parser Subset
rules:
  tokenizer:
    states: [...]
  parser:
    tag_closure: {...}
```

### code.patch (Implementation)
```diff
--- a/src/parser.py
+++ b/src/parser.py
@@ -120,6 +120,12 @@
+ # New implementation code
+ def parse_with_implicit_closure(...):
+     ...
```

### pipeline_report.json (Results)
```json
{
  "run_id": "20260224_123456",
  "status": "success",
  "stages": {
    "spec_agent": {"status": "success"},
    "codegen_agent": {"status": "success"},
    ...
  },
  "final_test_report": {
    "summary": {
      "passed": 32,
      "failed": 0,
      "success_rate": 1.0
    }
  }
}
```

## Test the Parser Directly

```python
from src.parser import tokenize, parse, parse_with_trace

html = "<p>Hello<div>World</div></p>"

# Tokenize
tokens = tokenize(html)
print([str(t) for t in tokens])

# Parse  
tree = parse(html)
print(tree.serialize())

# Parse with trace
result = parse_with_trace(html)
print(f"Events: {len(result['trace']['events'])}")
print(f"Duration: {result['trace']['duration']}s")
```

## Run Specific Tests

```bash
# Tokenization tests
pytest tests/test_integration.py::TestTokenizer -v

# Parser tests
pytest tests/test_integration.py::TestParser -v

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### "GROQ_API_KEY not set"
**Fix:** Make sure you've edited `.env` with your actual API key

### "ModuleNotFoundError: No module named 'groq'"
**Fix:** Run `pip install -r requirements.txt` again

### "git apply failed"
**Fix:** Make sure git is installed and you're in the right directory

### Slow responses
**Fix:** API can be slow sometimes. Wait longer or check: https://status.groq.com

## Key Files to Understand

| File | Purpose |
|------|---------|
| `orchestrator.py` | Main pipeline - start here! |
| `src/parser.py` | Core parser implementation |
| `src/groq_integration.py` | AI agent wrappers |
| `src/utils.py` | Artifact management |
| `config.py` | Configuration |
| `tests/test_integration.py` | 32 parser tests |
| `README.md` | Full documentation |

## Example: Customize the HTML Subset

Edit the `main()` function in `orchestrator.py`:

```python
html_subset = """
Implement a parser for these HTML5 elements:

1. Basic tags:
   - <html>, <body>, <head>
   - <p>, <div>, <span>
   
2. Semantic tags:
   - <article>, <section>, <nav>
   
3. Implicit closure:
   - <p> closes before <div>
   - <li> closes before another <li>
   
4. Attributes:
   - id, class, href, src
   - Parse attribute values correctly
"""

parser_interface = """
The parser must implement:
- tokenize(html) - returns list of tokens
- parse(html) - returns DOM tree
- parse_with_trace(html) - returns tokens, tree, trace
"""

report = orchestrator.run(html_subset, parser_interface)
```

Then run: `python orchestrator.py`

## Viewing Complete Architecture

See:
1. `README.md` - Complete documentation
2. `IMPLEMENTATION_REPORT.md` - Detailed design report
3. `docs/ARCHITECTURE.md` - Visual diagrams

## Next Steps

1. ✓ Run the complete pipeline
2. ✓ Review the generated artifacts
3. ✓ Study the inline comments in code
4. ✓ Run the test suite
5. ✓ Read the detailed documentation

## Getting Help

- **Configuration issues:** Check `.env` file
- **Import errors:** Verify `pip install -r requirements.txt`
- **API errors:** Check Groq console for quota
- **Test failures:** Look at `runs/[run_id]/reports/`
- **Code questions:** See inline comments and docstrings

---

**You're all set!** The pipeline is ready to generate, test, and repair an HTML5 parser entirely driven by AI agents.
