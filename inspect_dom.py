"""
Visual DOM Inspector
Provides a colorized, indented tree view of the parsed HTML.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.parser import parse, TreeNode

# ANSI Colors
COLORS = {
    'tag': '\033[94m',      # Blue
    'attr_key': '\033[92m', # Green
    'attr_val': '\033[93m', # Yellow
    'text': '\033[0m',      # Reset
    'reset': '\033[0m'
}

def inspect_node(node: TreeNode, indent=0):
    prefix = "  " * indent
    
    # Tag Start
    line = f"{prefix}{COLORS['tag']}<{node.name}"
    
    # Attributes
    for k, v in node.attributes.items():
        line += f" {COLORS['attr_key']}{k}={COLORS['attr_val']}\"{v}\""
    
    line += f"{COLORS['tag']}>"
    print(line)
    
    # Content
    if node.text_content.strip():
        print(f"{prefix}  {COLORS['text']}{node.text_content.strip()}")
        
    # Children
    for child in node.children:
        inspect_node(child, indent + 1)
        
    # Tag End
    print(f"{prefix}{COLORS['tag']}</{node.name}>{COLORS['reset']}")

def main():
    if len(sys.argv) > 1:
        # Check if it's a file or direct string
        arg = sys.argv[1]
        if Path(arg).exists():
            html = Path(arg).read_text()
        else:
            html = arg
    else:
        # Default demo
        html = '<div id="app" class="main-container"><p>Hello <b>World</b>!</p><ul class="list"><li>Item 1</li><li>Item 2</li></ul></div>'
    
    print("\n" + "="*40)
    print("VISUAL DOM INSPECTOR")
    print("="*40 + "\n")
    
    try:
        root = parse(html)
        inspect_node(root)
    except Exception as e:
        print(f"Error inspecting DOM: {e}")
    
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
