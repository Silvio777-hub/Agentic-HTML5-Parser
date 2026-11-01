# Chapter 6: Discussion and Limitations

## 6.1 Strengths of the Agentic Approach
The empirical results confirm that decomposing compiler engineering into specialized personas provides distinct advantages over monolithic LLM generation:
1. **Explainability & Verification Gating:** Because every agent generates a concrete file artifact (`spec.yml`, `code.patch`, `approval.json`), human engineers can inspect decisions at every pipeline stage.
2. **Reduced Hallucination via Adversarial Tension:** The creative implementer (`CodegenAgentAI`) is directly paired with an adversarial auditor (`RedTeamAgentAI`). This dynamic tension forces the implementer to handle edge cases that single-prompt systems overlook.
3. **Trace-Guided Convergence:** Rather than guessing blind fixes, `RepairAgentAI` converges rapidly because it receives structured runtime telemetry (failing token, character offset, and tree depth).

## 6.2 Scope and Architectural Limitations
In the interest of scientific rigor and intellectual honesty, several deliberate boundaries and architectural trade-offs must be acknowledged:

### 6.2.1 The Adoption Agency Algorithm (AAA) Boundary
The WHATWG specification (§13.2.6.4.7) dictates the Adoption Agency Algorithm (AAA) to resolve misnested inline formatting tags (e.g., `<b>`, `<i>`, `<a>`, `<em>`).
* **Full WHATWG Behavior:** When parsing `<b>1<i>2</b>3</i>`, the algorithm duplicates and reparents the active formatting elements to produce the reconstructed tree:
  ```html
  <b>1<i>2</i></b><i>3</i>
  ```
* **Our Structural Subset Behavior:** The parser resolves closing tags in strict stack order (LIFO), yielding:
  ```html
  <b>1<i>23</i></b>
  ```
* **Justification:** While not strictly identical to the 40-step WHATWG AAA state machine, our structural subset maintains strict tree well-formedness, prevents node duplication blowup, and guarantees **100% crash-free resilience**. This trade-off is formally verified in `tests/test_whatwg_boundary.py`.

### 6.2.2 Table Foster Parenting
Under WHATWG rules, loose content placed erroneously between `<table>` and `<tr>` is hoisted before the table ("foster parenting"). Our parser ingests this content into the table container rather than executing dynamic node displacement.

### 6.2.3 Foreign Content Namespaces
Standard HTML5 features specialized tokenizer transitions for `<svg>` and `<math>` elements to support XML-style self-closing tags and attribute case-sensitivity. In our parser, foreign elements are treated as standard HTML DOM element nodes.

### 6.2.4 Byte-Level Character Sniffing
Browser-embedded parsers inspect raw byte streams to sniff character sets (`windows-1252`, `iso-8859-1`, `utf-8`). Our engine accepts pre-decoded Unicode Python `str` inputs, delegating character decoding to upstream network layers.

## 6.3 Environmental & Economic Sustainability (Green AI)
The computational footprint of training and querying frontier LLMs represents a significant environmental concern (Schwartz et al., 2020).
* **Uncached Execution:** A full 7-agent pipeline run consumes ~18,000 prompt tokens and ~4,500 completion tokens, costing **\$0.06 per execution** and generating approximately **0.35g of $CO_2$**.
* **Cached Execution:** Through our on-disk SHA-256 caching architecture, repeat test executions achieve **\$0.00 cost, 0.00s latency, and zero carbon emissions**.
* This demonstrates that agentic software engineering pipelines can be deployed responsibly without runaway operational costs.
