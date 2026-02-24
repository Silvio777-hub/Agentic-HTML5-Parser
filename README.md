# Agentic AI HTML5 Parser Pipeline (v1.3.0)
> **Professional Suite - University of Florence (Topic 6)**

## Project Overview
This project implements a subset of an HTML5 parser (specifically for `div` and `p` tags) using a multi-agent AI pipeline powered by **Groq (Llama 3.3 70B)**. The "Professional Suite" v1.3.0 introduces production-grade enhancements, including a Selector Agent, Semantic Compliance Auditor, and automated deliverable generation (Word/PPTX).

## Professional Suite (v1.3.0) Highlights
1. **Selector Agent (Query Engine)**: Programmatic DOM searching by ID or tag name.
2. **Semantic Compliance Auditor**: Enforces HTML5 content model rules (e.g., no `div` inside `p`).
3. **Subprocess Sandboxing**: Uses Python's `multiprocessing` for hardware-level security isolation.
4. **Structural Integrity Wrapper**: Validates DOM depth and node counts.
5. **Full Attribute Parsing**: Supports complex quoted/unquoted attributes and boolean flags.

### 🚀 Professional Showcase & Demos
Ready for a live presentation? Run the dedicated demo suite:
```bash
python presentation_demos.py
```
This script orchestrates 5 high-impact scenarios: **Self-Healing**, **Security Sandbox**, **Semantic Compliance**, **Data Querying**, and **Visual DOM Exploration**.

## 5 Professional Grade Features

1.  **Visual DOM Explorer (`inspect_dom.py`)**: A terminal-based high-fidelity visualization tool with color-coded syntax highlighting and structural indentation.
2.  **Accessibility Auditor (`a11y_auditor.py`)**: Automated agent that scans the DOM for inclusive design violations (e.g., missing alt text, empty headings).
3.  **Selector Agent API**: A programmatic interface for DOM querying by ID or Tag, allowing developers to treat the engine like a lightweight jQuery for Python.
4.  **Industrial Sandboxing**: Hardware-level security using Python's `multiprocessing` to isolate parsing execution and prevent resource exhaustion 
    attacks.
5.  **Autonomous Repair Loop**: A self-correcting logic loop where AI agents analyze test failures and synthesize code patches in real-time.

### CLI Conversion
Convert text inputs directly to HTML:
```bash
python cli.py source.txt output.html
```

## 4 Core Agents

### 1. **Spec Agent** - Creates Rules (spec.yml)
**Responsibility:** Interpret HTML5 specification and generate structured rules.

**Input:**
- Human-written HTML5 subset description
- Parser interface contract

**Output:**
- `spec.yml` - YAML specification containing:
  - Tokenizer states and transitions
  - Parsing rules for each tag type
  - Implicit tag closure behaviors
  - Expected test cases

**AI Model:** Llama 3.3 70B (Groq) with semantic understanding of specifications

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

### 2. **Codegen Agent** - Creates Implementation (code.patch)
**Responsibility:** Generate code patches from specification.

**Input:**
- YAML specification from Spec Agent
- Current parser implementation
- List of features to implement

**Output:**
- `code.patch` - Unified diff patch containing:
  - Tokenizer enhancements
  - Tree construction logic
  - Implicit closure handling
  - Inline documentation

**Key Features:**
- Generates valid Python code
- Includes inline comments explaining each section
- Produces proper unified diff format
- Applies using standard `git apply` command

### 3. **Test Agent** - Creates Verification Suite (tests.py)
**Responsibility:** Generate comprehensive conformance tests.

**Input:**
- YAML specification
- Parser interface documentation

**Output:**
- `test_parser.py` - Pytest test suite

**Test Coverage:**
- ✓ Basic functionality
- ✓ Attribute parsing
- ✓ Nested structures
- ✓ Self-closing tags

### 4. **Repair Agent** - Autonomously Fixes Issues
**Responsibility:** Analyze test failures and synthesize repairs.

