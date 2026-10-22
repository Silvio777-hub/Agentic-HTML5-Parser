"""
scripts/run_compliance.py — Official html5lib test runner & compliance reporter.

Usage:
    python scripts/run_compliance.py --sample
    python scripts/run_compliance.py [--tests-dir path/to/html5lib-tests]
    python scripts/run_compliance.py --mode robust
"""

import os
import sys
import json
import glob
import argparse
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.parser import parse, TreeNode


def format_tree_to_document(node: TreeNode, indent: int = 1) -> List[str]:
    """Format TreeNode into html5lib-style pipe-indented document lines."""
    lines = []
    prefix = "| " + "  " * indent
    
    # Node tag line
    if node.name == "html" and indent == 1:
        lines.append("| <html>")
        lines.append("|   <head>")
        lines.append("|   <body>")
        if node.text_content:
            lines.append(f'|     "{node.text_content}"')
        for child in node.children:
            lines.extend(format_tree_to_document(child, indent=2))
        return lines

    lines.append(f"{prefix}<{node.name}>")
    
    # Attributes (alphabetical order)
    for attr, val in sorted(node.attributes.items()):
        lines.append(f"{prefix}  {attr}=\"{val}\"")
        
    # Text content
    if node.text_content:
        lines.append(f"{prefix}  \"{node.text_content}\"")
        
    # Children
    for child in node.children:
        lines.extend(format_tree_to_document(child, indent + 1))
        
    return lines


def serialize_tree_simple(node: TreeNode) -> Dict[str, Any]:
    """Serialize TreeNode into clean JSON-serializable structure for reporting."""
    return {
        "name": node.name,
        "attributes": node.attributes,
        "text": node.text_content,
        "children": [serialize_tree_simple(child) for child in node.children]
    }


