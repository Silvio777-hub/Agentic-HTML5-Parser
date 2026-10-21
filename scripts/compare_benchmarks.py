"""
scripts/compare_benchmarks.py — Comparative Benchmark Suite.
Compares the Agentic AI HTML5 Parser against standard industry parsers:
- html5lib (Python reference parser)
- BeautifulSoup4 (Standard industry scraping parser)
- lxml (Fast C-backed parser)

Outputs results in Markdown table format and JSON for inclusion in Chapter 5 of the thesis.
"""

import os
import sys
import time
import json
import tracemalloc
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.parser import parse as ai_parse

# Test corpus for benchmarking
SAMPLE_DOCUMENTS = [
    ("Small Fragment (100B)", "<html><body><p class='intro'>Hello <b>World</b></p></body></html>"),
    ("Nested Structure (1KB)", "<html><body>" + "<div><section><article><p>Nested item</p></article></section></div>" * 10 + "</body></html>"),
    ("Table & Attributes (5KB)", "<html><body><table border='1'>" + "".join([f"<tr><td>Row {i}</td><td>Value {i*2}</td></tr>" for i in range(100)]) + "</table></body></html>"),
    ("Complex Mixed DOM (20KB)", "<html><head><title>Benchmark</title></head><body>" + "".join([f"<div id='sec-{i}' class='card'><h3>Title {i}</h3><p>Content with <a href='#'>links</a> and <span>spans</span></p></div>" for i in range(150)]) + "</body></html>")
]


# Benchmark execution harness: profiles latency (avg/p95) and heap memory across iterations
def benchmark_parser(parser_name: str, parse_fn, iterations: int = 20) -> Dict[str, Any]:
    latencies = []
    
    # Warmup phase: execute one pass over corpus to ensure module bytecode is compiled in memory
    for _, doc in SAMPLE_DOCUMENTS:
        try:
            parse_fn(doc)
        except Exception:
            pass

    # Enable Python memory tracing to record peak heap allocation during benchmark
    tracemalloc.start()
    start_wall = time.perf_counter()
    
    for _ in range(iterations):
        for _, doc in SAMPLE_DOCUMENTS:
            t0 = time.perf_counter()
            try:
                parse_fn(doc)
            except Exception:
                pass
            latencies.append((time.perf_counter() - t0) * 1000.0)  # ms

    total_time = time.perf_counter() - start_wall
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    total_docs_parsed = iterations * len(SAMPLE_DOCUMENTS)
    avg_latency = sum(latencies) / len(latencies)
    sorted_latencies = sorted(latencies)
    p95_latency = sorted_latencies[int(0.95 * len(sorted_latencies))]

    return {
        "parser": parser_name,
        "total_docs": total_docs_parsed,
        "avg_latency_ms": round(avg_latency, 3),
        "p95_latency_ms": round(p95_latency, 3),
        "min_latency_ms": round(min(latencies), 3),
        "max_latency_ms": round(max(latencies), 3),
        "throughput_docs_per_sec": round(total_docs_parsed / total_time, 1),
        "peak_memory_kb": round(peak_mem / 1024.0, 2)
    }


def run_comparative_benchmark() -> List[Dict[str, Any]]:
    parsers_to_test = [
        ("Agentic AI HTML5 Parser", ai_parse)
    ]

    # Try importing BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        parsers_to_test.append(("BeautifulSoup4 (html.parser)", lambda h: BeautifulSoup(h, "html.parser")))
    except ImportError:
        print("[Notice] beautifulsoup4 not installed, skipping.")

    # Try importing html5lib
    try:
        import html5lib
        parsers_to_test.append(("html5lib (Reference)", lambda h: html5lib.parse(h)))
    except ImportError:
        print("[Notice] html5lib not installed, skipping.")

    # Try importing lxml
    try:
        import lxml.html
        parsers_to_test.append(("lxml.html (C-Parser)", lambda h: lxml.html.fromstring(h)))
    except ImportError:
        print("[Notice] lxml not installed, skipping.")

    print("\n" + "=" * 75)
    print("  RUNNING COMPARATIVE BENCHMARK SUITE")
    print("=" * 75)

    results = []
    for name, fn in parsers_to_test:
        print(f"Benchmarking: {name} ...", end="", flush=True)
        res = benchmark_parser(name, fn)
        results.append(res)
        print(f" Done ({res['avg_latency_ms']} ms/doc, {res['throughput_docs_per_sec']} docs/sec)")

    # Save to data/benchmark_results.json
    out_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Print Markdown Table for Thesis Chapter 5
    print("\n" + "=" * 75)
    print("  THESIS CHAPTER 5 COMPARATIVE BENCHMARK TABLE (Markdown)")
    print("=" * 75)
    print("| Parser Implementation | Avg Latency (ms) | P95 Latency (ms) | Throughput (docs/s) | Peak Memory (KB) |")
    print("|-----------------------|------------------|------------------|---------------------|------------------|")
    for r in results:
        print(f"| {r['parser']:<21} | {r['avg_latency_ms']:<16} | {r['p95_latency_ms']:<16} | {r['throughput_docs_per_sec']:<19} | {r['peak_memory_kb']:<16} |")
    print("=" * 75)
    print(f"[OK] Saved full results to: data/benchmark_results.json\n")

    return results


if __name__ == "__main__":
    run_comparative_benchmark()