**Input:**
- Original specification
- Failing test report
- Current implementation code

**Output:**
- Iterative repair patches (e.g., `repair_1.patch`)

**Mechanism:**
1. Parse the `test_report.json`
2. Identify specific logic errors
3. Generate minimal patches to resolve discrepancies
4. Hand off for re-validation

**Monitoring Points:**
- ✓ Recursion depth violations
- ✓ Memory exhaustion
- ✓ Timeout violations
- ✓ Inefficient algorithms
- ✓ State machine errors

## Pipeline Workflow

```
┌─────────────────────────────────────────────┐
│  Human-defined HTML5 Subset + Interface    │
└────────────────────┬────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Spec Agent     │
            │ (Llama 3.3 70B) │
            └────────┬────────┘
                     │ spec.yml
                     ▼
            ┌─────────────────┐
            │ Codegen Agent   │
            │ (Llama 3.3 70B) │
            └────────┬────────┘
                     │ code.patch
                     ▼
            ┌─────────────────┐
            │  Test Agent     │
            │ (Llama 3.3 70B) │
            └────────┬────────┘
                     │ test_parser.py
                     ▼
            ┌─────────────────┐
            │  Test Execution │
            │ & Analytics     │
            └────────┬────────┘
                     │ test_report
                     ▼
        ┌────────────┴────┐
        │ Tests Passed? ──┤──NO──┐
        └────────┬────────┘      │
                 │ YES           │
                 ▼               │
         ┌────────────┐          │
         │  SUCCESS   │          │
         └────────────┘          │
                                 ▼
                        ┌─────────────────┐
                        │ Repair Agent    │
                        │ (Llama 3.3 70B) │
                        └────────┬────────┘
                                 │ repair.patch
                                 │
                           ┌──────▼────────┐
                           │ Re-run tests  │
                           └───────────────┘
```

## 7 Core Features

### Feature 1: Traceable Parser Interface
The parser provides three entry points:
```python
tokenize(html) -> List[Token]           # Tokenization only
parse(html) -> TreeNode                 # Full parsing
parse_with_trace(html) -> Dict          # Parse + execution trace
```

### Feature 2: External AI Tool Integration
Groq (Llama 3.3 70B) API integration:
- Semantic understanding of specifications
- Code generation with context awareness
- Critique and validation logic
- Repair recommendations based on failures

### Feature 3: Artifact-Based Pipeline
All intermediate outputs are preserved:
- Specifications (YAML)
- Code patches (unified diff)
- Test suites (Python/pytest)
- Execution reports (JSON)
- Execution traces (JSON)

### Feature 4: Iterative Repair Loop
Failures drive targeted improvements:
- Test execution produces evidence
- Monitor agent analyzes traces
- Repair agent proposes fixes
- Patches applied and retested
- Iteration continues until success

### Feature 5: Security-Focused Testing
Red-team agent generates adversarial tests:
- Malformed HTML inputs
- Deeply nested structures
- Resource exhaustion patterns
- Timeout constraint violations

### Feature 6: Execution Monitoring
Parser execution is instrumented with:
- Token emission events
- Tag closure operations
- Attribute parsing records
- Error conditions and recovery

### Feature 7: Reproducible Workflow
Each pipeline run creates:
- Unique run ID (timestamp-based)
- Isolated run directory
- Complete artifact collection
- Execution report with timestamps

## Project Structure