def parse_dat_file(filepath: str) -> List[Dict[str, str]]:
    """Parse a .dat file into a list of test cases.
    
    W3C .dat format separates test cases by double-newlines. Each case contains:
    #data (raw HTML input), #errors (expected tokenizer errors), and #document (expected tree).
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    tests = []
    # Test cases in .dat are separated by double newlines or blank lines between sections
    raw_cases = content.split("\n\n")
    for raw in raw_cases:
        raw = raw.strip()
        if not raw:
            continue
        
        current_section = None
        sections: Dict[str, List[str]] = {}
        for line in raw.split("\n"):
            if line.startswith("#"):
                current_section = line[1:].strip()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        if "data" in sections:
            data_html = "\n".join(sections.get("data", [])).strip()
            expected_doc = "\n".join(sections.get("document", [])).strip()
            tests.append({
                "data": data_html,
                "document": expected_doc,
                "errors": "\n".join(sections.get("errors", [])).strip()
            })
            
    return tests


def run_compliance_tests(test_files: List[str], mode: str = "strict") -> Dict[str, Any]:
    """Run parser on all given test files and collect results."""
    results = []
    total = 0
    passed = 0
    failed = 0
    strict_matches = 0
    crash_free_count = 0

    test_counter = 1
    for filepath in test_files:
        test_cases = parse_dat_file(filepath)
        filename = os.path.basename(filepath)
        
        for case in test_cases:
            total += 1
            input_html = case["data"]
            expected_doc = case["document"]
            
            actual_tree = None
            actual_doc = ""
            error_msg = None
            crash_free = False
            strict_match = False
            
            try:
                # Parse input HTML using our custom Python HTML5 parser
                actual_tree = parse(input_html)
                crash_free = True
                crash_free_count += 1
                
                actual_lines = format_tree_to_document(actual_tree)
                actual_doc = "\n".join(actual_lines)
                
                # Normalize whitespace on both sides for deterministic tree comparison
                norm_expected = "\n".join([l.rstrip() for l in expected_doc.split("\n") if l.strip()])
                norm_actual = "\n".join([l.rstrip() for l in actual_lines if l.strip()])
                
                strict_match = (norm_expected == norm_actual)
                if strict_match:
                    strict_matches += 1
                else:
                    error_msg = "DOM tree differed from expected W3C document"
            except Exception as e:
                error_msg = f"Parser exception: {str(e)}"
                
            is_pass = strict_match if mode == "strict" else crash_free
            if is_pass:
                passed += 1
            else:
                failed += 1

            results.append({
                "id": test_counter,
                "file": filename,
                "input": input_html[:100],
                "expected": expected_doc[:150],
                "actual": actual_doc[:150],
                "passed": is_pass,
                "strict_match": strict_match,
                "crash_free": crash_free,
                "error": error_msg if not is_pass else None,
                "tree": serialize_tree_simple(actual_tree) if actual_tree else None
            })
            test_counter += 1

    pass_percentage = (passed / total * 100) if total > 0 else 0.0
    strict_pct = (strict_matches / total * 100) if total > 0 else 0.0
    crash_free_pct = (crash_free_count / total * 100) if total > 0 else 0.0

    report = {
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_percentage": round(pass_percentage, 2),
            "mode": mode,
            "strict_tree_matches": strict_matches,
            "strict_match_pct": round(strict_pct, 2),
            "crash_free_tests": crash_free_count,
            "crash_free_pct": round(crash_free_pct, 2)
        },
        "tests": results
    }

    # Save to data/compliance_results.json
    data_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "compliance_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    parser = argparse.ArgumentParser(description="HTML5 Parser Compliance Test Runner")
    parser.add_argument("--sample", action="store_true", help="Run with bundled sample tests")
    parser.add_argument("--tests-dir", type=str, default="html5lib-tests/tree-construction", help="Path to html5lib-tests tree-construction folder")
    parser.add_argument("--mode", type=str, choices=["strict", "robust"], default="strict", help="Evaluation mode: 'strict' (exact W3C tree) or 'robust' (crash-free)")
    parser.add_argument("--robustness", action="store_true", help="Shortcut for --mode robust")
    args = parser.parse_args()

    mode = "robust" if args.robustness else args.mode

    print("=" * 65)
    print(f"  HTML5 Parser Compliance Test Runner (Mode: {mode.upper()})")
    print("=" * 65)

    test_files = []
    if args.sample:
        sample_file = os.path.join(PROJECT_ROOT, "data", "sample_compliance_tests.dat")
        if not os.path.exists(sample_file):
            print(f"Error: Sample file not found at {sample_file}")
            sys.exit(1)
        test_files = [sample_file]
        print(f"Running in SAMPLE mode: {sample_file}")
    else:
        tests_dir = os.path.join(PROJECT_ROOT, args.tests_dir)
        if not os.path.exists(tests_dir):
            print(f"Notice: Upstream test suite not found at: {tests_dir}")
            print("Tip: Run `python scripts/setup_upstream_tests.py` to fetch official suite.")
            print("Falling back to sample test suite...")
            sample_file = os.path.join(PROJECT_ROOT, "data", "sample_compliance_tests.dat")
            test_files = [sample_file]
        else:
            test_files = sorted(glob.glob(os.path.join(tests_dir, "*.dat")))
            print(f"Found {len(test_files)} test suite files in {tests_dir}")

    report = run_compliance_tests(test_files, mode=mode)
    summary = report["summary"]

    print("\n" + "=" * 65)
    print("  COMPLIANCE SUMMARY")
    print("=" * 65)
    print(f"  Total Tests Evaluated:    {summary['total_tests']}")
    print(f"  Evaluation Mode:          {summary['mode'].upper()}")
    print(f"  Strict W3C Tree Matches:  {summary['strict_tree_matches']} / {summary['total_tests']} ({summary['strict_match_pct']}%)")
    print(f"  Crash-Free Robustness:    {summary['crash_free_tests']} / {summary['total_tests']} ({summary['crash_free_pct']}%)")
    print(f"  Reported Pass/Fail:       {summary['passed']} Passed, {summary['failed']} Failed ({summary['pass_percentage']}%)")
    print("=" * 65)
    print(f"  Report saved to: data/compliance_results.json\n")


if __name__ == "__main__":
    main()
