"""
cli.py — Master Unified Command-Line Interface.

Single control center for the Agentic AI HTML5 Parser thesis project:
Provides easy 1-command access to all verification, benchmarking,
repair demos, chart generation, and dashboard servers.

Usage Examples:
    python cli.py dashboard            # Launches live dashboard & playground at http://localhost:8080/dashboard/
    python cli.py test                 # Runs all 70 automated unit & streaming & WHATWG boundary tests
    python cli.py compliance           # Runs W3C html5lib compliance test harness
    python cli.py benchmark            # Runs comparative performance benchmarks vs BeautifulSoup & lxml
    python cli.py adversarial          # Runs Red-Team hacker stress tests
    python cli.py ablation             # Runs empirical ablation study experiments
    python cli.py charts               # Generates all 300-DPI thesis figures
    python cli.py carbon               # Runs Green AI carbon footprint assessment
    python cli.py audit                # Runs AST security analysis & STRIDE audit
    python cli.py repair-demo          # Runs the live self-repair showcase demonstration
    python cli.py build-thesis         # Verifies all 7 thesis chapters in thesis/
    python cli.py parse "<html>..."    # Parse inline HTML and print DOM tree / JSON / tokens
    python cli.py lint <file.html>     # Lint an HTML file and report structural issues
    python cli.py orchestrate          # Run the full 7-agent agentic pipeline end-to-end
    python cli.py repl                 # Drop into the interactive HTML5 Parser REPL
    python cli.py all                  # Executes the entire pipeline and builds all assets
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_command(cmd_list, description):
    """Helper function to execute a sub-process command and handle errors."""
    print(f"\n>>> [CLI] Executing: {description} ...")
    # Execute the requested script in a subprocess with working directory pinned to project root
    result = subprocess.run(cmd_list, cwd=str(PROJECT_ROOT))
    # Non-zero return code indicates test failure, crash, or execution exception
    if result.returncode != 0:
        print(f"[FAIL] [CLI] Command failed with returncode {result.returncode}")
        return False
    return True


def cmd_test():
    """Runs all 70 automated unit, integration, and streaming tests."""
    # Invokes pytest directly using the current Python interpreter environment
    return run_command([sys.executable, "-m", "pytest", "tests/", "-v"], "Automated Test Suite (pytest)")


def cmd_compliance():
    """Runs W3C html5lib compliance test harness."""
    upstream_dir = os.path.join(os.path.dirname(__file__), "html5lib-tests", "tree-construction")
    if os.path.exists(upstream_dir) and any(os.scandir(upstream_dir)):
        return run_command([sys.executable, "scripts/run_compliance.py"], "W3C Compliance Test Runner (Official Upstream)")
    return run_command([sys.executable, "scripts/run_compliance.py", "--sample"], "W3C Compliance Test Runner (Sample)")


def cmd_benchmark():
    """Runs comparative benchmarks against BeautifulSoup4 and lxml."""
    # Measures document parsing latency, throughput, and memory consumption
    return run_command([sys.executable, "scripts/compare_benchmarks.py"], "Comparative Benchmark Suite")


def cmd_adversarial():
    """Runs Red-Team adversarial security tests."""
    # Probes the parser with 15 malicious attack vectors (XSS, nesting, zero-width chars)
    return run_command([sys.executable, "scripts/run_adversarial.py"], "Red-Team Adversarial Robustness Suite")


def cmd_ablation():
    """Runs empirical multi-agent ablation study."""
    # Systematically disables agents (Critique, Red-Team, Repair) to measure their empirical impact
    return run_command([sys.executable, "scripts/run_ablation_study.py"], "Empirical Ablation Study Runner")


def cmd_charts():
    """Generates all 300-DPI publication figures."""
    # Renders high-resolution vector and raster charts in figures/ for the thesis document
    return run_command([sys.executable, "scripts/generate_thesis_charts.py"], "300-DPI Publication Figure Generator")


def cmd_carbon():
    """Runs computational carbon footprint & energy assessment."""
    # Quantifies Joules and estimated CO2 emissions for uncached vs cached LLM operations
    return run_command([sys.executable, "scripts/estimate_carbon.py"], "Green AI Carbon Footprint Estimator")


def cmd_audit():
    """Runs AST static security analysis and STRIDE threat modeling."""
    # Scans Python AST for dangerous functions (eval, exec) and audits against STRIDE threats
    return run_command([sys.executable, "scripts/run_security_audit.py"], "Static Security & STRIDE Auditor")


def cmd_repair_demo():
    """Runs the live self-repair showcase demo."""
    # Demonstrates an automated end-to-end failure detection and trace-guided patching cycle
    return run_command([sys.executable, "scripts/demo_self_repair.py"], "Autonomous Self-Repair Showcase Demo")


def cmd_build_thesis():
    """Verifies that all 7 thesis chapters exist in thesis/."""
    # Checks that all 7 numbered chapter Markdown documents are present in thesis/
    thesis_dir = Path("thesis")
    chapters = list(thesis_dir.glob("0*.md"))
    if len(chapters) == 7:
        print(f"  Thesis chapters verified: {len(chapters)} chapters present in thesis/")
        return True
    print(f"  Thesis directory missing chapters in {thesis_dir}")
    return False


def cmd_matrix():
    """Runs full W3C upstream functional compliance matrix across 6 buckets."""
    return run_command([sys.executable, "scripts/run_upstream_matrix.py"], "W3C Upstream Functional Compliance Matrix")


def cmd_dashboard(port=8080, no_browser=False):
    """Starts the local web server and live playground API."""
    # Builds server command line with configurable TCP port
    cmd = [sys.executable, "scripts/serve_dashboard.py", "--port", str(port)]
    if no_browser:
        # Suppress automatic browser tab opening if requested (e.g. in headless environments)
        cmd.append("--no-browser")
    return run_command(cmd, "Live Quality Dashboard & API Server")


def cmd_parse(html_string, output_format="tree"):
    """
    Parse an inline HTML string and print the result in the requested format.

    Args:
        html_string:   HTML markup to parse
        output_format: 'tree' (default), 'json', or 'tokens'
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from src.parser import parse, tokenize

    if output_format == "tokens":
        tokens = tokenize(html_string)
        print(f"\n{'='*60}")
        print(f"  TOKEN STREAM ({len(tokens)} tokens)")
        print(f"{'='*60}")
        for i, tok in enumerate(tokens, 1):
            attrs = f"  attrs={tok.attributes}" if tok.attributes else ""
            data = f"  data={repr(tok.data)}" if tok.data else ""
            print(f"  [{i:02d}] {tok.type.value:<14} name={tok.name or '':<16}{attrs}{data}")
        return True

    root = parse(html_string)

    if output_format == "json":
        import json
        print(json.dumps(root.serialize(), indent=2))
        return True

    if output_format == "html":
        print(f"\n{'='*60}")
        print("  REVERSE SERIALIZED HTML (to_html)")
        print(f"{'='*60}")
        print(root.to_html(pretty=True))
        return True

    # Default: tree format
    def _print_tree(node, indent=0):
        prefix = "  " * indent
        if node.name == "#text":
            print(f"{prefix}|-- #text: {repr(node.text_content)}")
        else:
            attrs = ""
            if node.attributes:
                attrs = " " + " ".join(f'{k}="{v}"' for k, v in node.attributes.items())
            print(f"{prefix}|-- <{node.name}{attrs}>")
        for child in node.children:
            _print_tree(child, indent + 1)

    print(f"\n{'='*60}")
    print("  PARSED DOM TREE")
    print(f"{'='*60}")
    _print_tree(root)
    return True


