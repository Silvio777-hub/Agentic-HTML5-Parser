"""
cli.py — Master Unified Command-Line Interface.

Single control center for the Agentic AI HTML5 Parser thesis project:
Provides easy 1-command access to all verification, benchmarking,
repair demos, chart generation, and dashboard servers.

Usage Examples:
    python cli.py dashboard       # Launches live dashboard & playground at http://localhost:8080/dashboard/
    python cli.py test            # Runs all 34 automated unit & streaming tests
    python cli.py compliance      # Runs W3C html5lib compliance test harness
    python cli.py benchmark       # Runs comparative performance benchmarks vs BeautifulSoup & lxml
    python cli.py adversarial     # Runs Red-Team hacker stress tests
    python cli.py ablation        # Runs empirical ablation study experiments
    python cli.py charts          # Generates all 300-DPI thesis figures
    python cli.py carbon          # Runs Green AI carbon footprint assessment
    python cli.py audit           # Runs AST security analysis & STRIDE audit
    python cli.py repair-demo     # Runs the live self-repair showcase demonstration
    python cli.py build-thesis    # Verifies all 7 thesis chapters in thesis/
    python cli.py all             # Executes the entire pipeline and builds all assets
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
    result = subprocess.run(cmd_list, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print(f"[FAIL] [CLI] Command failed with returncode {result.returncode}")
        return False
    return True


def cmd_test():
    """Runs all 34 automated unit, integration, and streaming tests."""
    return run_command([sys.executable, "-m", "pytest", "tests/", "-v"], "Automated Test Suite (pytest)")


def cmd_compliance():
    """Runs W3C html5lib compliance test harness."""
    return run_command([sys.executable, "scripts/run_compliance.py", "--sample"], "W3C Compliance Test Runner")


def cmd_benchmark():
    """Runs comparative benchmarks against BeautifulSoup4 and lxml."""
    return run_command([sys.executable, "scripts/compare_benchmarks.py"], "Comparative Benchmark Suite")


def cmd_adversarial():
    """Runs Red-Team adversarial security tests."""
    return run_command([sys.executable, "scripts/run_adversarial.py"], "Red-Team Adversarial Robustness Suite")


def cmd_ablation():
    """Runs empirical multi-agent ablation study."""
    return run_command([sys.executable, "scripts/run_ablation_study.py"], "Empirical Ablation Study Runner")


def cmd_charts():
    """Generates all 300-DPI publication figures."""
    return run_command([sys.executable, "scripts/generate_thesis_charts.py"], "300-DPI Publication Figure Generator")


def cmd_carbon():
    """Runs computational carbon footprint & energy assessment."""
    return run_command([sys.executable, "scripts/estimate_carbon.py"], "Green AI Carbon Footprint Estimator")


def cmd_audit():
    """Runs AST static security analysis and STRIDE threat modeling."""
    return run_command([sys.executable, "scripts/run_security_audit.py"], "Static Security & STRIDE Auditor")


def cmd_repair_demo():
    """Runs the live self-repair showcase demo."""
    return run_command([sys.executable, "scripts/demo_self_repair.py"], "Autonomous Self-Repair Showcase Demo")


def cmd_build_thesis():
    """Verifies that all 7 thesis chapters exist in thesis/."""
    thesis_dir = Path("thesis")
    chapters = list(thesis_dir.glob("0*.md"))
    if len(chapters) == 7:
        print(f"  Thesis chapters verified: {len(chapters)} chapters present in thesis/")
        return True
    print(f"  Thesis directory missing chapters in {thesis_dir}")
    return False


def cmd_dashboard(port=8080, no_browser=False):
    """Starts the local web server and live playground API."""
    cmd = [sys.executable, "scripts/serve_dashboard.py", "--port", str(port)]
    if no_browser:
        cmd.append("--no-browser")
    return run_command(cmd, "Live Quality Dashboard & API Server")


def cmd_all():
    """Runs the entire verification, benchmarking, and asset generation pipeline."""
    print("=" * 75)
    print("  EXECUTING COMPLETE MASTER AGENTIC AI HTML5 PARSER PIPELINE")
    print("=" * 75)
    
    steps = [
        ("Testing", cmd_test),
        ("Compliance", cmd_compliance),
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
            print(f"\n❌ Pipeline failed during step: {name}")
            return False

    print("\n" + "=" * 75)
    print("  🎉 COMPLETE PIPELINE EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")
    print("  👉 Live Dashboard: python cli.py dashboard")
    print("  👉 Thesis Chapters: thesis/ (All 7 chapters present)")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Master Unified CLI for Agentic AI HTML5 Parser Thesis Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  test          Run all 34 automated unit & streaming tests
  compliance    Run W3C compliance test harness
  benchmark     Run performance benchmarks vs BeautifulSoup & lxml
  adversarial   Run Red-Team hacker stress tests
  ablation      Run empirical ablation study experiments
  charts        Generate all 300-DPI publication figures
  carbon        Run computational carbon footprint assessment
  audit         Run AST security analysis & STRIDE audit
  repair-demo   Run the live self-repair showcase demonstration
  build-thesis  Verify all 7 thesis chapters in thesis/
  dashboard     Launch live dashboard & playground server
  all           Run complete pipeline end-to-end
        """
    )
    parser.add_argument("command", choices=[
        "test", "compliance", "benchmark", "adversarial", "ablation",
        "charts", "carbon", "audit", "repair-demo", "build-thesis", "dashboard", "all"
    ], help="Command to execute")
    parser.add_argument("--port", type=int, default=8080, help="Port for dashboard server (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser on dashboard launch")

    args = parser.parse_args()

    if args.command == "test":
        cmd_test()
    elif args.command == "compliance":
        cmd_compliance()
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
    elif args.command == "all":
        cmd_all()


if __name__ == "__main__":
    main()
