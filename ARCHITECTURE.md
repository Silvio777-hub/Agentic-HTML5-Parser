# Architecture & Design Documentation

## System Architecture Overview

### High-Level Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     INPUT: HTML5 SUBSET                          │
│           (Human-written specification fragment)                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │   SPEC AGENT     │  (Llama 3.3 70B (Groq))
                   │ (Interpretation) │
                   └────────┬─────────┘
                            │
                            ├─→ spec.yml (YAML rules)
                            │
                            ▼
                   ┌──────────────────┐
                   │  CODEGEN AGENT   │  (Llama 3.3 70B (Groq))
                   │ (Implementation) │
                   └────────┬─────────┘
                            │
                            ├─→ code.patch (unified diff)
                            │
                            ▼
                   ┌──────────────────┐
                   │ CRITIQUE AGENT   │  (Llama 3.3 70B (Groq))
                   │ (Validation)     │
                   └────────┬─────────┘
                            │
                            ├─→ approval.json
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
   ┌─────────────┐                     ┌──────────────────┐
   │ TEST AGENT  │                     │ RED-TEAM AGENT   │
   │  (Conformance)                    │ (Security Focus) │
   └──────┬──────┘                     └────────┬─────────┘
          │                                     │
          ├─→ test_parser.py                    ├─→ test_red_team.py
          │                                     │
          └─────────────┬───────────────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │   TEST EXECUTOR        │
            │ (Pytest Runner)        │
            └────────┬───────────────┘
                     │
                     ├─→ test_report.json
                     │
                     ▼
            ┌────────────────────────┐
            │  MONITOR AGENT         │  (Llama 3.3 70B (Groq))
            │ (Performance Analysis) │
            └────────┬───────────────┘
                     │
                     ├─→ health_analysis.json
                     │
          ┌──────────▼──────────┐
          │ Tests Passed? ──────┤──────YES──────┐
          └──────────┬──────────┘               │
                     │ NO                       │
                     ▼                          │
            ┌────────────────────┐              │
            │  REPAIR AGENT      │              │
            │ (Failure Fixes)    │              │
            └────────┬───────────┘              │
                     │                          │
                     ├─→ repair_N.patch         │
                     │                          │
        ┌────────────▼────────────┐             │
        │ Reapply Patch & Retest  │             │
        │ (Loop ≤ 3 iterations)   │             │
        └────────────┬────────────┘             │
                     │                          │
                     └──────────┬───────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │     SUCCESS!         │
                     │  Functional Parser   │
                     │  Comprehensive Tests │
                     │  Security Analysis   │
                     └──────────────────────┘
```

---

## Component Architecture

### Core Modules

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│              (Pipeline Coordinator)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Manages agent execution sequence                  │   │
│  │ • Collects and stores artifacts                     │   │
│  │ • Handles error recovery                            │   │
│  │ • Reports progress and results                      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────┬───────────────────────────────────┬──────────┘
               │                                   │
        ┌──────▼──────────────────┐        ┌──────▼──────┐
        │   AI AGENT WRAPPERS     │        │  UTILITIES  │
        │   (claude_integration) │        │             │
        ├────────────────────────┤        ├─────────────┤
        │ • GroqAgent (base)   │        │ • Artifact  │
        │ • SpecAgentAI          │        │   Manager   │
        │ • CodegenAgentAI       │        │ • Patch     │
        │ • CritiqueAgentAI      │        │   Manager   │
        │ • TestAgentAI          │        │ • Report    │
        │ • RedTeamAgentAI       │        │   Generator │
        │ • MonitorAgentAI       │        └─────────────┘
        │ • RepairAgentAI        │
        └───────────────┬────────┘
                        │
                 ┌──────▼──────────┐
                 │   CLAUDE API    │
                 │  (Groq)    │
                 │ claude-3-5      │
                 │ sonnet-20241022 │
                 └─────────────────┘
```

### Parser Module Architecture