def cmd_lint(filepath, output_format="tree"):
    """
    Lint an HTML file and report structural issues and DOM outline.

    Args:
        filepath:      Path to HTML file to lint
        output_format: 'tree' (default), 'json', or 'tokens'
    """
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from src.parser import parse, tokenize

    fpath = _Path(filepath)
    if not fpath.exists():
        print(f"[ERROR] File not found: {filepath}")
        return False

    html_string = fpath.read_text(encoding="utf-8", errors="replace")
    print(f"\n{'='*60}")
    print(f"  HTML LINTER: {fpath.name}")
    print(f"  File size:   {len(html_string)} characters")
    print(f"{'='*60}")

    root = parse(html_string)
    tokens = tokenize(html_string)

    # Structural checks
    warnings = []

    def _collect_tags(node, seen=None):
        if seen is None:
            seen = []
        seen.append(node.name)
        for c in node.children:
            _collect_tags(c, seen)
        return seen

    all_tags = _collect_tags(root)
    if "html" not in all_tags:
        warnings.append("Missing <html> root element")
    if "head" not in all_tags:
        warnings.append("Missing <head> element")
    if "body" not in all_tags:
        warnings.append("Missing <body> element")
    if "title" not in all_tags:
        warnings.append("Missing <title> element inside <head>")

    # Check for unclosed implicit paragraphs heuristic
    open_p = sum(1 for tok in tokens if tok.type.value == "StartTag" and tok.name == "p")
    close_p = sum(1 for tok in tokens if tok.type.value == "EndTag" and tok.name == "p")
    if open_p > close_p:
        warnings.append(f"Implicit <p> closure: {open_p} opened, {close_p} explicit closes (W3C auto-closure applied)")

    if warnings:
        print(f"\n  [!]  {len(warnings)} structural notice(s):")
        for w in warnings:
            print(f"     - {w}")
    else:
        print("\n  [OK] No structural issues detected.")

    print(f"\n  Tokens emitted: {len(tokens)}")
    print(f"  DOM nodes:      {len(all_tags)}")

    # Print the DOM tree
    print()
    return cmd_parse(html_string, output_format=output_format)


