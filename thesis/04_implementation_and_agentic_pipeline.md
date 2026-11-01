# Chapter 4: Implementation and the Agentic Pipeline

## 4.1 Parser Engine Implementation
The synthesized parser engine resides in `src/parser.py`. It is a pure-Python library designed with **zero runtime dependencies**, ensuring high portability and embeddability.

### 4.1.1 The Tokenizer Finite State Machine
The lexical scanner operates as an explicit Finite State Machine. The principal states include:
* `DATA`: Reads raw text characters until an open angle bracket (`<`) or ampersand (`&`) is encountered.
* `TAG_OPEN`: Dispatches to `TAG_NAME`, `END_TAG_OPEN` (`</`), `COMMENT_START` (`<!--`), or `DOCTYPE`.
* `TAG_NAME`: Accumulates tag identifiers in a case-insensitive manner.
* `BEFORE_ATTRIBUTE_NAME`: Consumes whitespace and dispatches to attribute key parsing.
* `ATTRIBUTE_VALUE_QUOTED` / `UNQUOTED`: Extracts attribute values with proper entity replacement.
* `RAWTEXT`: Specialized state for `<script>`, `<style>`, `<textarea>`, and `<title>` where standard HTML tag parsing is suspended until the corresponding closing tag is found.

### 4.1.2 Tree Construction & DOM Data Structures
The parser produces an AST composed of `TreeNode` objects:
```python
class TreeNode:
    def __init__(self, name: str, attributes: dict = None, parent: 'TreeNode' = None):
        self.name = name.lower()
        self.attributes = attributes or {}
        self.children = []
        self.parent = parent
        self.text_content = ""
```
The tree constructor maintains a stack of open elements. To handle HTML5 structural subsets correctly:
1. **Implicit Paragraph Closure:** Encountering a block-level start tag (`<div>`, `<blockquote>`, `<section>`, `<h1>`–`<h6>`, `<table>`, `<ul>`, `<ol>`) automatically pops open `<p>` elements from the active stack.
2. **Void Element Handling:** Elements such as `<img>`, `<br>`, `<hr>`, `<input>`, `<meta>` are appended as leaf nodes without being pushed onto the active ancestor stack.
3. **Attribute Merging:** Duplicate `<html>` or `<body>` tags merge attributes into the root node rather than generating redundant nested containers.

### 4.1.3 Streaming & Incremental API
To support large web documents and real-time network streams, the engine exposes generator-based streaming functions:
* `tokenize_stream(stream)`: Yields `HTMLToken` instances on-the-fly as chunks arrive from a socket.
* `parse_stream(stream)`: Progressively constructs and links DOM nodes without buffering the entire HTML string into RAM.

### 4.1.4 Reverse HTML Serialization & Query Engine
* **DOM Querying:** Implements modern selector methods: `.find()`, `.find_all()`, `.select()`, and `.select_one()`, supporting tag names, IDs (`#id`), classes (`.class`), and attribute filters (`[attr=val]`).
* **Reverse Serializer (`to_html`):** Emits valid HTML5 markup with optional indentation formatting (`pretty=True`), correctly omitting closing tags for void elements.

## 4.2 Multi-Agent Orchestration Engine
The end-to-end orchestration pipeline is implemented in `orchestrator.py` and managed via `src/claude_integration.py`.

### 4.2.1 LLM Provider Abstraction
To avoid vendor lock-in and enable offline execution, the system employs an abstract LLM interface (`src/llm_provider.py`) supporting:
1. **Anthropic Claude:** Primary model (`claude-3-5-sonnet-20241022`).
2. **Groq Llama 3.3 70B:** High-throughput open-weights fallback.
3. **Local Ollama:** Fully offline local deployment.
4. **Mock Provider:** Deterministic, network-independent replay provider for CI environments.

### 4.2.2 Execution Telemetry & Tracing
The function `parse_with_trace(html_string)` captures comprehensive execution telemetry:
* Start, tokenizer completion, and tree completion timestamps.
* Token count and memory allocations.
* Step-by-step state transition logs.
* Unclosed stack traces on syntax anomalies.

This structured trace serves as the diagnostic substrate consumed by `MonitorAgentAI` and `RepairAgentAI`.

## 4.3 Extensible Plugin Architecture
To allow domain-specific customization without modifying core parser source code, a `PluginManager` (`src/plugin_manager.py`) was implemented:
* Plugins are discovered via `plugins/*/plugin.yml` metadata manifests.
* Supports lifecycle hooks: `on_token_emitted`, `on_node_created`, and `on_document_parsed`.
* Example: `plugins/example_lint/` audits deprecated tags (`<center>`, `<font>`, `<marquee>`, `<blink>`), generating non-fatal linter warnings.
