"""
Interactive Step-by-Step Pipeline Runner
Runs Agentic AI HTML5 Parser agents one by one with user confirmation.
"""

import sys
from orchestrator import PipelineOrchestrator
from config import Config

def prompt_user(message):
    print(f"\n[PROMPT] {message}")
    input("Press Enter to continue or Ctrl+C to abort...")

def main():
    Config.ensure_directories_exist()
    
    # Initialize Orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Inputs
    html_subset = """
    Implement a parser for: <html>, <body>, <p>, <div>.
    Include implicit closure of <p> before <div>.
    """
    parser_interface = """
    Required functions: tokenize(html), parse(html), parse_with_trace(html).
    """

    report = {
        "run_id": orchestrator.run_id,
        "stages": {}
    }

    print("\nStarting Interactive Agent Pipeline...")

    # Stage 1: Spec Agent
    prompt_user("Run STAGE 1: Spec Agent (Generate specification)")
    orchestrator._run_spec_agent(html_subset, parser_interface, report)

    # Stage 2: Codegen Agent
    prompt_user("Run STAGE 2: Codegen Agent (Generate code patches)")
    orchestrator._run_codegen_agent(report)

    # Stage 3: Test Agent
    prompt_user("Run STAGE 3: Test Agent (Generate test suite)")
    orchestrator._run_test_agent(report)

    # Stage 4: execution
    prompt_user("Run STAGE 4: Test Execution")
    test_report = orchestrator._run_tests_only(report)

    # Stage 5: Repair
    if test_report.get("summary", {}).get("failed", 0) > 0:
        prompt_user("Run STAGE 5: Repair Agent (Fix failures)")
        orchestrator._run_repair_agent(report, test_report)
    else:
        print("\n[+] All tests passed! No repair needed.")

    print("\n" + "="*40)
    print(f"Sequential Run Complete!")
    print(f"Artifacts saved in: {orchestrator.run_dir}")
    print("="*40)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Execution aborted by user.")
        sys.exit(0)