def cmd_orchestrate():
    """
    Run the full 7-agent agentic AI orchestration pipeline.

    Executes: Spec → Codegen → Critique || Red-Team (parallel) →
              Test → Monitor → iterative Repair (≤ 3 loops).
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from orchestrator import main as orchestrator_main
        print("\n>>> [CLI] Launching full 7-agent Orchestration Pipeline ...")
        orchestrator_main()
        return True
    except Exception as exc:
        print(f"[FAIL] Orchestration pipeline error: {exc}")
        return False


def cmd_repl():
    """
    Interactive HTML5 Parser REPL (Read-Eval-Print Loop).

    Commands available at the prompt:
      :tree       — Print the parsed DOM tree
      :json       — Print DOM as JSON
      :html       — Serialise DOM back to HTML (round-trip)
      :tokens     — Print the raw token stream
      :select <css> — Run a CSS selector query
      :find <tag>   — Find first element by tag name
      :findall <tag> — Find all elements by tag name
      :text       — Extract all visible text
      :quit / :exit — Exit the REPL
      (anything else) — Re-parse the current HTML with any edits appended

    Type a new HTML string at the prompt to load it, then use the
    commands above to inspect the result.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.parser import parse, tokenize
    import json as _json

    BANNER = """
\033[1;36m╔══════════════════════════════════════════════════════════╗
║        Agentic HTML5 Parser  —  Interactive REPL          ║
║  Type HTML to parse it.  Commands: :tree :json :html      ║
║  :tokens :select <css> :find <tag> :text :quit            ║
╚══════════════════════════════════════════════════════════╝\033[0m"""

    print(BANNER)
    current_html = ""
    current_root = None

    def _print_tree(node, indent=0):
        prefix = "  " * indent
        if node.name == "#text":
            print(f"{prefix}|-- #text: {repr(node.text_content)}")
        elif node.name == "#comment":
            print(f"{prefix}|-- <!-- {node.text_content[:60]} -->")
        else:
            attrs = ""
            if node.attributes:
                attrs = " " + " ".join(f'{k}="{v}"' for k, v in node.attributes.items()
                                       if not k.startswith("_"))
            print(f"{prefix}|-- <{node.name}{attrs}>")
        for child in node.children:
            _print_tree(child, indent + 1)

    while True:
        try:
            line = input("\033[32mhtml> \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[REPL] Exiting.")
            break

        if not line:
            continue

        # --- Commands ---
        if line in (":quit", ":exit", ":q"):
            print("[REPL] Goodbye.")
            break

        elif line == ":tree":
            if current_root is None:
                print("[REPL] No HTML loaded. Type an HTML string first.")
            else:
                print(f"\n{'='*60}")
                print("  PARSED DOM TREE")
                print(f"{'='*60}")
                _print_tree(current_root)

        elif line == ":json":
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                print(_json.dumps(current_root.serialize(), indent=2))

        elif line == ":html":
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                print(f"\n{'='*60}")
                print("  ROUND-TRIP HTML (to_html)")
                print(f"{'='*60}")
                print(current_root.to_html(pretty=True))

        elif line == ":tokens":
            if not current_html:
                print("[REPL] No HTML loaded.")
            else:
                tokens = tokenize(current_html)
                print(f"\n{'='*60}")
                print(f"  TOKEN STREAM ({len(tokens)} tokens)")
                print(f"{'='*60}")
                for i, tok in enumerate(tokens, 1):
                    attrs = f"  attrs={tok.attributes}" if tok.attributes else ""
                    data = f"  data={repr(tok.data)}" if tok.data else ""
                    print(f"  [{i:02d}] {tok.type.value:<14} name={tok.name or '':<16}{attrs}{data}")

        elif line == ":text":
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                print(repr(current_root.get_text(separator=" ", strip=True)))

        elif line.startswith(":select "):
            selector = line[8:].strip()
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                results = current_root.select(selector)
                print(f"[REPL] select({repr(selector)}) → {len(results)} result(s)")
                for node in results:
                    _print_tree(node, indent=1)

        elif line.startswith(":find "):
            tag = line[6:].strip()
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                node = current_root.find(tag)
                if node:
                    _print_tree(node, indent=1)
                else:
                    print(f"[REPL] No <{tag}> found.")

        elif line.startswith(":findall "):
            tag = line[9:].strip()
            if current_root is None:
                print("[REPL] No HTML loaded.")
            else:
                nodes = current_root.find_all(tag)
                print(f"[REPL] find_all({repr(tag)}) → {len(nodes)} result(s)")
                for node in nodes:
                    _print_tree(node, indent=1)

        elif line.startswith(":"):
            print(f"[REPL] Unknown command: {line}.  Type :quit to exit.")

        else:
            # Treat input as HTML to parse
            current_html = line
            try:
                current_root = parse(current_html)
                tokens = tokenize(current_html)
                print(f"[REPL] Parsed {len(current_html)} chars → "
                      f"{len(tokens)} tokens, root=<{current_root.name}>")
                _print_tree(current_root)
            except Exception as exc:
                print(f"[REPL] Parse error: {exc}")

    return True


