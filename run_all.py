"""
Master script to execute the full multi-agent pipeline simulation.
Runs parsing, verification, auditing, and fuzzer.
"""

from src.parser import parse_with_trace
from src.verifiers import SemanticComplianceAuditor, DifferentialOracle, SecurityFuzzer
from src.robustness import SandboxWrapper, IntegrityWrapper
import json
import os

def run_simulation(html: str, label: str):
    print(f"\n>>> Running Simulation: {label}")
    
    # 1. Parsing with Trace
    print("[1] Parsing and Tracing...")
    result = parse_with_trace(html)
    
    # 2. Semantic Audit
    print("[2] Semantic Compliance Audit...")
    auditor = SemanticComplianceAuditor()
    from src.parser import parse # for local use
    tree = parse(html)
    audit_results = auditor.audit(tree)
    print(f"    Status: {audit_results['status']} (Score: {audit_results['score']})")
    
    # 3. Differential Oracle
    print("[3] Differential Oracle Comparison...")
    oracle = DifferentialOracle()
    diff_results = oracle.compare(html, tree)
    print(f"    Match: {diff_results['matches']}")
    
    # 4. Integrity Check
    print("[4] Integrity Verification...")
    integrity = IntegrityWrapper()
    integrity_results = integrity.verify(tree)
    print(f"    Valid: {integrity_results['valid']}")
    
    # Save Artifacts
    run_dir = f"runs/simulation_{label.lower().replace(' ', '_')}"
    os.makedirs(run_dir, exist_ok=True)
    
    with open(f"{run_dir}/report.json", "w") as f:
        json.dump({
            "label": label,
            "audit": audit_results,
            "differential": diff_results,
            "integrity": integrity_results,
            "trace_events": len(result["trace"]["events"])
        }, f, indent=2)
    
    print(f"[+] Artifacts saved to {run_dir}/")

def main():
    demos = [
        ("<div><p>Simple Test</p></div>", "Simple Tag Nesting"),
        ("<p><div>Invalid Nesting</div></p>", "Semantic Violation"),
        ('<div id="main" class="container" data-test="true"><p>Test</p></div>', "Attributes and IDs"),
        ('<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>', "Table Structure"),
        ('<form><label>User:</label><input type="text"><button>Submit</button></form>', "Login Form")
    ]
    
    for html, label in demos:
        run_simulation(html, label)
        
    # Run Fuzzer
    print("\n>>> Running Security Fuzzer...")
    wild_html = SecurityFuzzer.generate_wild_html(complexity=10)
    run_simulation(wild_html, "Fuzzer Test Case")

if __name__ == "__main__":
    main()