```
Agentic AI HTML5 Parser/
├── src/
│   ├── parser.py              # Parser implementation
│   ├── utils.py               # Artifact management
│   ├── groq_integration.py    # AI agent wrappers
│   ├── verifiers.py           # Compliance & Selector agents
│   ├── robustness.py          # Sandboxing & Integrity
│   └── __init__.py
├── agents/ (Prompts)
│   ├── spec_agent.txt
│   ├── codegen_agent.txt
│   └── ...
├── tests/
├── prompts/
│   ├── spec_agent.txt         # Spec Agent prompt
│   ├── codegen_agent.txt      # Codegen Agent prompt
│   ├── test_agent.txt         # Test Agent prompt
│   └── ...                    # Other prompts
├── runs/
│   └── <run_id>/              # Pipeline run outputs
│       ├── spec/
│       │   └── spec.yml
│       ├── patches/
│       │   ├── code.patch
│       │   ├── tests.patch
│       │   └── repair_1.patch
│       ├── reports/
│       │   ├── pipeline_report.json
│       │   └── test_report.json
│       └── traces/
│           └── execution.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AGENT_GUIDE.md
│   └── USAGE_GUIDE.md
├── orchestrator.py            # Main pipeline orchestrator
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── README.md                 # This file
└── .gitignore
```

## Installation and Setup

### Prerequisites
- Python 3.9+
- Groq API key (Llama 3.3 70B access)
- Git (for patch operations)

### Installation Steps

1. **Clone/Setup Project**
```bash
cd "Agentic AI HTML5 Parser"
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=gsk_...
```

4. **Verify Setup**
```bash
python config.py
# Should output all directories created successfully
```

## Usage Guide

### Running the Complete Pipeline

```python
from orchestrator import PipelineOrchestrator

# Create orchestrator
orchestrator = PipelineOrchestrator()

# Define your HTML5 subset
html_subset = """
Implement a parser for:
1. Basic tags: <html>, <body>, <p>, <div>
2. Implicit closure of <p> before block elements
3. Attribute parsing
"""

parser_interface = """
- tokenize(html) -> List[Token]
- parse(html) -> TreeNode
- parse_with_trace(html) -> Dict
"""

# Run full pipeline
report = orchestrator.run(html_subset, parser_interface)

# Access results
print(f"Run ID: {report['run_id']}")
print(f"Status: {report['status']}")
print(f"Run Directory: {orchestrator.run_dir}")
```

### Running Individual Agents

```python
from src.groq_integration import SpecAgentAI

# Create agent
spec_agent = SpecAgentAI()

# Generate specification
spec_yaml = spec_agent.generate_specification(
    html_subset="<p>, <div>, implicit closure",
    parser_interface="tokenize() and parse()"
)

print(spec_yaml)
```

### Testing the Parser

```python
from src.parser import tokenize, parse, parse_with_trace

html = "<p>Hello<div>World</div></p>"

# Tokenization
tokens = tokenize(html)
for token in tokens:
    print(token)

# Parsing
tree = parse(html)
print(tree.serialize())

# Parsing with trace
result = parse_with_trace(html)
print(f"Events: {len(result['trace']['events'])}")
print(f"Duration: {result['trace']['duration']}s")
```

## Validation and Testing

### Running Tests
```bash
# Run conformance tests
pytest tests/test_parser.py -v

# Run adversarial tests
pytest tests/test_red_team.py -v

# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Examining Pipeline Outputs

```bash
# View latest pipeline report
cat runs/[run_id]/reports/pipeline_report.json

# View test report
cat runs/[run_id]/reports/test_report.json

# View generated specification
cat runs/[run_id]/spec/spec.yml

# View applied patches
cat runs/[run_id]/patches/code.patch
```

## Key Implementation Details

### Spec Agent Output Format

```yaml
name: HTML5 Parser Spec
version: 0.1.0
rules:
  tokenizer:
    states:
      - name: DATA
        description: "Normal character reading"
      - name: TAG_OPEN
        description: "After '<'"
    transitions:
      DATA:
        '<': TAG_OPEN
        '': CHARACTER
  parser:
    tag_closure:
      p:
        closes_before: [div, blockquote]
test_cases:
  - input: "<p>Test<div>Block</div>"
    expected: "p closes before div starts"
```

### Patch Format

Patches are standard unified diff format:
```diff
--- a/src/parser.py
+++ b/src/parser.py
@@ -120,6 +120,12 @@ def parse(html):
     # Handle tag closure
     if tag_name in self.SPECIAL_END_TAGS:
