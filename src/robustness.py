"""
Robustness and security wrappers for the Agentic AI HTML5 Parser.
Provides sandboxing via multiprocessing and structural integrity enforcement.
"""

import multiprocessing
import time
from typing import Dict, Any, Optional
from src.parser import parse, TreeNode

class SandboxWrapper:
    """
    Utilizes multiprocessing to isolate the parsing logic for security and reliability.
    """
    
    @staticmethod
    def _parse_worker(html: str, queue: multiprocessing.Queue):
        """Worker function for subprocess execution."""
        try:
            tree = parse(html)
            queue.put({"success": True, "tree": tree.serialize()})
        except Exception as e:
            queue.put({"success": False, "error": str(e)})

    @staticmethod
    def safe_parse(html: str, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Run the parser in a separate process with a timeout.
        """
        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=SandboxWrapper._parse_worker, args=(html, queue))
        
        process.start()
        process.join(timeout)
        
        if process.is_alive():
            process.terminate()
            process.join()
            return {"success": False, "error": f"Parsing timed out after {timeout} seconds"}
        
        if queue.empty():
            return {"success": False, "error": "Parser failed to return result"}
            
        return queue.get()

class IntegrityWrapper:
    """
    A post-parse verification layer that enforces DOM depth and token limits.
    """
    
    def __init__(self, max_depth: int = 100, max_nodes: int = 1000):
        self.max_depth = max_depth
        self.max_nodes = max_nodes

    def verify(self, root: TreeNode) -> Dict[str, Any]:
        """Check if the tree complies with structural constraints."""
        node_count = self._count_nodes(root)
        max_depth = self._get_depth(root)
        
        issues = []
        if node_count > self.max_nodes:
            issues.append(f"Node count ({node_count}) exceeds limit ({self.max_nodes})")
        if max_depth > self.max_depth:
            issues.append(f"DOM depth ({max_depth}) exceeds limit ({self.max_depth})")
            
        return {
            "valid": len(issues) == 0,
            "node_count": node_count,
            "max_depth": max_depth,
            "issues": issues
        }

    def _count_nodes(self, node: TreeNode) -> int:
        return 1 + sum(self._count_nodes(child) for child in node.children)

    def _get_depth(self, node: TreeNode) -> int:
        if not node.children:
            return 1
        return 1 + max(self._get_depth(child) for child in node.children)

if __name__ == "__main__":
    # Test safe parse
    print("--- Sandbox Test ---")
    result = SandboxWrapper.safe_parse("<div><p>Testing Sandbox</p></div>")
    print(f"Success: {result['success']}")
    
    # Test integrity
    print("\n--- Integrity Test ---")
    node = TreeNode("root")
    curr = node
    for i in range(10): # Depth 11
        new_node = TreeNode(f"level_{i}")
        curr.add_child(new_node)
        curr = new_node
        
    wrapper = IntegrityWrapper(max_depth=5)
    print(wrapper.verify(node))
