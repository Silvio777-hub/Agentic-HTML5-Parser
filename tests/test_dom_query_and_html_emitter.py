"""
tests/test_dom_query_and_html_emitter.py — Comprehensive tests for:
1. DOM Query & Search API (find, find_all, select, select_one, get_text, .text)
2. Reverse HTML Serialization (to_html) and Round-Trip fidelity.
"""

import pytest
from src.parser import parse, TreeNode


@pytest.fixture
def sample_dom():
    html = """
    <div id="container" class="layout main-content">
        <header id="top-header">
            <h1 class="title">Agentic AI HTML5 Parser</h1>
            <nav class="navigation">
                <a href="/home" class="nav-link active">Home</a>
                <a href="/docs" class="nav-link">Documentation</a>
                <a href="/tests" class="nav-link">Test Matrix</a>
            </nav>
        </header>
        <main>
            <section class="card" data-category="compiler">
                <h2>Lexical Tokenizer</h2>
                <p class="body-text">Emits 11 states of tokens.</p>
                <img src="diagram.png" alt="Architecture Diagram">
            </section>
            <section class="card featured" data-category="agentic">
                <h2>Autonomous Self-Repair</h2>
                <p class="body-text">Trace-guided patching within 3 loops.</p>
                <input type="text" name="repair_status" value="verified" disabled>
            </section>
        </main>
        <footer>
            <p class="copyright">&copy; 2026 Silvio JM Opoka</p>
        </footer>
    </div>
    """
    return parse(html)


class TestDOMQueryAPI:
    """Tests for TreeNode.find, find_all, select, select_one, and text extraction."""

    def test_find_by_tag_name(self, sample_dom):
        h1 = sample_dom.find("h1")
        assert h1 is not None
        assert h1.name == "h1"
        assert "Agentic AI" in h1.text

    def test_find_by_id(self, sample_dom):
        header = sample_dom.find(id="top-header")
        assert header is not None
        assert header.name == "header"
        assert header.attributes.get("id") == "top-header"

    def test_find_by_class(self, sample_dom):
        nav_link = sample_dom.find("a", class_="active")
        assert nav_link is not None
        assert nav_link.attributes.get("href") == "/home"

    def test_find_non_existent(self, sample_dom):
        non_existent = sample_dom.find("table")
        assert non_existent is None

    def test_find_all_tags(self, sample_dom):
        all_links = sample_dom.find_all("a")
        assert len(all_links) == 3
        hrefs = [a.attributes.get("href") for a in all_links]
        assert "/home" in hrefs
        assert "/docs" in hrefs
        assert "/tests" in hrefs

    def test_find_all_with_limit(self, sample_dom):
        two_links = sample_dom.find_all("a", limit=2)
        assert len(two_links) == 2

    def test_find_all_with_class_filter(self, sample_dom):
        cards = sample_dom.find_all("section", class_="card")
        assert len(cards) == 2

    def test_select_tag_and_class(self, sample_dom):
        titles = sample_dom.select("h1.title")
        assert len(titles) == 1
        assert "Agentic AI" in titles[0].text

    def test_select_descendant_combinator(self, sample_dom):
        nav_links = sample_dom.select("header nav a")
        assert len(nav_links) == 3

    def test_select_by_id(self, sample_dom):
        nodes = sample_dom.select("#container")
        assert len(nodes) == 1
        assert nodes[0].attributes.get("id") == "container"

    def test_select_attribute_selector(self, sample_dom):
        featured = sample_dom.select("[data-category='agentic']")
        assert len(featured) == 1
        assert featured[0].name == "section"

    def test_select_one(self, sample_dom):
        footer_p = sample_dom.select_one("footer p.copyright")
        assert footer_p is not None
        assert "Silvio" in footer_p.text

    def test_get_text_extraction(self, sample_dom):
        header = sample_dom.find("header")
        text = header.get_text(separator=" ", strip=True)
        assert "Agentic AI HTML5 Parser" in text
        assert "Home" in text


class TestReverseHTMLEmitter:
    """Tests for TreeNode.to_html() serialization and round-trip fidelity."""

    def test_to_html_basic(self):
        html_input = "<div><p>Simple paragraph</p></div>"
        tree = parse(html_input)
        rendered = tree.to_html(pretty=False)
        assert "<p>Simple paragraph</p>" in rendered
        assert "<div>" in rendered and "</div>" in rendered

    def test_to_html_pretty_indented(self):
        html_input = "<div><p>Hello</p></div>"
        tree = parse(html_input)
        pretty = tree.to_html(pretty=True)
        assert "\n" in pretty
        assert "  " in pretty
        assert "<p>Hello</p>" in pretty

    def test_void_elements_do_not_emit_closing_tag(self):
        html_input = "<p>Line 1<br>Line 2<hr><img src='pic.jpg'></p>"
        tree = parse(html_input)
        rendered = tree.to_html()
        assert "<br>" in rendered
        assert "</br>" not in rendered
        assert "<hr>" in rendered
        assert "</hr>" not in rendered
        assert "<img src=\"pic.jpg\">" in rendered
        assert "</img>" not in rendered

    def test_round_trip_parse_html(self):
        """Validates that HTML -> AST -> HTML -> AST produces identical structures."""
        original_html = "<article class=\"story\"><h1>News</h1><p>Breaking story content.</p></article>"
        tree1 = parse(original_html)
        emitted_html = tree1.to_html()
        tree2 = parse(emitted_html)

        # Confirm structural isomorphism
        assert tree1.find("h1").text == tree2.find("h1").text
        assert tree1.find("p").text == tree2.find("p").text
        assert tree1.find("article").attributes == tree2.find("article").attributes