```
┌──────────────────────────────────────────────────────┐
│              PARSER MODULE (src/parser.py)           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │         ParsingTrace                        │    │
│  │ ┌──────────────────────────────────────┐    │    │
│  │ │ • Events list                        │    │    │
│  │ │ • Parse errors                       │    │    │
│  │ │ • Tokenizer states                   │    │    │
│  │ │ • Timing information                 │    │    │
│  │ └──────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────┘    │
│           ▲                          ▲               │
│           │                          │               │
│  ┌────────┴──────────┐  ┌────────────┴──────────┐   │
│  │ HTMLTokenizer     │  │ HTMLParser            │   │
│  │                   │  │                       │   │
│  │ • 8 states        │  │ • Tree construction   │   │
│  │ • Token creation  │  │ • Implicit closure    │   │
│  │ • Attribute parse │  │ • Stack management    │   │
│  │ • Trace recording │  │ • Trace recording     │   │
│  └────────┬──────────┘  └────────┬──────────────┘   │
│           │                      │                  │
│           ▼                      ▼                  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Token Structure    │ TreeNode Structure       │  │
│  │ • type            │ • name                    │  │
│  │ • name            │ • attributes              │  │
│  │ • attributes      │ • children                │  │
│  │ • data            │ • text_content            │  │
│  │ • self_closing    │ • parent reference        │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  Public Interface:                                 │
│  • tokenize(html) → List[Token]                   │
│  • parse(html) → TreeNode                         │
│  • parse_with_trace(html) → Dict                  │
└──────────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

### Specification Flow

```
HTML Subset Description
        │
        ▼
   ┌─────────────────────────────────────┐
   │  Spec Agent AI                      │
   │  • Interprets requirements          │
   │  • Generates rules                  │
   │  • Defines test cases               │
   └────────┬────────────────────────────┘
            │
            ├─ YAML parsing
            │
            ▼
    spec.yml (YAML)
    ├─ name
    ├─ version
    ├─ rules
    │  ├─ tokenizer
    │  │  ├─ states
    │  │  └─ transitions
    │  ├─ parser
    │  │  ├─ tag_closure
    │  │  └─ error_handling
    │  └─ conformance
    └─ test_cases
```

### Code Generation Flow

```
spec.yml + Current Implementation
            │
            ▼
   ┌─────────────────────────────────────┐
   │  Codegen Agent AI                   │
   │  • Reads specification              │
   │  • Generates Python code            │
   │  • Creates unified diff             │
   └────────┬────────────────────────────┘
            │
            ├─ Diff generation
            │
            ▼
    code.patch (Unified Diff)
    --- a/src/parser.py
    +++ b/src/parser.py
    @@ -120,6 +120,12 @@
    + New code implementation
    + With inline comments
    
            │
            ├─ git apply
            │
            ▼
    Modified src/parser.py
```

### Test Generation Flow

```
spec.yml
  │
  ├──────────────────┬──────────────────┐
  │                  │                  │
  ▼                  ▼                  ▼
  
Test Agent      Red-Team Agent      Critique Agent
  │                  │                  │
  ├─ Conformance     ├─ Adversarial    ├─ Code Review
  ├─ Edge cases      ├─ Malformed      └─ Specification
  └─ Error handling  └─ Performance          alignment

  │                  │                  │
  └──────────┬───────┴──────────┬───────┘
             │                  │
             ▼                  ▼
    test_parser.py    test_red_team.py
    (32 tests)        (20+ security tests)
             │                  │
             └──────────┬───────┘
                        │
                        ▼
                   Test Execution
                   (Pytest)
                        │
                   ┌────┴────┐
                   │          │
                   ▼          ▼
              Passed      Failed
                │             │
                ▼             ▼
             SUCCESS    Repair Loop
