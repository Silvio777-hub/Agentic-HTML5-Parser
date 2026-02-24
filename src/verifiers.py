"""
Verification tools for the Agentic AI HTML5 Parser.
Includes DOM querying, semantic auditing, and differential testing.
"""

from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import random
from src.parser import TreeNode, parse

class SelectorAgent:
    """
    Programmatic utility to search the DOM tree by ID or tag name.
    """
    
    @staticmethod
    def select_by_id(root: TreeNode, target_id: str) -> Optional[TreeNode]:
        """Search for a node with a specific ID."""
        if root.attributes.get("id") == target_id:
            return root
        for child in root.children:
            result = SelectorAgent.select_by_id(child, target_id)
            if result:
                return result
        return None

    @staticmethod
    def select_by_tag(root: TreeNode, tag_name: str) -> List[TreeNode]:
        """Search for all nodes with a specific tag name."""
        results = []
        if root.name == tag_name:
            results.append(root)
        for child in root.children:
            results.extend(SelectorAgent.select_by_tag(child, tag_name))
        return results

class SemanticComplianceAuditor:
    """
    Enforces HTML5 content model rules and detects invalid nesting.
    """
    
    # Rules: parent tag -> tags it CANNOT contain
    INVALID_NESTING = {
        "p": ["div", "p", "blockquote", "header", "footer", "section", "article"],
        "ul": ["p", "div"], # Simplified: should only contain li, but we'll focus on block elements
        "li": ["header", "footer"]
    }

    def __init__(self):
        self.violations = []

    def audit(self, root: TreeNode) -> Dict[str, Any]:
        """Audit the tree for semantic violations."""
        self.violations = []
        self._check_node(root)
        
        score = max(0, 100 - (len(self.violations) * 10))
        return {
            "score": score,
            "violations": self.violations,
            "status": "PASS" if score == 100 else "FAIL"
        }

    def _check_node(self, node: TreeNode):
        children_names = [child.name for child in node.children]
        forbidden = self.INVALID_NESTING.get(node.name, [])
        
        for child_name in children_names:
            if child_name in forbidden:
                self.violations.append(f"Invalid nesting: <{child_name}> inside <{node.name}>")
        
        for child in node.children:
            self._check_node(child)

class DifferentialOracle:
    """
    Comparison logic to validate the parser against BeautifulSoup4 (reference).
    """
    
    @staticmethod
    def compare(html: str, target_tree: TreeNode) -> Dict[str, Any]:
        """Compare our parser output with BS4."""
        soup = BeautifulSoup(html, "html.parser")
        # Simplified comparison: compare tag hierarchy
        ref_structure = DifferentialOracle._get_structure_bs4(soup)
        our_structure = DifferentialOracle._get_structure_our(target_tree)
        
        matches = ref_structure == our_structure
        return {
            "matches": matches,
            "ref_tags": len(ref_structure),
            "our_tags": len(our_structure),
            "details": "Structure matches reference" if matches else "Structural discrepancy detected"
        }

    @staticmethod
    def _get_structure_bs4(soup_node) -> List[str]:
        tags = []
        name = getattr(soup_node, "name", None)
        if name and name not in ("[document]", "html", "body"):
            tags.append(name)
        for child in getattr(soup_node, "children", []):
            tags.extend(DifferentialOracle._get_structure_bs4(child))
        return tags

    @staticmethod
    def _get_structure_our(node: TreeNode) -> List[str]:
        tags = []
        if node.name not in ("html", "body"):
            tags.append(node.name)
        for child in node.children:
            tags.extend(DifferentialOracle._get_structure_our(child))
        return tags

class SecurityFuzzer:
    """
    Targeted malformed input generator.
    """
    
    @staticmethod
    def generate_wild_html(complexity: int = 5) -> str:
        """Generate messy HTML for stress testing."""
        tags = ["div", "p", "span", "b", "i", "ul", "li"]
        html = ""
        stack = []
        
        for _ in range(complexity):
            action = random.choice(["open", "close", "text", "attr"])
            if action == "open":
                tag = random.choice(tags)
                html += f"<{tag}>"
                stack.append(tag)
            elif action == "close" and stack:
                tag = stack.pop()
                html += f"</{tag}>"
            elif action == "text":
                html += " fuzzy_data "
            elif action == "attr":
                html += f'<div id="{"".join(random.choices("abc", k=5))}" class="test">content</div>'
        
        # Close remaining tags
        while stack:
            html += f"</{stack.pop()}>"
        return html

if __name__ == "__main__":
    # Quick test
    test_html = "<div><p id='target'>Hello</p><div><span>Test</span></div></div>"
    root = parse(test_html)
    
    print("--- Selector Agent ---")
    target = SelectorAgent.select_by_id(root, "target")
    print(f"ID Search: {target.name if target else 'Not Found'}")
    
    print("\n--- Compliance Audit ---")
    bad_html = "<p><div>Forbidden</div></p>"
    bad_root = parse(bad_html)
    auditor = SemanticComplianceAuditor()
    print(auditor.audit(bad_root))
    
    print("\n--- Differential Oracle ---")
    oracle = DifferentialOracle()
    print(oracle.compare(test_html, root))
