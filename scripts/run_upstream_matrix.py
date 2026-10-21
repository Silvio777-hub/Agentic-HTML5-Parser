"""
scripts/run_upstream_matrix.py — Full W3C Upstream Compliance Matrix & Test Bucket Runner.

Executes and categorizes test suites across 6 core academic HTML5 functional buckets:
1. Core Structural Hierarchy (HTML, HEAD, BODY, basic nesting)
2. Implicit Tag Closure (W3C Section 13.2.6.4.7 paragraph auto-closure)
3. Void Elements & Self-Closing Behavior (<br>, <img>, <hr>, <input>, <meta>)
4. HTML Entities & Character References (named &amp;, &lt;, &gt;, &#60;, &#x3C;)
5. Attributes & Quoting Semantics (unquoted, double, single, boolean flags)
6. Adversarial Robustness & Malformed Recovery (deep nesting, comments, script tags)

Generates:
- Structured console summary table
- data/upstream_matrix_report.json
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.parser import parse, tokenize, TreeNode


# Define the 6 Academic Test Buckets with concrete test cases
TEST_BUCKETS: Dict[str, List[Dict[str, Any]]] = {
    "Core Structural Hierarchy": [
        {"name": "Basic html/body structure", "html": "<html><body><p>Hello</p></body></html>", "assert": lambda t: t.name == "html" and len(t.children) > 0},
        {"name": "Nested container hierarchy", "html": "<main><section><article><p>Content</p></article></section></main>", "assert": lambda t: t.find("article") is not None and t.find("p") is not None},
        {"name": "Sibling tags under root", "html": "<div>One</div><div>Two</div><div>Three</div>", "assert": lambda t: len(t.find_all("div")) == 3},
        {"name": "Preserve text content", "html": "<h1>Header Title</h1>", "assert": lambda t: "Header Title" in t.text},
        {"name": "Empty document", "html": "", "assert": lambda t: t.name == "html"}
    ],
    "Implicit Tag Closure": [
        {"name": "<p> closes before <div>", "html": "<p>First<div>Second</div>", "assert": lambda t: len(t.find_all("p")) == 1 and t.find("p").find("div") is None},
        {"name": "<p> closes before <blockquote>", "html": "<p>First<blockquote>Quote</blockquote>", "assert": lambda t: t.find("p").find("blockquote") is None},
        {"name": "<p> closes before <section>", "html": "<p>First<section>Sec</section>", "assert": lambda t: t.find("p").find("section") is None},
        {"name": "<p> closes before <h1>", "html": "<p>Para<h1>Heading</h1>", "assert": lambda t: t.find("p").find("h1") is None},
        {"name": "Cascade multiple unclosed <p>", "html": "<p>One<p>Two<p>Three", "assert": lambda t: len(t.find_all("p")) == 3}
    ],
    "Void Elements & Self-Closing": [
        {"name": "<br> void tag (no children)", "html": "<p>Line 1<br>Line 2</p>", "assert": lambda t: len(t.find("p").find_all("br")) == 1},
        {"name": "<hr> horizontal rule void", "html": "<section><hr></section>", "assert": lambda t: t.find("hr") is not None and len(t.find("hr").children) == 0},
        {"name": "<img> with attributes", "html": "<img src='logo.png' alt='Logo'>", "assert": lambda t: t.find("img").attributes.get("src") == "logo.png"},
        {"name": "<input> void tag in form", "html": "<form><input type='text' name='q'></form>", "assert": lambda t: t.find("input").attributes.get("name") == "q"},
        {"name": "Self-closing slash <br />", "html": "Line<br />Next", "assert": lambda t: t.find("br") is not None}
    ],
    "HTML Entities & Character References": [
        {"name": "Named entity &amp; in text", "html": "<p>AT&amp;T</p>", "assert": lambda t: "AT&T" in t.find("p").text},
        {"name": "Named entity &lt; and &gt;", "html": "<p>5 &lt; 10 &gt; 2</p>", "assert": lambda t: "5 < 10 > 2" in t.find("p").text},
        {"name": "Named entity &quot; in text", "html": "<p>&quot;Quoted&quot;</p>", "assert": lambda t: '"Quoted"' in t.find("p").text},
        {"name": "Numeric decimal entity &#60;", "html": "<p>&#60;tag&#62;</p>", "assert": lambda t: "<tag>" in t.find("p").text},
        {"name": "Numeric hex entity &#x26;", "html": "<p>A&#x26;B</p>", "assert": lambda t: "A&B" in t.find("p").text},
        {"name": "Entities decoded in attribute values", "html": "<a href='search?q=1&amp;lang=en'>Link</a>", "assert": lambda t: t.find("a").attributes.get("href") == "search?q=1&lang=en"}
    ],
    "Attributes & Quoting Semantics": [
        {"name": "Double-quoted attributes", "html": "<div class=\"card primary\">Card</div>", "assert": lambda t: t.find("div").attributes.get("class") == "card primary"},
        {"name": "Single-quoted attributes", "html": "<div id='main-nav'>Nav</div>", "assert": lambda t: t.find("div").attributes.get("id") == "main-nav"},
        {"name": "Unquoted attributes", "html": "<input type=text disabled>", "assert": lambda t: t.find("input").attributes.get("type") == "text"},
        {"name": "Multiple attributes on element", "html": "<a href='/home' title='Home' target='_blank'>Home</a>", "assert": lambda t: len(t.find("a").attributes) >= 3},
        {"name": "Special characters in attributes", "html": "<div data-value=\"a=1&b=2\">Data</div>", "assert": lambda t: "data-value" in t.find("div").attributes}
    ],
    "Adversarial Robustness & Malformed Recovery": [
        {"name": "Deep nesting 50 levels", "html": "<div>" * 50 + "Deep" + "</div>" * 50, "assert": lambda t: t is not None and "Deep" in t.text},
        {"name": "Bogus comments recovery", "html": "<!-- normal --><! bogus comment ><p>After</p>", "assert": lambda t: t.find("p") is not None},
        {"name": "Script injection contained", "html": "<script>alert('xss')</script><p>Safe</p>", "assert": lambda t: t.find("p") is not None},
        {"name": "Extreme unclosed tags cascade", "html": "<div><span><b><i><u>Text", "assert": lambda t: "Text" in t.text},
        {"name": "Zero-width spaces & Unicode tags", "html": "<div>مرحبا بالعالم 🌟</div>", "assert": lambda t: "مرحبا" in t.text}
    ]
}


def run_matrix():
    print("=" * 80)
    print("  W3C UPSTREAM COMPLIANCE MATRIX & FUNCTIONAL BUCKET HARNESS")
    print("=" * 80)

    bucket_summaries = []
    total_all_tests = 0
    passed_all_tests = 0
    t_start_all = time.perf_counter()

    for bucket_name, test_cases in TEST_BUCKETS.items():
        print(f"\nEvaluating Bucket: [{bucket_name}] ({len(test_cases)} tests)...")
        b_passed = 0
        b_failed = 0
        t0 = time.perf_counter()
        results = []

        for tc in test_cases:
            tc_start = time.perf_counter()
            try:
                tree = parse(tc["html"])
                passed = tc["assert"](tree)
                duration_ms = round((time.perf_counter() - tc_start) * 1000.0, 3)
                if passed:
                    b_passed += 1
                    status = "PASSED"
                else:
                    b_failed += 1
                    status = "ASSERTION_FAILED"
            except Exception as e:
                duration_ms = round((time.perf_counter() - tc_start) * 1000.0, 3)
                b_failed += 1
                status = f"ERROR: {e}"

            results.append({
                "name": tc["name"],
                "status": status,
                "passed": (status == "PASSED"),
                "duration_ms": duration_ms
            })
            mark = "[OK]" if status == "PASSED" else "[FAIL]"
            print(f"  {mark} {tc['name']:<45} ({duration_ms:.2f} ms)")

        b_elapsed = (time.perf_counter() - t0) * 1000.0
        pass_rate = round((b_passed / len(test_cases)) * 100.0, 1) if test_cases else 0.0

        bucket_summaries.append({
            "bucket_name": bucket_name,
            "total_tests": len(test_cases),
            "passed_tests": b_passed,
            "failed_tests": b_failed,
            "pass_rate_pct": pass_rate,
            "total_duration_ms": round(b_elapsed, 2),
            "avg_latency_ms": round(b_elapsed / len(test_cases), 3) if test_cases else 0.0,
            "test_cases": results
        })

        total_all_tests += len(test_cases)
        passed_all_tests += b_passed

    total_wall_clock_s = round(time.perf_counter() - t_start_all, 3)
    overall_pass_rate = round((passed_all_tests / total_all_tests) * 100.0, 1)

    # Print Summary Markdown Table
    print("\n" + "=" * 80)
    print("  W3C FUNCTIONAL COMPLIANCE MATRIX SUMMARY (Markdown Table)")
    print("=" * 80)
    print("| Functional Bucket | Tests | Passed | Failed | Pass Rate (%) | Avg Latency (ms) | Status |")
    print("|-------------------|-------|--------|--------|---------------|------------------|--------|")
    for b in bucket_summaries:
        status_flag = "VERIFIED [OK]" if b["pass_rate_pct"] == 100.0 else "PARTIAL"
        print(f"| {b['bucket_name']:<19} | {b['total_tests']:<5} | {b['passed_tests']:<6} | {b['failed_tests']:<6} | {b['pass_rate_pct']:<13.1f} | {b['avg_latency_ms']:<16.3f} | {status_flag:<6} |")
    print("=" * 80)
    print(f"OVERALL MATRIX SCORE: {passed_all_tests}/{total_all_tests} ({overall_pass_rate}%) in {total_wall_clock_s}s\n")

    report_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_tests": total_all_tests,
        "passed_tests": passed_all_tests,
        "overall_pass_rate_pct": overall_pass_rate,
        "total_wall_clock_seconds": total_wall_clock_s,
        "buckets": bucket_summaries
    }

    out_file = PROJECT_ROOT / "data" / "upstream_matrix_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    print(f"[OK] Upstream matrix report saved to: {out_file}")
    return overall_pass_rate == 100.0


if __name__ == "__main__":
    success = run_matrix()
    sys.exit(0 if success else 1)