```

---

## Artifact Management Architecture

```
┌────────────────────────────────────────────────────┐
│            Artifact Manager                        │
├────────────────────────────────────────────────────┤
│                                                    │
│  Run Directory: runs/[RUN_ID]/                    │
│  │                                                │
│  ├─ spec/                                        │
│  │  └─ spec.yml                 (YAML)           │
│  │                                                │
│  ├─ patches/                                     │
│  │  ├─ code.patch              (Unified Diff)    │
│  │  ├─ tests.patch             (Unified Diff)    │
│  │  ├─ repair_1.patch          (Unified Diff)    │
│  │  └─ repair_2.patch          (Unified Diff)    │
│  │                                                │
│  ├─ reports/                                     │
│  │  ├─ pipeline_report.json    (Complete)        │
│  │  ├─ test_report.json        (Test Results)    │
│  │  ├─ critique_report.json    (Code Review)     │
│  │  └─ monitor_report.json     (Performance)     │
│  │                                                │
│  └─ traces/                                      │
│     ├─ execution_1.json        (Trace Events)    │
│     ├─ execution_2.json        (Trace Events)    │
│     └─ execution_3.json        (Trace Events)    │
│                                                    │
│  Each artifact:                                   │
│  • Is versioned and time-stamped                 │
│  • Can be reviewed independently                 │
│  • Is preserved for audit trail                  │
│  • Enables reproducibility                       │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Agent Communication Protocol

### Message Format

```python
┌──────────────────────────────────────────────────────┐
│           Agent Input (Message)                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  system_prompt: str  (Role definition)              │
│  user_message: str   (Task instructions)            │
│  context: Dict       (Optional previous output)     │
│  temperature: float  (Task-specific: 0.2-0.9)       │
│                                                      │
└──────────────────────────────────────────────────────┘

         │
         │ Claude API Call
         ▼

┌──────────────────────────────────────────────────────┐
│           Agent Output (Response)                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Each agent utilizes a specialized prompt and interacts with an LLM (Llama 3.3 70B via Groq) │
│  to perform its specific task within the pipeline.                                          │
│                                                                                            │
│  1.  **Spec Agent**: Uses Groq to interpret HTML subsets and produce YAML specifications.  │
│  Examples:                                           │
│  • Unified diff patch (Codegen Agent)               │
│  • JSON approval report (Critique Agent)            │
│  • Python test code (Test Agent)                    │
│  • Adversarial test code (Red-Team Agent)           │
│  • JSON analysis (Monitor Agent)                    │
│  • Patch content (Repair Agent)                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## State Machine: Tokenizer States

```
                    ┌─────────────────┐
                    │  START (DATA)   │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
         [a-z]              [<]             [EOF]
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────────┐  ┌─────────────┐  [EMIT TOKEN]
    │[CHARACTER]   │  │ TAG_OPEN    │
    │EMIT CHAR     │  └──────┬──────┘
    │              │         │
    └──────┬───────┘    ┌────┼────┐
           │            │    │    │
           └────┐       [/]  [!]  [a-z]
                │       │    │    │
                │   ┌───┘    │    └─────┐
                │   │        │          │
                │   ▼        ▼          ▼
                │   TAG_NAME TAG_NAME  BOGUS_COMMENT
                │   (END)    (DOCTYPE)
                │   │        │
                └───┼────┬───┴────┐
                    │    │        │
                  [>]  [>]   [EOF]
                    │    │        │
                    └────┼────────┘
                         │
                ┌────────▼──────────┐
                │ EMIT TAG TOKEN    │
                │ Return to DATA    │
                └───────────────────┘
```

---

## Repair Loop Architecture

```
┌──────────────────────────────────────┐
│       Test Execution                 │
│    (32 tests × 2 test suites)        │
└────────────┬───────────────────────┘
             │
             ├─ Pass
             │
    ┌────────▼──────────┐
    │ All Tests Passed? │
    └────────┬──────────┘
             │
        ┌────┴────┐
      YES         NO
        │          │
        ▼          ▼
     SUCCESS    ┌─────────────────────────────┐
                │  Collect Failure Evidence   │
                │  • Failed test names        │
                │  • Error messages           │
                │  • Execution traces         │
                │  • Performance metrics      │
                └────────┬────────────────────┘
                         │
                         ▼
                ┌─────────────────────────────┐
                │  Repair Agent AI            │
                │  • Analyzes failures        │
                │  • Identifies root cause    │
                │  • Generates repair patch   │
                │  • Adds inline comments     │
                └────────┬────────────────────┘
                         │
                         ▼
                ┌─────────────────────────────┐
                │  Apply Repair Patch         │
                │  (git apply)                │
                └────────┬────────────────────┘
                         │
                         ▼
                ┌─────────────────────────────┐
                │  Re-run Tests               │
                │  (Iteration N+1)            │
                └────────┬────────────────────┘
                         │
           ┌─────────────┴──────────────┐
           │                            │
      Improvement?              Max Iterations?
        (Tests up)               (Limit: 3)
           │                            │
        YES│                           NO
           │                            │
           ▼                            ▼
        Loop Back              ┌──────────────┐
                               │  Try Manual  │
                               │  Fixes or    │
                               │  Refactor    │
                               └──────────────┘