+        # NEW: Implicit p closure rule
+        if self.is_open("p"):
+            self.close_element("p")
+            self.trace.add_event("implicit_p_closed",
+                                details={"before_tag": tag_name})
+
         self.open_elements.append(node)
```

### Execution Trace Format

```json
{
  "events": [
    {
      "timestamp": 0.001,
      "type": "tokenization_start",
      "details": {"html_length": 45}
    },
    {
      "timestamp": 0.002,
      "type": "character_emitted",
      "details": {"char": "H"}
    },
    {
      "timestamp": 0.003,
      "type": "tag_emitted",
      "details": {"tag_name": "p", "tag_type": "StartTag"}
    }
  ],
  "errors": [],
  "duration": 0.015
}
```

## Troubleshooting

### Issue: "GROQ_API_KEY not set"
**Solution:**
1. Get free API key from https://console.groq.com
2. Create `.env` file with `GROQ_API_KEY=gsk_your_key`
3. Verify with `python config.py`

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
python -c "import groq; print('OK')"
```

### Issue: Git apply fails
**Solution:**
1. Ensure git is installed: `git --version`
2. Initialize repository: `git init` (if needed)
3. Check patch format validity

### Issue: Slow agent responses
**Solutions:**
- Use lighter prompts for faster responses
- Reduce `MAX_TOKENS` in config.py
- Check API rate limits on Groq console

## Extending the Pipeline

### Adding a New Agent Type

1. **Create agent class in `groq_integration.py`:**
```python
class CustomAgentAI:
    def __init__(self):
        self.groq = GroqAgent()
    
    def generate_output(self, input_data):
        return self.groq.call(prompt, system_prompt)
```

2. **Create stage in `orchestrator.py`:**
```python
def _run_custom_agent(self, report):
    agent = CustomAgentAI()
    output = agent.generate_output(data)
    # Save and report
```

3. **Add to pipeline workflow**

### Customizing Prompts

Edit prompt templates in `prompts/` directory to:
- Change agent behavior
- Adjust tone and style
- Add domain-specific instructions
- Implement specialized logic

### Using Different AI Models

Modify `config.py` to use different models:
```python
GROQ_MODEL = "llama3-70b-8192"  # Or another model
```

## Performance Considerations

### Optimization Tips

1. **Reduce token usage:**
   - Smaller prompts
   - Focus examples
   - Concise specifications

2. **Batch operations:**
   - Run multiple test cases in one call
   - Combine agent inputs where possible

3. **Caching:**
   - Save specifications and reuse
   - Cache generated tests

### Expected Runtimes

- Full pipeline: ~2-5 minutes
- Spec Agent: 30-60 seconds
- Codegen Agent: 60-120 seconds
- Test Agent: 30-60 seconds
- Red-Team Agent: 30-60 seconds
- Repair iteration: 60-90 seconds

## Security Considerations

1. **API Key Protection:**
   - Never commit `.env` to version control
   - Use environment variables in production
   - Rotate keys regularly

2. **Input Validation:**
   - Validate HTML before parsing
   - Limit input sizes
   - Monitor resource usage

3. **Output Verification:**
   - Always review agent-generated code
   - Run comprehensive tests
   - Check security implications

## Contributing

To extend this project:

1. Create feature branches
2. Add tests for new functionality
3. Update documentation
4. Submit pull requests

## License

This project is part of a bootcamp exercise. See LICENSE file for details.

## References

- [HTML5 Specification](https://html.spec.whatwg.org/)
- [html5lib-tests](https://github.com/html5lib/html5lib-tests)
- [Groq API](https://console.groq.com/docs/api)
- [Agentic AI Patterns](https://www.groq.com/research/agents)

## Support and Questions

For questions or issues:
1. Check troubleshooting section
2. Review generated reports in `runs/` directory
3. Examine execution traces for debugging
4. Consult inline code comments

---

**Last Updated:** February 2026
**Python Version:** 3.9+
**Groq Model:** Llama 3.3 70B Versatile
