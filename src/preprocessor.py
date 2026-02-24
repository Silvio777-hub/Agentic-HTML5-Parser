"""
Preprocessor for the Agentic AI HTML5 Parser.
Converts input text into Intermediate Representation (IR).
"""

from typing import List, Dict, Any

class Preprocessor:
    """
    Utility to convert natural language text or simple structures into IR.
    """
    
    def process(self, text: str) -> List[Dict[str, Any]]:
        """
        Convert text into IR (list of dictionaries describing elements).
        Simple heuristic: lines starting with '#' are headers (div style), 
        normal lines are paragraphs.
        """
        ir = []
        lines = text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("#"):
                # Interpret as a header/div
                content = line.lstrip("#").strip()
                ir.append({
                    "tag": "div",
                    "attributes": {"class": "header"},
                    "content": content
                })
            elif line.startswith("-"):
                # Interpret as list item
                content = line.lstrip("-").strip()
                ir.append({
                    "tag": "li",
                    "content": content
                })
            else:
                # Interpret as paragraph
                ir.append({
                    "tag": "p",
                    "content": line
                })
                
        return ir

if __name__ == "__main__":
    p = Preprocessor()
    test_text = "# Title\nThis is a paragraph.\n- Item 1\n- Item 2"
    print(p.process(test_text))
