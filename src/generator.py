"""
Generator for the Agentic AI HTML5 Parser.
Converts Intermediate Representation (IR) into standards-compliant HTML5.
"""

from typing import List, Dict, Any

class Generator:
    """
    Utility to render IR into standards-compliant HTML5.
    """
    
    def generate(self, ir: List[Dict[str, Any]]) -> str:
        """
        Render IR into HTML string.
        """
        html_output = "<!DOCTYPE html>\n<html>\n<body>\n"
        
        for item in ir:
            tag = item.get("tag", "p")
            attrs = item.get("attributes", {})
            content = item.get("content", "")
            
            attr_str = ""
            for k, v in attrs.items():
                attr_str += f' {k}="{v}"'
                
            html_output += f"  <{tag}{attr_str}>{content}</{tag}>\n"
            
        html_output += "</body>\n</html>"
        return html_output

if __name__ == "__main__":
    g = Generator()
    test_ir = [
        {"tag": "div", "attributes": {"class": "header"}, "content": "Title"},
        {"tag": "p", "content": "This is a paragraph."},
        {"tag": "li", "content": "Item 1"}
    ]
    print(g.generate(test_ir))