def cmd_all():
    """Runs the entire verification, benchmarking, and asset generation pipeline."""
    print("=" * 75)
    print("  EXECUTING COMPLETE MASTER AGENTIC AI HTML5 PARSER PIPELINE")
    print("=" * 75)
    
    steps = [
        ("Testing", cmd_test),
        ("Compliance", cmd_compliance),
        ("W3C Matrix", cmd_matrix),
        ("Adversarial", cmd_adversarial),
        ("Benchmarking", cmd_benchmark),
        ("Ablation Study", cmd_ablation),
        ("Carbon Assessment", cmd_carbon),
        ("Security Audit", cmd_audit),
        ("Self-Repair Demo", cmd_repair_demo),
        ("Figure Generation", cmd_charts),
        ("Thesis Compilation", cmd_build_thesis)
    ]

    for name, step_fn in steps:
        success = step_fn()
        if not success:
            print(f"\n[FAIL] Pipeline failed during step: {name}")
            return False

    print("\n" + "=" * 75)
    print("  [OK] COMPLETE PIPELINE EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")
    print("  [NOTE] Live Dashboard:   python cli.py dashboard")
    print("  [NOTE] Parse Utility:    python cli.py parse \"<p>Hello</p>\" --format tree|json|tokens")
    print("  [NOTE] Lint Utility:     python cli.py lint <file.html>")
    print("  [NOTE] Thesis Chapters:  thesis/ (All 7 chapters present)")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Master Unified CLI for Agentic AI HTML5 Parser Thesis Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  test          Run all 70 automated unit, streaming & WHATWG boundary tests
  compliance    Run W3C compliance test harness
  matrix        Run 6-bucket W3C functional compliance matrix
  benchmark     Run performance benchmarks vs BeautifulSoup & lxml
  adversarial   Run Red-Team hacker stress tests
  ablation      Run empirical ablation study experiments
  charts        Generate all 300-DPI publication figures
  carbon        Run computational carbon footprint assessment
  audit         Run AST security analysis & STRIDE audit
  repair-demo   Run the live self-repair showcase demonstration
  build-thesis  Verify all 7 thesis chapters in thesis/
  dashboard     Launch live dashboard & playground server
  parse         Parse inline HTML and print DOM tree / JSON / tokens
  lint          Lint an HTML file and report structural issues
  orchestrate   Run the full 7-agent agentic AI pipeline end-to-end
  repl          Drop into the interactive HTML5 Parser REPL
  all           Run complete pipeline end-to-end

