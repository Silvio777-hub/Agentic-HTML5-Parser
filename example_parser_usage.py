"""
Example: Using the Agentic AI HTML5 Parser

This script demonstrates how to use the parser directly without the AI pipeline.
Perfect for testing and understanding the core parsing functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parser import tokenize, parse, parse_with_trace, TokenType

def example_1_basic_tokenization():
    """Example 1: Basic HTML tokenization"""
    print("=" * 60)
    print("EXAMPLE 1: Basic HTML Tokenization")
    print("=" * 60)
    
    html = "<p>Hello World</p>"
    tokens = tokenize(html)
    
    print(f"\nHTML: {html}")
    print(f"\nTokens generated: {len(tokens)}")
    for i, token in enumerate(tokens, 1):
        print(f"  {i}. {token.type.value:15} | name={token.name} | data={token.data}")
    print()


def example_2_parsing_to_tree():
    """Example 2: Parse HTML into a DOM tree"""
    print("=" * 60)
    print("EXAMPLE 2: Parsing HTML to DOM Tree")
    print("=" * 60)
    
    html = """
    <div id="main">
        <p>First paragraph</p>
        <p>Second paragraph</p>
    </div>
    """
    
    root = parse(html)
    
    print(f"\nHTML Input:")
    print(html)
    print(f"\nDOM Tree Structure:")
    print(f"  Root: {root.name}")
    print(f"  Children: {len(root.children)}")
    for i, child in enumerate(root.children, 1):
        print(f"    {i}. {child.name} (attributes: {child.attributes})")
        for j, grandchild in enumerate(child.children, 1):
            print(f"       {j}. {grandchild.name} (text: '{grandchild.text_content}')")
    print()


def example_3_execution_tracing():
    """Example 3: Parse with execution tracing for debugging"""
    print("=" * 60)
    print("EXAMPLE 3: Execution Tracing")
    print("=" * 60)
    
    html = "<p>Test</p>"
    result = parse_with_trace(html)
    
    print(f"\nHTML: {html}")
    print(f"Tokens: {len(result['tokens'])}")
    
    # The trace is returned as a serialized dict
    trace_data = result.get('trace', {})
    events = trace_data.get('events', [])
    
    print(f"Parse Events: {len(events)}")
    
    print("\nExecution Events:")
    for event in events[:10]:  # Show first 10 events
        print(f"  - {event.get('type', 'unknown'):25} | {event}")
    
    if len(events) > 10:
        print(f"  ... and {len(events) - 10} more events")
    
    elapsed = trace_data.get('elapsed_time', 0)
    print(f"\nParsing Time: {elapsed:.4f}s")
    print()


def example_4_attributes_and_hierarchy():
    """Example 4: Complex HTML with attributes"""
    print("=" * 60)
    print("EXAMPLE 4: Attributes & Hierarchy")
    print("=" * 60)
    
    html = """
    <div class="container" id="main-content">
        <header>
            <h1>Page Title</h1>
            <nav>Menu</nav>
        </header>
        <section class="content">
            <article>
                <h2>Article Title</h2>
                <p>Content here</p>
            </article>
        </section>
    </div>
    """
    
    root = parse(html)
    
    def print_tree(node, indent=0):
        """Recursively print the tree structure"""
        attrs_str = f" {node.attributes}" if node.attributes else ""
        text_str = f" [text: '{node.text_content[:20]}...']" if len(node.text_content) > 20 else f" [text: '{node.text_content}']" if node.text_content else ""
        print("  " * indent + f"<{node.name}>{attrs_str}{text_str}")
        for child in node.children:
            print_tree(child, indent + 1)
    
    print(f"\nHTML Input: {len(html)} characters")
    print("\nDOM Tree Hierarchy:")
    print_tree(root)
    print()


def example_5_implicit_tag_closure():
    """Example 5: Implicit tag closure rules"""
    print("=" * 60)
    print("EXAMPLE 5: Implicit Tag Closure")
    print("=" * 60)
    
    # Without closing </p>, it should close implicitly before <div>
    html = """
    <div>
        <p>First paragraph
        <div>
            <p>Nested paragraph</p>
        </div>
    </div>
    """
    
    root = parse(html)
    
    print(f"\nHTML (note: <p> not explicitly closed):")
    print(html)
    print(f"\nParsed Structure:")
    
    def count_nodes(node):
        return 1 + sum(count_nodes(child) for child in node.children)
    
    print(f"Total nodes: {count_nodes(root)}")
    print(f"Root children: {len(root.children)}")
    for child in root.children:
        print(f"  - {child.name}: {len(child.children)} children")
    print()


def example_6_error_handling():
    """Example 6: Error handling with malformed HTML"""
    print("=" * 60)
    print("EXAMPLE 6: Error Handling")
    print("=" * 60)
    
    html = """
    <div>
        <p>Unclosed paragraph
        <span>Nested
        </div>
    </div>
    """
    
    result = parse_with_trace(html)

    # trace and tree are returned as serialized dicts
    trace_data = result.get('trace', {})
    parse_errors = trace_data.get('parse_errors', [])

    print(f"\nMalformed HTML:")
    print(html)
    print(f"\nParsing Errors: {len(parse_errors)}")
    for error in parse_errors:
        print(f"  - {error}")

    tree = result.get('tree', {})
    print(f"\nParsed anyway: {tree.get('name')}")
    print(f"Children: {len(tree.get('children', []))}")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AGENTIC AI HTML5 PARSER - EXAMPLES" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        example_1_basic_tokenization()
        example_2_parsing_to_tree()
        example_3_execution_tracing()
        example_4_attributes_and_hierarchy()
        example_5_implicit_tag_closure()
        example_6_error_handling()
        
        print("=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print("\nNext Steps:")
        print("  1. Edit .env and add your GROQ_API_KEY")
        print("  2. Run: python orchestrator.py")
        print("  3. Check runs/[timestamp]/ for AI-generated artifacts")
        print()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
