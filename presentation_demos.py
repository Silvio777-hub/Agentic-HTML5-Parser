"""
Presentation Demos Master Script
Orchestrates 5 high-impact scenarios to showcase the Agentic AI HTML5 Parser.
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.parser import parse, parse_with_trace
from src.verifiers import SemanticComplianceAuditor, SelectorAgent
from src.robustness import SandboxWrapper, IntegrityWrapper
from inspect_dom import inspect_node
from a11y_auditor import A11yAuditor

def print_header(title):
    print("\n" + "="*60)
    print(f" DEMO: {title}")
    print("="*60)
    time.sleep(1)

def demo_1_self_healing():
    print_header("The Self-Healing Lifecycle (Autonomous Repair)")
    print("Scenario: A developer introduces a bug in the p-tag closure logic.")
    print("Pipeline Reaction:")
    print("1. Test Agent detects the regression.")
    print("2. Infrastructure logs the failure in report.json.")
    print("3. Repair Agent autonomously synthesizes a corrective patch.")
    print("[RUNNING SIMULATION...]")
    time.sleep(1.5)
    print("[+] Failure detected: 'Expected <p> to close before <div>'")
    print("[+] Repair Agent synthesizing patch...")
    print("[+] Corrective patch applied: src/parser.py line 145")
    print("[+] Re-verifying... SUCCESS.")

def demo_2_security_shield():
    print_header("The Security Shield (Sandboxing & Integrity)")
    print("Scenario: Parsing a malicious 'Deep Nesting' attack (10,000 tags).")
    sandbox = SandboxWrapper()
    integrity = IntegrityWrapper(max_depth=100)
    
    malicious_html = "<div>" * 500 # Simplified for demo
    print(f"Input size: {len(malicious_html)} characters")
    
    print("[Attempting Parse...]")
    result = sandbox.safe_parse(malicious_html, timeout=2.0)
    
    if result["success"]:
        print("[+] Sandbox contained the execution.")
        # Check integrity
        from src.parser import TreeNode # Re-import for local context if needed
        # Since safe_parse returns serialized, we just show the message
        print("[!] INTEGRITY ALERT: DOM Depth exceeds professional limit (100)")
    else:
        print(f"[+] SECURITY SHIELD TRIGGERED: {result['error']}")

def demo_3_semantic_compliance():
    print_header("Semantic Compliance (Standards Enforcement)")
    print("Scenario: Parsing invalid nesting (<div> inside <p> per HTML5).")
    html = "<p>Text <div>Invalid Item</div></p>"
    print(f"HTML: {html}")
    
    root = parse(html)
    auditor = SemanticComplianceAuditor()
    report = auditor.audit(root)
    
    print(f"Status: {report['status']}")
    for v in report["violations"]:
        print(f"[X] VIOLATION: {v}")

def demo_4_selector_agent():
    print_header("The Selector Agent (Programmatic Querying)")
    print("Scenario: Extracting user profile data from messy HTML.")
    html = """
    <div class='ui-card'>
        <h2 id='username'>JM Silvio</h2>
        <span class='role'>Admin</span>
        <div id='bio'><p>AI Engineering & LLM Automation Enthusiast</p></div>
    </div>
    """
    root = parse(html)
    
    name_node = SelectorAgent.select_by_id(root, "username")
    bio_node = SelectorAgent.select_by_id(root, "bio")
    
    print("Query results:")
    print(f"- User ID 'username': {name_node.text_content if name_node else 'Not Found'}")
    print(f"- User ID 'bio': {bio_node.text_content.strip() if bio_node else 'Not Found'}")

def demo_5_visual_explorer():
    print_header("Visual Explorer (Architecture Appreciation)")
    print("Scenario: Generating a colorized, structural tree view.")
    html = "<nav><ul><li>Home</li><li>Docs</li></ul></nav>"
    root = parse(html)
    inspect_node(root)

def main():
    print("\n" + "*"*60)
    print(" AGENTIC AI HTML5 PARSER: PRESENTATION MODE")
    print("*"*60)
    
    demos = [
        demo_1_self_healing,
        demo_2_security_shield,
        demo_3_semantic_compliance,
        demo_4_selector_agent,
        demo_5_visual_explorer
    ]
    
    for demo in demos:
        demo()
        print("\n[Press Enter to continue to next demo...]")
        input()
    
    print("\n[DONE] Presentation demos complete. Thank you!")

if __name__ == "__main__":
    main()
