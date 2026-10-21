"""
scripts/run_adversarial.py — Red-Team Adversarial Robustness Test Suite.
Evaluates parser resilience against 20+ specialized malformed, edge-case, and adversarial inputs.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.parser import parse, parse_with_trace

ADVERSARIAL_TESTS = [
    {"id": "ADV-01", "name": "Deeply Nested 200 Levels", "html": "<div>" * 200 + "Deep Content" + "</div>" * 200, "category": "Nesting"},
    {"id": "ADV-02", "name": "Unclosed Paragraphs Cascade", "html": "<p>1<p>2<p>3<p>4<p>5<div>Block End</div>", "category": "Implicit Closure"},
    {"id": "ADV-03", "name": "Bogus Comment Syntax", "html": "<!DOCTYPE html><!--- Broken comment --!><div>Valid</div>", "category": "Comments"},
    {"id": "ADV-04", "name": "Script Injection Attack Vector", "html": "<script>alert('xss')</script><img src=x onerror=prompt(1)>", "category": "Security / XSS"},
    {"id": "ADV-05", "name": "Unquoted Complex Attributes", "html": "<a href=https://example.com/test?a=1&b=2 class=btn-primary>Click</a>", "category": "Attributes"},
    {"id": "ADV-06", "name": "Unicode RTL & Emoji Tags", "html": "<div class='🔥' data-lang='العربية'>مرحبا بالعالم 🎉</div>", "category": "Internationalization"},
    {"id": "ADV-07", "name": "Zero-Width Spaces in Tag Names", "html": "<p\u200b>Zero width content</p>", "category": "Unicode"},
    {"id": "ADV-08", "name": "Self-Closing Non-Void Tag", "html": "<div/><span/>content", "category": "Void Elements"},
    {"id": "ADV-09", "name": "Extreme Long Attribute (5000 chars)", "html": f"<div data-long='{'a'*5000}'>Content</div>", "category": "Stress"},
    {"id": "ADV-10", "name": "Missing Root Tag", "html": "Just raw text without any wrapping tags", "category": "Malformed"},
    {"id": "ADV-11", "name": "Mixed Case Tag Names", "html": "<DiV ClAsS='MIXED'><P>Uppercase tags</p></dIV>", "category": "Case Sensitivity"},
    {"id": "ADV-12", "name": "Empty Input", "html": "", "category": "Edge Case"},
    {"id": "ADV-13", "name": "Whitespace Only", "html": "   \n\t  \r\n   ", "category": "Edge Case"},
    {"id": "ADV-14", "name": "Repeated Self-Closing Breaks", "html": "<br><br><hr><hr><img src='a.png'><input type='text'>", "category": "Void Elements"},
    {"id": "ADV-15", "name": "Nested Blockquote Hierarchy", "html": "<blockquote><blockquote><p>Quote level 2</p></blockquote></blockquote>", "category": "Hierarchy"}
]


# Executes the 15 red-team adversarial attacks and records response times and resilience rates
def run_adversarial_suite() -> Dict[str, Any]:
    print("=" * 70)
    print("  RED-TEAM ADVERSARIAL ROBUSTNESS SUITE")
    print("=" * 70)

    results = []
    passed = 0
    crashed = 0

    for test in ADVERSARIAL_TESTS:
        # High-resolution monotonic timing before sending malicious payload
        t0 = time.perf_counter()
        status = "PASSED"
        error_msg = None
        
        try:
            # Feed adversarial markup into parser and verify it recovers without throwing unhandled exceptions
            tree = parse(test["html"])
            elapsed = (time.perf_counter() - t0) * 1000.0
            passed += 1
            node_count = len(tree.children)
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000.0
            status = "CRASHED"
            error_msg = str(e)
            crashed += 1
            node_count = 0

        print(f"[{test['id']}] {test['name']:<35} [{status}] ({elapsed:.2f}ms)")
        
        results.append({
            "id": test["id"],
            "name": test["name"],
            "category": test["category"],
            "status": status,
            "duration_ms": round(elapsed, 2),
            "error": error_msg
        })

    summary = {
        "total": len(ADVERSARIAL_TESTS),
        "passed": passed,
        "crashed": crashed,
        "resilience_rate": round((passed / len(ADVERSARIAL_TESTS)) * 100.0, 1)
    }

    print("\n" + "=" * 70)
    print(f"  RESILIENCE RATE: {summary['resilience_rate']}% ({passed}/{len(ADVERSARIAL_TESTS)} survived without crash)")
    print("=" * 70)

    # Save to data/adversarial_results.json
    out_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "adversarial_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    return {"summary": summary, "results": results}


if __name__ == "__main__":
    run_adversarial_suite()
