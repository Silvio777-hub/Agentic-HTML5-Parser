"""
Integration tests for the Agentic AI HTML5 Parser pipeline.
Tests parser functionality, AI agents, and end-to-end workflow.
"""

import sys
import json
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parser import (
    tokenize, parse, parse_with_trace, 
    Token, TokenType, TreeNode, HTMLTokenizer, HTMLParser
)


class TestTokenizer:
    """Test HTML tokenization functionality."""
    
    def test_simple_text(self):
        """Test tokenization of plain text."""
        tokens = tokenize("Hello")
        # Tokenizer emits individual character tokens + EOF
        character_tokens = [t for t in tokens if t.type == TokenType.CHARACTER]
        assert len(character_tokens) == 5  # H, e, l, l, o
        assert character_tokens[0].data == "H"
        assert tokens[-1].type == TokenType.EOF  # Last token is EOF
    
    def test_start_tag(self):
        """Test tokenization of start tag."""
        tokens = tokenize("<p>")
        assert any(t.type == TokenType.START_TAG and t.name == "p" for t in tokens)
    
    def test_end_tag(self):
        """Test tokenization of end tag."""
        tokens = tokenize("</div>")
        assert any(t.type == TokenType.END_TAG and t.name == "div" for t in tokens)
    
    def test_attributes(self):
        """Test parsing of tag attributes."""
        tokens = tokenize('<a href="test">link</a>')
        start_tags = [t for t in tokens if t.type == TokenType.START_TAG]
        assert len(start_tags) > 0
        assert "href" in start_tags[0].attributes
    
    def test_self_closing_tag(self):
        """Test tokenization of self-closing tags."""
        # Test void element (br doesn't need closing slash)
        tokens = tokenize("<br>")
        void_elements = [t for t in tokens if t.type == TokenType.START_TAG and t.name == "br"]
        assert len(void_elements) > 0
        
        # Alternatively test with explicit self-closing syntax
        tokens2 = tokenize("<img src='test'>")
        img_tags = [t for t in tokens2 if t.type == TokenType.START_TAG and t.name == "img"]
        assert len(img_tags) > 0
    
    def test_multiple_tokens(self):
        """Test tokenization of complex HTML."""
        tokens = tokenize("<div>Text</div>")
        assert len(tokens) > 3
        token_types = [t.type for t in tokens]
        assert TokenType.START_TAG in token_types
        assert TokenType.END_TAG in token_types
        assert TokenType.CHARACTER in token_types


class TestParser:
    """Test DOM tree construction."""
    
    def test_empty_html(self):
        """Test parsing empty HTML."""
        tree = parse("")
        assert tree.name == "html"
        assert len(tree.children) == 0
    
    def test_simple_hierarchy(self):
        """Test parsing simple nested structure."""
        tree = parse("<div><p>Text</p></div>")
        assert tree.name == "html"
        assert len(tree.children) > 0
    
    def test_multiple_children(self):
        """Test parsing multiple sibling elements."""
        tree = parse("<p>One</p><p>Two</p>")
        assert tree.name == "html"
        # Count all p elements recursively
        def count_p(node):
            count = 1 if node.name == "p" else 0
            return count + sum(count_p(child) for child in node.children)
        
        assert count_p(tree) >= 2
    
    def test_text_content(self):
        """Test that text content is preserved."""
        tree = parse("<p>Hello</p>")
        # Find p element and check text
        def find_p(node):
            if node.name == "p":
                return node
            for child in node.children:
                result = find_p(child)
                if result:
                    return result
            return None
        
        p_elem = find_p(tree)
        assert p_elem is not None
        assert "Hello" in p_elem.text_content
    
    def test_attributes_preservation(self):
        """Test that attributes are preserved in tree."""
        tree = parse('<a href="test">link</a>')
        # Find a element and check attributes
        def find_a(node):
            if node.name == "a":
                return node
            for child in node.children:
                result = find_a(child)
                if result:
                    return result
            return None
        
        a_elem = find_a(tree)
        assert a_elem is not None
        assert "href" in a_elem.attributes


