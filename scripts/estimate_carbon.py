"""
scripts/estimate_carbon.py — Environmental Energy & Carbon Footprint Estimator.

This script quantifies the computational energy consumption (Joules / kWh) and
estimated carbon emissions (g CO2e) for parser execution, compliance testing,
and multi-agent reasoning cycles.

Key Features:
1. Calculates CPU energy footprint using TDP (Thermal Design Power) heuristics.
2. Evaluates environmental savings enabled by the SHA-256 on-disk ResponseCache.
3. Outputs structured data to data/carbon_footprint_report.json for Chapter 6 of the thesis.

Usage:
    python scripts/estimate_carbon.py
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Ensure project root is available in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.parser import parse

# Regional carbon intensity factors (kg CO2e per kWh)
CARBON_INTENSITY_FACTORS = {
    "EU_Average": 0.275,      # European Union average
    "UK_Grid": 0.207,         # United Kingdom grid average
    "US_Average": 0.385,      # United States average
    "Global_Average": 0.475   # Global average grid intensity
}

# Assumed hardware power draw (Watts)
CLIENT_CPU_TDP_WATTS = 45.0       # Average laptop / desktop CPU power during active parse
CLOUD_LLM_GPU_WATTS = 300.0       # Estimated server-side GPU wattage per inference call


def measure_parser_energy(iterations: int = 100) -> Dict[str, Any]:
    """
    Measures pure-Python parser execution energy across a batch of sample documents.
    """
    sample_html = "<html><body><header><h1>Energy Benchmark</h1></header><main><p>Content paragraph</p><div>Nested block</div></main></body></html>" * 10
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        parse(sample_html)
    elapsed_seconds = time.perf_counter() - start_time

    # Energy (Joules) = Power (Watts) * Time (Seconds)
    energy_joules = CLIENT_CPU_TDP_WATTS * elapsed_seconds
    energy_kwh = energy_joules / 3_600_000.0  # 1 kWh = 3.6e6 Joules

    # Carbon emissions (grams of CO2e)
    co2_grams_eu = energy_kwh * CARBON_INTENSITY_FACTORS["EU_Average"] * 1000.0
    co2_per_doc_mg = (co2_grams_eu / iterations) * 1000.0  # milligrams

    return {
        "iterations": iterations,
        "total_time_seconds": round(elapsed_seconds, 4),
        "avg_time_per_doc_ms": round((elapsed_seconds / iterations) * 1000.0, 3),
        "energy_joules": round(energy_joules, 4),
        "energy_kwh": round(energy_kwh, 8),
        "co2_grams_eu": round(co2_grams_eu, 6),
        "co2_per_doc_milligrams": round(co2_per_doc_mg, 4)
    }


def estimate_pipeline_energy() -> Dict[str, Any]:
    """
    Estimates energy and carbon impact of a full 7-agent LLM pipeline run,
    contrasting standard execution vs cache-accelerated execution.
    """
    # 7 Agents * ~2.5 seconds cloud LLM inference per agent = ~17.5s active GPU time
    active_llm_time_sec = 17.5
    uncached_energy_joules = CLOUD_LLM_GPU_WATTS * active_llm_time_sec
    uncached_energy_kwh = uncached_energy_joules / 3_600_000.0
    uncached_co2_grams = uncached_energy_kwh * CARBON_INTENSITY_FACTORS["EU_Average"] * 1000.0

    # With SHA-256 ResponseCache: disk lookup takes ~0.0005s on local CPU
    cached_energy_joules = CLIENT_CPU_TDP_WATTS * 0.0035
    cached_energy_kwh = cached_energy_joules / 3_600_000.0
    cached_co2_grams = cached_energy_kwh * CARBON_INTENSITY_FACTORS["EU_Average"] * 1000.0

    savings_percentage = ((uncached_energy_joules - cached_energy_joules) / uncached_energy_joules) * 100.0

    return {
        "uncached_run": {
            "energy_joules": round(uncached_energy_joules, 2),
            "energy_kwh": round(uncached_energy_kwh, 6),
            "co2_grams": round(uncached_co2_grams, 3)
        },
        "cached_run": {
            "energy_joules": round(cached_energy_joules, 4),
            "energy_kwh": round(cached_energy_kwh, 8),
            "co2_grams": round(cached_co2_grams, 6)
        },
        "energy_savings_percentage": round(savings_percentage, 2)
    }


def run_environmental_assessment():
    print("=" * 75)
    print("  GREEN AI & COMPUTATIONAL CARBON FOOTPRINT ASSESSMENT")
    print("=" * 75)

    parser_metrics = measure_parser_energy(iterations=100)
    pipeline_metrics = estimate_pipeline_energy()

    print("\n1. Pure-Python HTML5 Parser Execution Energy:")
    print(f"   - 100 Documents Elapsed Time:    {parser_metrics['total_time_seconds']} s")
    print(f"   - Energy per Document:           {parser_metrics['energy_joules'] / 100.0:.4f} Joules")
    print(f"   - Estimated Carbon per Document: {parser_metrics['co2_per_doc_milligrams']:.4f} mg CO2e (EU Grid)")

    print("\n2. Agentic Pipeline LLM Energy & ResponseCache Efficiency:")
    print(f"   - Uncached 7-Agent Run:          {pipeline_metrics['uncached_run']['energy_joules']} Joules ({pipeline_metrics['uncached_run']['co2_grams']} g CO2e)")
    print(f"   - Cached 7-Agent Run:            {pipeline_metrics['cached_run']['energy_joules']} Joules ({pipeline_metrics['cached_run']['co2_grams']} g CO2e)")
    print(f"   - Energy Reduction with Cache:   {pipeline_metrics['energy_savings_percentage']}% LESS ENERGY CONSUMED!")

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parser_metrics": parser_metrics,
        "pipeline_metrics": pipeline_metrics,
        "carbon_intensity_standards": CARBON_INTENSITY_FACTORS
    }

    # Save to data/carbon_footprint_report.json
    out_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "carbon_footprint_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 75)
    print(f"[OK] Saved carbon footprint report to: data/carbon_footprint_report.json")
    print("=" * 75 + "\n")

    return report


if __name__ == "__main__":
    run_environmental_assessment()