```

---

## Configuration Hierarchy

```
Default Values (config.py)
    ↓
Environment Variables (.env)
    ↓
Runtime Parameters (orchestrator.py)
    ↓
Effective Configuration
```

**Configuration Scope:**

```
System-wide (config.py)
├─ API keys
├─ Model selection
├─ Token limits
├─ Timeout thresholds
├─ Directory paths
└─ The interface to Groq is encapsulated in `src/groq_integration.py`. This module provides 
   a `GroqAgent` class that handles the API calls, including retry logic and 
   conversation history management.

- **Model**: Llama-3.3-70b-versatile
Per-Agent (groq_integration.py)
├─ System prompts
├─ Task-specific temperature
├─ Input constraints
└─ Output parsing rules

Per-Run (orchestrator.py)
├─ Run ID
├─ HTML subset
├─ Parser interface
├─ Max repair iterations
└─ Test suite selection
```

---

## Performance Characteristics

### Response Time Profile

```
Agent              Min      Avg      Max    Notes
─────────────────────────────────────────────────────
Spec Agent        20s      45s      90s    Complex interpretation
Codegen Agent     40s      90s     180s    Requires code quality
Critique Agent    15s      40s      80s    Focused task
Test Agent        20s      45s      90s    Multiple test cases
Red-Team Agent    25s      50s     100s    Creative generation
Monitor Agent     10s      35s      70s    Trace analysis
Repair Agent      30s      60s     120s    Debugging required

Full Pipeline    220s     395s     730s    Depends on repairs
```

### Resource Usage Profile

```
Memory: 200-500 MB
Disk: 50-100 MB per run
Network: 2-5 MB per agent call
CPU: Moderate (waits on API)
```

---

## Error Handling Architecture

```
┌──────────────────────────────────────────┐
│  Error Detection Points                  │
├──────────────────────────────────────────┤
│                                          │
│  Agent Call Failed                       │
│  ├─ API error → Retry with fallback      │
│  ├─ Timeout → Return cached result       │
│  ├─ Invalid response → Log and continue  │
│  └─ Rate limit → Wait and retry          │
│                                          │
│  Patch Application Failed                │
│  ├─ Conflict detected → Manual review    │
│  ├─ Invalid format → Validate and fix    │
│  └─ Out of order → Reorder patches       │
│                                          │
│  Test Execution Failed                   │
│  ├─ Syntax error → Fix automatically     │
│  ├─ Import error → Check dependencies    │
│  └─ Runtime error → Trigger repair       │
│                                          │
│  Parser Execution Failed                 │
│  ├─ Timeout → Mark as robustness issue   │
│  ├─ Stack overflow → Reduce depth limit  │
│  └─ Memory exhaustion → Optimize         │
│                                          │
└──────────────────────────────────────────┘
```

---

## Extension Points

### Adding a New Agent

```
New Agent Class
├─ Inherit from GroqAgent-like pattern
├─ Define system_prompt
├─ Implement input_validation()
├─ Implement parse_response()
└─ Add to orchestrator pipeline

New Test Category
├─ Create test_*.py file
├─ Use pytest framework
├─ Add to TestAgentAI prompt
└─ Include in test_runner

New Metric
├─ Add to ParsingTrace
├─ Track in executor
├─ Report in MonitorAgent
└─ Visualize in reports
```

---

**Last Updated:** February 24, 2026
