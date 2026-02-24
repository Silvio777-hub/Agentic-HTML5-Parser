"""
Utility functions for file operations, patching, and artifact management.
Handles reading/writing specifications, patches, and reports.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
from difflib import unified_diff


class ArtifactManager:
    """Manages creation, storage, and retrieval of pipeline artifacts."""
    
    def __init__(self, run_id: str, run_dir: Path):
        """
        Initialize artifact manager for a specific pipeline run.
        
        Args:
            run_id: Unique identifier for this pipeline run
            run_dir: Directory where artifacts will be stored
        """
        self.run_id = run_id
        self.run_dir = run_dir
        
        # Create subdirectories
        self.spec_dir = run_dir / "spec"
        self.patch_dir = run_dir / "patches"
        self.report_dir = run_dir / "reports"
        self.trace_dir = run_dir / "traces"
        
        for directory in [self.spec_dir, self.patch_dir, self.report_dir, self.trace_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_specification(self, spec_data: Dict[str, Any]) -> Path:
        """
        Save structured specification as YAML.
        
        Args:
            spec_data: Dictionary containing specification rules
            
        Returns:
            Path to saved spec file
        """
        spec_file = self.spec_dir / "spec.yml"
        with open(spec_file, 'w') as f:
            yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False)
        return spec_file
    
    def load_specification(self) -> Dict[str, Any]:
        """Load specification from YAML file."""
        spec_file = self.spec_dir / "spec.yml"
        if not spec_file.exists():
            return {}
        with open(spec_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def save_patch(self, patch_content: str, patch_name: str = "code.patch") -> Path:
        """
        Save unified diff patch.
        
        Args:
            patch_content: Unified diff content
            patch_name: Name of patch file
            
        Returns:
            Path to saved patch file
        """
        patch_file = self.patch_dir / patch_name
        with open(patch_file, 'w') as f:
            f.write(patch_content)
        return patch_file
    
    def save_report(self, report_data: Dict[str, Any], report_name: str = "report.json") -> Path:
        """
        Save report as JSON.
        
        Args:
            report_data: Dictionary containing report data
            report_name: Name of report file
            
        Returns:
            Path to saved report file
        """
        report_file = self.report_dir / report_name
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        return report_file
    
    def save_trace(self, trace_data: Dict[str, Any], trace_name: str = "execution.json") -> Path:
        """
        Save execution trace as JSON.
        
        Args:
            trace_data: Dictionary containing trace events
            trace_name: Name of trace file
            
        Returns:
            Path to saved trace file
        """
        trace_file = self.trace_dir / trace_name
        with open(trace_file, 'w') as f:
            json.dump(trace_data, f, indent=2)
        return trace_file
    
    def list_artifacts(self) -> Dict[str, List[str]]:
        """List all artifacts in this run."""
        return {
            "specs": [f.name for f in self.spec_dir.glob("*.yml")],
            "patches": [f.name for f in self.patch_dir.glob("*.patch")],
            "reports": [f.name for f in self.report_dir.glob("*.json")],
            "traces": [f.name for f in self.trace_dir.glob("*.json")]
        }


class PatchManager:
    """Handles creation and application of unified diff patches."""
    
    @staticmethod
    def create_patch(old_content: str, new_content: str, 
                    filename: str = "file.py", context_lines: int = 3) -> str:
        """
        Create a unified diff patch.
        
        Args:
            old_content: Original file content
            new_content: Modified file content
            filename: Name of file being patched
            context_lines: Number of context lines in diff
            
        Returns:
            Unified diff patch as string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = unified_diff(old_lines, new_lines, 
                          fromfile=f"a/{filename}",
                          tofile=f"b/{filename}",
                          lineterm='')
        
        return '\n'.join(diff)
    
    @staticmethod
    def apply_patch(patch_content: str, target_file: Path) -> bool:
        """
        Apply a unified diff patch to a file.
        
        Args:
            patch_content: Unified diff patch
            target_file: File to patch
            
        Returns:
            True if patch applied successfully
        """
        try:
            # Write patch to temporary file
            patch_file = target_file.parent / ".temp.patch"
            with open(patch_file, 'w') as f:
                f.write(patch_content)
            
            # Apply patch using git apply
            result = subprocess.run(
                ['git', 'apply', str(patch_file)],
                capture_output=True,
                text=True,
                cwd=target_file.parent
            )
            
            # Clean up temp patch
            patch_file.unlink()
            
            return result.returncode == 0
        except Exception as e:
            print(f"Error applying patch: {e}")
            return False


class ReportGenerator:
    """Generates structured reports for pipeline stages."""
    
    @staticmethod
    def create_test_report(passed: int, failed: int, errors: List[str],
                          traces: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create test execution report.
        
        Args:
            passed: Number of passing tests
            failed: Number of failing tests
            errors: List of error messages
            traces: Optional execution traces
            
        Returns:
            Test report dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "success_rate": (passed / (passed + failed)) if (passed + failed) > 0 else 0
            },
            "errors": errors,
            "traces": traces or {}
        }
    
    @staticmethod
    def create_repair_report(repair_patch: str, tests_before: Dict[str, Any],
                            tests_after: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create repair operation report.
        
        Args:
            repair_patch: Patch that was applied
            tests_before: Test results before repair
            tests_after: Test results after repair
            
        Returns:
            Repair report dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "patch": repair_patch[:500],  # First 500 chars
            "results": {
                "before": tests_before,
                "after": tests_after,
                "improvement": tests_after["summary"]["success_rate"] - 
                             tests_before["summary"]["success_rate"]
            }
        }


if __name__ == "__main__":
    # Test artifact manager
    from datetime import datetime
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    manager = ArtifactManager(run_id, Path(f"runs/{run_id}"))
    
    spec = {
        "name": "HTML5 Parser Spec",
        "version": "0.1.0",
        "rules": {
            "p_closure": "Paragraph implicitly closes before block elements"
        }
    }
    
    spec_path = manager.save_specification(spec)
    print(f"Saved spec to: {spec_path}")
    
    loaded_spec = manager.load_specification()
    print(f"Loaded spec: {loaded_spec}")
    
    print(f"Artifacts: {manager.list_artifacts()}")
