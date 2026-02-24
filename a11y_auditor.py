"""
Accessibility (A11y) Auditor
Analyzes the DOM tree for common accessibility issues.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.parser import parse, TreeNode

class A11yAuditor:
    def audit(self, root: TreeNode) -> List[Dict]:
        violations = []
        self._traverse(root, violations)
        return violations

    def _traverse(self, node: TreeNode, violations: List):
        # Rule 1: Images must have alt text
        if node.name == "img":
            if "alt" not in node.attributes or not node.attributes["alt"].strip():
                violations.append({
                    "element": "img",
                    "issue": "Missing 'alt' attribute",
                    "severity": "CRITICAL",
                    "node_id": node.attributes.get("id", "N/A")
                })
        
        # Rule 2: Inputs must have labels (simplified check)
        if node.name == "input":
            # Very basic check: look for id and then a corresponding label (or parent label)
            pass # Placeholder for more complex logic
            
        # Rule 3: Headings should not be empty
        if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if not node.text_content.strip():
                violations.append({
                    "element": node.name,
                    "issue": "Empty heading",
                    "severity": "WARNING",
                    "node_id": node.attributes.get("id", "N/A")
                })

        for child in node.children:
            self._traverse(child, violations)

def main():
    html = """
    <div>
        <h1></h1>
        <img src="logo.png">
        <p>This is a paragraph.</p>
        <img src="avatar.jpg" alt="User Avatar">
        <h3>Section Title</h3>
    </div>
    """
    
    print("\n" + "="*40)
    print("ACCESSIBILITY AUDITOR")
    print("="*40 + "\n")
    
    root = parse(html)
    auditor = A11yAuditor()
    results = auditor.audit(root)
    
    if not results:
        print("[+] No accessibility issues found.")
    else:
        for v in results:
            print(f"[{v['severity']}] {v['element']}: {v['issue']}")
            
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