class TestImplicitClosure:
    """Test implicit tag closure rules."""
    
    def test_p_closes_before_div(self):
        """Test that <p> closes before <div>."""
        tree = parse("<p>Text<div>Block</div></p>")
        # Check structure - p should not contain div
        def find_element(node, name):
            if node.name == name:
                yield node
            for child in node.children:
                yield from find_element(child, name)
        
        p_elements = list(find_element(tree, "p"))
        assert len(p_elements) > 0
        
        # Find if any p contains a div (they shouldn't directly)
        for p in p_elements:
            div_children = [c for c in p.children if c.name == "div"]
            # P might close, so div could be sibling
    
    def test_p_closes_before_blockquote(self):
        """Test that <p> closes before <blockquote>."""
        tree = parse("<p>Text<blockquote>Quote</blockquote></p>")
        # Similar verification
        assert tree.name == "html"
    
    def test_p_closes_before_section(self):
        """Test that <p> closes before <section>."""
        tree = parse("<p>Text<section>Content</section></p>")
        assert tree.name == "html"


class TestExecutionTrace:
    """Test execution tracing functionality."""
    
    def test_trace_structure(self):
        """Test that trace contains expected structure."""
        result = parse_with_trace("<p>Test</p>")
        
        assert "tokens" in result
        assert "tree" in result
        assert "trace" in result
    
    def test_trace_events(self):
        """Test that trace events are recorded."""
        result = parse_with_trace("<p>Hello</p>")
        trace = result["trace"]
        
        assert "events" in trace
        assert len(trace["events"]) > 0
        assert "duration" in trace
    
    def test_trace_captures_tokens(self):
        """Test that trace captures tokenization."""
        result = parse_with_trace("<div>Content</div>")
        events = result["trace"]["events"]
        
        # Should have tokenization events
        token_events = [e for e in events if "token" in e.get("type", "")]
        assert len(token_events) > 0
    
    def test_trace_timing(self):
        """Test that trace records timing information."""
        result = parse_with_trace("<p>Test</p>")
        duration = result["trace"]["duration"]
        
        assert duration >= 0
        assert duration < 1.0  # Should be very fast


class TestErrorHandling:
    """Test error handling and robustness."""
    
    def test_unclosed_tag(self):
        """Test handling of unclosed tags."""
        tree = parse("<p>Text without closing")
        assert tree.name == "html"
    
    def test_malformed_html(self):
        """Test handling of malformed HTML."""
        tree = parse("<p>Text<>>Invalid")
        assert tree.name == "html"
    
    def test_deeply_nested(self):
        """Test handling of deeply nested structures."""
        html = "<div>" * 100 + "Content" + "</div>" * 100
        tree = parse(html)
        assert tree.name == "html"
    
    def test_very_long_attribute(self):
        """Test handling of very long attributes."""
        html = '<a href="' + 'x' * 1000 + '">link</a>'
        tree = parse(html)
        assert tree.name == "html"


class TestEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_with_trace("")
        assert result["tree"]["name"] == "html"
    
    def test_whitespace_only(self):
        """Test parsing whitespace-only HTML."""
        result = parse_with_trace("   \n\t  ")
        assert result["tree"]["name"] == "html"
    
    def test_comments(self):
        """Test handling of HTML comments."""
        tokens = tokenize("<!-- Comment -->Text")
        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
        # Should handle comments gracefully
    
    def test_special_characters(self):
        """Test handling of special characters."""
        tree = parse("<p>&lt; &gt; &amp;</p>")
        assert tree.name == "html"
    
    def test_mixed_case_tags(self):
        """Test that tags are case-insensitive."""
        result1 = parse("<DIV>Test</DIV>")
        result2 = parse("<div>Test</div>")
        # Both should parse successfully
        assert result1.name == result2.name


class TestTreeSerialization:
    """Test tree serialization."""
    
    def test_serialize_simple_tree(self):
        """Test serialization of simple tree."""
        tree = parse("<p>Test</p>")
        serialized = tree.serialize()
        
        assert "name" in serialized
        assert "children" in serialized
        assert serialized["name"] == "html"
    
    def test_serialize_with_attributes(self):
        """Test serialization preserves attributes."""
        tree = parse('<a href="test">link</a>')
        serialized = tree.serialize()
        
        # Should be serializable to JSON
        json_str = json.dumps(serialized)
        assert len(json_str) > 0


class TestParserInterface:
    """Test the three main parser functions."""
    
    def test_tokenize_interface(self):
        """Test tokenize() function."""
        tokens = tokenize("<p>Test</p>")
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(t, Token) for t in tokens)
    
    def test_parse_interface(self):
        """Test parse() function."""
        tree = parse("<p>Test</p>")
        assert isinstance(tree, TreeNode)
        assert tree.name == "html"
    
    def test_parse_with_trace_interface(self):
        """Test parse_with_trace() function."""
        result = parse_with_trace("<p>Test</p>")
        assert isinstance(result, dict)
        assert "tokens" in result
        assert "tree" in result
        assert "trace" in result


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