Parse / Lint Examples:
  python cli.py parse "<p>Hello <b>World</b></p>"
  python cli.py parse "<p>Hello</p>" --format json
  python cli.py parse "<p>Hello</p>" --format tokens
  python cli.py lint index.html
  python cli.py lint index.html --format json
        """
    )
    parser.add_argument("command", choices=[
        "test", "compliance", "matrix", "benchmark", "adversarial", "ablation",
        "charts", "carbon", "audit", "repair-demo", "build-thesis",
        "dashboard", "parse", "lint", "orchestrate", "repl", "all"
    ], help="Command to execute")
    parser.add_argument("--port", type=int, default=8080, help="Port for dashboard server (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser on dashboard launch")
    parser.add_argument("--format", choices=["tree", "json", "tokens", "html"], default="tree",
                        help="Output format for parse/lint commands (default: tree)")
    parser.add_argument("html_or_file", nargs="?", default=None,
                        help="HTML string (for parse) or file path (for lint)")

    args = parser.parse_args()

    if args.command == "test":
        cmd_test()
    elif args.command == "compliance":
        cmd_compliance()
    elif args.command == "matrix":
        cmd_matrix()
    elif args.command == "benchmark":
        cmd_benchmark()
    elif args.command == "adversarial":
        cmd_adversarial()
    elif args.command == "ablation":
        cmd_ablation()
    elif args.command == "charts":
        cmd_charts()
    elif args.command == "carbon":
        cmd_carbon()
    elif args.command == "audit":
        cmd_audit()
    elif args.command == "repair-demo":
        cmd_repair_demo()
    elif args.command == "build-thesis":
        cmd_build_thesis()
    elif args.command == "dashboard":
        cmd_dashboard(port=args.port, no_browser=args.no_browser)
    elif args.command == "parse":
        if not args.html_or_file:
            print("[ERROR] provide an HTML string: python cli.py parse \"<p>Hello</p>\"")
            sys.exit(1)
        cmd_parse(args.html_or_file, output_format=args.format)
    elif args.command == "lint":
        if not args.html_or_file:
            print("[ERROR] provide an HTML file path: python cli.py lint index.html")
            sys.exit(1)
        cmd_lint(args.html_or_file, output_format=args.format)
    elif args.command == "orchestrate":
        cmd_orchestrate()
    elif args.command == "repl":
        cmd_repl()
    elif args.command == "all":
        cmd_all()


if __name__ == "__main__":
    main()
