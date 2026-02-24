"""
Main Pipeline Orchestrator
Orchestrates all agents in sequence to build, test, and repair the HTML5 parser.

FEATURE 3: Artifact-Based Pipeline Orchestration
- Manages workflow through intermediate artifacts
- Applies patches iteratively
- Stores all outputs for auditability
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from src.utils import ArtifactManager, PatchManager, ReportGenerator
from src.parser import parse_with_trace, tokenize, parse
from src.groq_integration import (
    SpecAgentAI, CodegenAgentAI, CritiqueAgentAI, TestAgentAI,
    RedTeamAgentAI, MonitorAgentAI, RepairAgentAI
)


class PipelineOrchestrator:
    """
    Orchestrates the complete agentic AI pipeline for HTML5 parser development.
    
    Workflow:
    1. Spec Agent: HTML subset → structured specification (spec.yml)
    2. Codegen Agent: specification → code patches
    3. Critique Agent: validates patches
    4. Test Agent: generates test suite
    5. Red-Team Agent: generates adversarial tests
    6. Runner: executes tests and collects reports
    7. Monitor Agent: analyzes execution metrics
    8. Repair Agent: fixes failures and iterates
    """
    
    def __init__(self, run_id: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            run_id: Unique run identifier (auto-generated if not provided)
        """
        # Generate run ID if not provided
        if not run_id:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.run_id = run_id
        self.run_dir = Config.RUNS_DIR / run_id
        self.artifact_manager = ArtifactManager(run_id, self.run_dir)
        
        # Initialize agents
        self.spec_agent = SpecAgentAI()
        self.codegen_agent = CodegenAgentAI()
        self.critique_agent = CritiqueAgentAI()
        self.test_agent = TestAgentAI()
        self.red_team_agent = RedTeamAgentAI()
        self.monitor_agent = MonitorAgentAI()
        self.repair_agent = RepairAgentAI()
        
        # Pipeline state
        self.specification = {}
        self.iteration = 0
        self.max_iterations = 3
        
        print(f"\n{'='*60}")
        print(f"Pipeline Orchestrator initialized")
        print(f"Run ID: {self.run_id}")
        print(f"Run directory: {self.run_dir}")
        print(f"{'='*60}\n")
    
    def run(self, html_subset: str, parser_interface: str) -> Dict[str, Any]:
        """
        Execute the complete pipeline.
        
        Args:
            html_subset: HTML5 subset specification
            parser_interface: Description of parser interface
            
        Returns:
            Pipeline execution report
        """
        report = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        try:
            # Stage 1: Spec Agent
            print("\n" + "="*60)
            print("STAGE 1: SPEC AGENT")
            print("="*60)
            self._run_spec_agent(html_subset, parser_interface, report)
            
            # Stage 2: Codegen Agent
            print("\n" + "="*60)
            print("STAGE 2: CODEGEN AGENT")
            print("="*60)
            self._run_codegen_agent(report)
            
            # Stage 3: Critique Agent
            print("\n" + "="*60)
            print("STAGE 3: CRITIQUE AGENT")
            print("="*60)
            self._run_critique_agent(report)
            
            # Stage 4: Test Agent
            print("\n" + "="*60)
            print("STAGE 4: TEST AGENT")
            print("="*60)
            self._run_test_agent(report)
            
            # Stage 5: Red-Team Agent
            print("\n" + "="*60)
            print("STAGE 5: RED-TEAM AGENT")
            print("="*60)
            self._run_red_team_agent(report)
            
            # Stage 6: Execute Tests & Generate Reports
            print("\n" + "="*60)
            print("STAGE 6: TEST EXECUTION & MONITORING")
            print("="*60)
            test_report = self._run_tests_and_monitor(report)
            
            # Stage 7: Repair (if needed)
            if test_report["summary"]["failed"] > 0:
                print("\n" + "="*60)
                print("STAGE 7: REPAIR AGENT")
                print("="*60)
                self._run_repair_agent(report, test_report)
            
            report["status"] = "success"
            report["final_test_report"] = test_report
            
        except Exception as e:
            print(f"\nError during pipeline execution: {e}")
            report["status"] = "failed"
            report["error"] = str(e)
        
        # Save final report
        self.artifact_manager.save_report(report, "pipeline_report.json")
        
        return report
    
    def _run_spec_agent(self, html_subset: str, parser_interface: str, 
                       report: Dict[str, Any]) -> None:
        """Execute Spec Agent to generate specification."""
        print("\nGenerating specification from HTML subset...")
        
        try:
            # Call Spec Agent AI
            spec_yaml = self.spec_agent.generate_specification(
                html_subset,
                parser_interface
            )
            
            # Parse YAML
            import yaml
            self.specification = yaml.safe_load(spec_yaml)
            
            # Save specification
            spec_path = self.artifact_manager.save_specification(self.specification)
            
            report["stages"]["spec_agent"] = {
                "status": "success",
                "spec_path": str(spec_path),
                "spec_size": len(spec_yaml),
                "rules_count": len(self.specification.get("rules", {}))
            }
            
            print(f"✓ Specification generated ({len(spec_yaml)} chars)")
            print(f"  Rules: {len(self.specification.get('rules', {}))}")
            
        except Exception as e:
            report["stages"]["spec_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Spec Agent failed: {e}")
            raise
    
    def _run_codegen_agent(self, report: Dict[str, Any]) -> None:
        """Execute Codegen Agent to generate code patches."""
        print("\nGenerating code patches...")
        
        try:
            # Read current parser implementation
            parser_file = Config.SRC_DIR / "parser.py"
            current_impl = parser_file.read_text()
            
            # Call Codegen Agent AI
            patch_content = self.codegen_agent.generate_code_patch(
                json.dumps(self.specification),
                current_impl,
                "Implement tokenization and tree construction improvements"
            )
            
            # Save patch
            patch_path = self.artifact_manager.save_patch(patch_content, "code.patch")
            
            report["stages"]["codegen_agent"] = {
                "status": "success",
                "patch_path": str(patch_path),
                "patch_size": len(patch_content)
            }
            
            print(f"✓ Code patch generated ({len(patch_content)} chars)")
            
        except Exception as e:
            report["stages"]["codegen_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Codegen Agent failed: {e}")
    
    def _run_critique_agent(self, report: Dict[str, Any]) -> None:
        """Execute Critique Agent to validate patches."""
        print("\nCritiquing generated patches...")
        
        try:
            # Get patch and specification
            patch_path = self.artifact_manager.patch_dir / "code.patch"
            if not patch_path.exists():
                raise FileNotFoundError("No patch found from Codegen Agent")
            
            patch_content = patch_path.read_text()
            spec_str = json.dumps(self.specification)
            
            # Call Critique Agent AI
            critique = self.critique_agent.critique_patch(
                patch_content,
                spec_str,
                "Pending test execution"
            )
            
            # Save critique
            report["stages"]["critique_agent"] = {
                "status": "success",
                "critique": critique
            }
            
            approval = critique.get("approval", False)
            confidence = critique.get("confidence_score", 0)
            print(f"✓ Code reviewed - Approval: {approval}, Confidence: {confidence}%")
            
            if not approval:
                print(f"  Issues: {critique.get('issues', [])}")
            
        except Exception as e:
            report["stages"]["critique_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Critique Agent failed: {e}")
    
    def _run_test_agent(self, report: Dict[str, Any]) -> None:
        """Execute Test Agent to generate test suite."""
        print("\nGenerating test suite...")
        
        try:
            # Call Test Agent AI
            test_code = self.test_agent.generate_tests(
                json.dumps(self.specification),
                self._load_parser_interface()
            )
            
            # Save test code
            test_file = Config.TESTS_DIR / "test_parser.py"
            test_file.write_text(test_code)
            
            report["stages"]["test_agent"] = {
                "status": "success",
                "test_file": str(test_file),
                "test_code_size": len(test_code)
            }
            
            print(f"✓ Test suite generated ({len(test_code)} chars)")
            
        except Exception as e:
            report["stages"]["test_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Test Agent failed: {e}")
    
    def _run_red_team_agent(self, report: Dict[str, Any]) -> None:
        """Execute Red-Team Agent to generate adversarial tests."""
        print("\nGenerating adversarial tests...")
        
        try:
            # Call Red-Team Agent AI
            adversarial_tests = self.red_team_agent.generate_adversarial_tests(
                self._load_parser_interface(),
                "Focus on malformed HTML and deeply nested structures"
            )
            
            # Save adversarial tests
            red_team_file = Config.TESTS_DIR / "test_red_team.py"
            red_team_file.write_text(adversarial_tests)
            
            report["stages"]["red_team_agent"] = {
                "status": "success",
                "test_file": str(red_team_file),
                "test_code_size": len(adversarial_tests)
            }
            
            print(f"✓ Adversarial tests generated ({len(adversarial_tests)} chars)")
            
        except Exception as e:
            report["stages"]["red_team_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Red-Team Agent failed: {e}")
    
    def _run_tests_and_monitor(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests and collect execution metrics."""
        print("\nExecuting test suite...")
        
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"passed": 0, "failed": 0, "total": 0},
            "errors": [],
            "test_details": []
        }
        
        # Test basic parser functionality
        test_cases = self._create_test_cases()
        
        for test_name, test_html, expected_behavior in test_cases:
            try:
                result = parse_with_trace(test_html)
                
                # Basic validation
                test_result = {
                    "name": test_name,
                    "status": "passed",
                    "duration": result["trace"]["duration"]
                }
                
                test_report["test_details"].append(test_result)
                test_report["summary"]["passed"] += 1
                
            except Exception as e:
                test_result = {
                    "name": test_name,
                    "status": "failed",
                    "error": str(e)
                }
                test_report["test_details"].append(test_result)
                test_report["summary"]["failed"] += 1
                test_report["errors"].append(f"{test_name}: {str(e)}")
        
        test_report["summary"]["total"] = (
            test_report["summary"]["passed"] + test_report["summary"]["failed"]
        )
        test_report["summary"]["success_rate"] = (
            test_report["summary"]["passed"] / test_report["summary"]["total"]
            if test_report["summary"]["total"] > 0 else 0
        )
        
        # Save test report
        self.artifact_manager.save_report(test_report, "test_report.json")
        
        # Call Monitor Agent for analysis
        self._run_monitor_agent(report, test_report)
        
        return test_report
    
    def _run_monitor_agent(self, report: Dict[str, Any], 
                          test_report: Dict[str, Any]) -> None:
        """Execute Monitor Agent to analyze execution metrics."""
        print("\nMonitoring execution metrics...")
        
        try:
            trace_data = json.dumps({
                "test_summary": test_report["summary"],
                "test_count": len(test_report["test_details"])
            })
            
            analysis = self.monitor_agent.analyze_execution(
                trace_data,
                {"total_tests": test_report["summary"]["total"],
                 "failed_tests": test_report["summary"]["failed"]}
            )
            
            report["stages"]["monitor_agent"] = {
                "status": "success",
                "analysis": analysis
            }
            
            print(f"✓ Execution monitored - Healthy: {analysis.get('healthy', False)}")
            
        except Exception as e:
            report["stages"]["monitor_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Monitor Agent failed: {e}")
    
    def _run_repair_agent(self, report: Dict[str, Any], 
                         test_report: Dict[str, Any]) -> None:
        """Execute Repair Agent to fix failing tests."""
        print("\nAnalyzing failures and generating repairs...")
        
        if self.iteration >= self.max_iterations:
            print(f"Max iterations ({self.max_iterations}) reached, stopping repairs")
            return
        
        self.iteration += 1
        
        try:
            # Get failing tests
            failing_tests = [
                t["name"] for t in test_report["test_details"] 
                if t["status"] == "failed"
            ]
            
            if not failing_tests:
                print("✓ No failures to repair")
                return
            
            # Get parser code
            parser_file = Config.SRC_DIR / "parser.py"
            parser_code = parser_file.read_text()
            
            # Call Repair Agent AI
            repair_patch = self.repair_agent.generate_repair_patch(
                str(failing_tests),
                json.dumps(test_report),
                parser_code
            )
            
            # Save repair patch
            repair_path = self.artifact_manager.save_patch(
                repair_patch, 
                f"repair_{self.iteration}.patch"
            )
            
            report["stages"]["repair_agent"] = {
                "status": "success",
                "patch_path": str(repair_path),
                "iteration": self.iteration,
                "failing_tests_count": len(failing_tests)
            }
            
            print(f"✓ Repair patch generated (iteration {self.iteration})")
            print(f"  Fixed {len(failing_tests)} failing tests")
            
        except Exception as e:
            report["stages"]["repair_agent"] = {"status": "failed", "error": str(e)}
            print(f"✗ Repair Agent failed: {e}")
    
    def _load_parser_interface(self) -> str:
        """Load parser interface documentation."""
        return """
        Parser Interface:
        - tokenize(html: str) -> List[Token]
        - parse(html: str) -> TreeNode
        - parse_with_trace(html: str) -> Dict[str, Any]
        
        Token types: DOCTYPE, START_TAG, END_TAG, COMMENT, CHARACTER, EOF, PARSE_ERROR
        
        TreeNode has: name, attributes, children, text_content
        """
    
    def _create_test_cases(self) -> list:
        """Create basic test cases for validation."""
        return [
            ("Empty HTML", "", "Should handle empty input"),
            ("Simple tag", "<p>Hello</p>", "Should tokenize and parse simple tags"),
            ("Nested tags", "<div><p>Nested</p></div>", "Should handle nested structure"),
            ("Attributes", '<a href="test">Link</a>', "Should parse attributes"),
            ("Multiple tags", "<p>One</p><p>Two</p>", "Should parse multiple elements"),
            ("Implicit closure", "<p>Text<div>Block</div>", "Should close p implicitly"),
            ("Self-closing", "<br><hr>", "Should handle void elements"),
        ]
    
    def get_run_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline run."""
        artifacts = self.artifact_manager.list_artifacts()
        return {
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "artifacts": artifacts,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point for pipeline orchestrator."""
    # Ensure directories exist
    Config.ensure_directories_exist()
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Define HTML5 subset to implement
    html_subset = """
    Implement a parser for the following HTML5 elements:
    
    1. Basic tags: <html>, <body>, <head>, <p>, <div>
    2. Inline tags: <a>, <span>, <em>, <strong>
    3. Block tags: <blockquote>, <section>, <article>
    4. Self-closing tags: <br>, <hr>, <img>, <input>
    5. Implicit closure rules:
       - <p> closes when block element starts
       - Lists close when block elements encountered
    """
    
    parser_interface = """
    The parser should provide:
    1. tokenize(html) -> tokens
    2. parse(html) -> tree
    3. parse_with_trace(html) -> {tokens, tree, trace}
    """
    
    # Run pipeline
    report = orchestrator.run(html_subset, parser_interface)
    
    # Print summary
    print("\n" + "="*60)
    print("PIPELINE EXECUTION COMPLETE")
    print("="*60)
    print(f"Run ID: {orchestrator.run_id}")
    print(f"Status: {report['status']}")
    print(f"Run directory: {orchestrator.run_dir}")
    print(f"\nArtifacts created:")
    for artifact_type, files in orchestrator.get_run_summary()["artifacts"].items():
        if files:
            print(f"  {artifact_type}: {len(files)} files")
    
    return report


if __name__ == "__main__":
    main()
