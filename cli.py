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
    # Executes the compliance harness against bundled sample W3C test cases
    return run_command([sys.executable, "scripts/run_compliance.py", "--sample"], "W3C Compliance Test Runner")


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
        "dashboard", "parse", "lint", "all"
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
    elif args.command == "all":
        cmd_all()


if __name__ == "__main__":
    main()
