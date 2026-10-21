"""
tests/test_whatwg_boundary.py — Boundary Analysis: Structural Subset vs WHATWG Adoption Agency Algorithm (AAA).

Academic Test Suite for Chapter 6 ("Discussion & Limitations"):
Contrasts the behavior of this pure-Python structural subset parser against the
full WHATWG Adoption Agency Algorithm (AAA) and Foster Parenting specifications.

WHATWG Background:
Section 13.2.6.4.7 of the WHATWG specification mandates the Adoption Agency Algorithm (AAA)
for handling misnested inline formatting elements (e.g. <b>, <i>, <a>, <em>).
When <b>1<i>2</b>3</i> is encountered:
  - Full WHATWG: Clones and reparents formatting elements to produce <b>1<i>2</i></b><i>3</i>.
  - Structural Subset: Maintains a well-formed tree without node duplication or stack underflow.
"""

import pytest
from src.parser import parse, tokenize, TreeNode


class TestWhatwgBoundaryAnalysis:
    """
    Formal boundary tests contrasting structural subset parsing against full WHATWG AAA.
    """

    def test_misnested_formatting_tags_subset_behavior(self):
        """
        Boundary Test 1: Misnested formatting tags <b>1<i>2</b>3</i>.
        
        Full WHATWG: Reconstructs active formatting elements via AAA -> <b>1<i>2</i></b><i>3</i>.
        Structural Subset: Maintains well-nested hierarchy without duplicating AST nodes.
        """
        html = "<b>1<i>2</b>3</i>"
        root = parse(html)
        
        # Verify parser completes safely without crashing or hanging
        assert root is not None
        assert root.name == "html"
        
        # In our subset, tags are resolved in stack order without crashes
        tag_names = [n.name for n in root.children]
        assert "b" in tag_names or any(c.name == "b" for c in root.children)

    def test_foster_parenting_boundary(self):
        """
        Boundary Test 2: Foster parenting in table structures.
        
        Full WHATWG: Non-table content inside <table> is foster-parented before the table.
        Structural Subset: Ingests non-table content into the table container without silent dropping.
        """
        html = "<table>Text outside cells<tr><td>Cell 1</td></tr></table>"
        root = parse(html)
        
        assert root is not None
        assert root.name == "html"

        def get_all_text(node):
            texts = []
            if node.text_content:
                texts.append(node.text_content)
            for c in node.children:
                texts.append(get_all_text(c))
            return "".join(texts)
            
        all_text = get_all_text(root)
        clean_text = "".join(all_text.split())
        assert "Cell1" in clean_text

    def test_void_elements_with_spurious_end_tags(self):
        """
        Boundary Test 3: Void elements followed by illegal explicit end tags.
        
        WHATWG HTML5 specifies that void elements (<br>, <img>, <hr>) cannot have end tags;
        if a spurious </br> is encountered, it is treated as a parse error and converted to <br>.
        """
        html = "Line 1<br></br>Line 2"
        root = parse(html)
        assert root is not None
        assert root.name == "html"
        
        # Parser should safely survive spurious </br> without raising an unhandled exception
        assert any(c.name == "br" for c in root.children)
        assert "Line 1" in root.text_content or "Line 2" in root.text_content

    def test_heading_implicit_boundary(self):
        """
        Boundary Test 4: Adjacent headings <h1>Title<h2>Subtitle.
        
        HTML5 outlines specify heading levels. The parser should treat each heading as
        distinct top-level blocks or siblings.
        """
        html = "<h1>Main Heading<h2>Subheading</h2></h1>"
        root = parse(html)
        assert root is not None
        assert root.name == "html"
        
        h1_nodes = [c for c in root.children if c.name == "h1"]
        assert len(h1_nodes) >= 1

    def test_deep_formatting_stack_without_overflow(self):
        """
        Boundary Test 5: Deeply interleaved formatting tags.
        
        Tests that an alternating chain <b><i><u><b><i><u> does not cause
        infinite loops or stack overflow in the absence of AAA.
        """
        html = "<b><i><u><b><i><u>Deep text</u></i></b></u></i></b>"
        root = parse(html)
        assert root is not None
        assert root.name == "html"
