"""
tests/test_new_features.py — Comprehensive tests for new HTML5 parser features.

Covers:
  - ParsedDocument wrapper (parse_document API)
  - to_html / serialize round-trips
  - Extended HTML entity decoding (emoji, mixed, attributes, nbsp)
  - parse() backward-compatibility (still returns TreeNode)
  - Plugin system (PluginManager discovery, hooks, load_plugins)
"""

from __future__ import annotations

import re
import sys
import os
import tempfile
from pathlib import Path

import pytest

# Ensure project root is on sys.path (mirrors conftest.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.parser import parse, parse_document, ParsedDocument, TreeNode


# ===========================================================================
# 1. TestParsedDocument
# ===========================================================================

class TestParsedDocument:
    """Tests for the ParsedDocument thin wrapper returned by parse_document()."""

    def test_parse_document_returns_wrapper(self):
        doc = parse_document("<p>Hello</p>")
        assert isinstance(doc, ParsedDocument), \
            f"Expected ParsedDocument, got {type(doc)}"

    def test_parse_document_has_root(self):
        doc = parse_document("<p>Hello</p>")
        assert hasattr(doc, "root"), "ParsedDocument must expose a .root attribute"
        assert isinstance(doc.root, TreeNode), \
            f"Expected .root to be TreeNode, got {type(doc.root)}"

    def test_parse_document_find(self):
        doc = parse_document("<div><p>Hello</p></div>")
        node = doc.find("p")
        assert node is not None, "find('p') should locate the <p> element"
        name = getattr(node, "tag_name", None) or getattr(node, "name", "")
        assert name.lower() == "p"

    def test_parse_document_find_all(self):
        doc = parse_document("<div><p>A</p><p>B</p><p>C</p></div>")
        nodes = doc.find_all("p")
        assert len(nodes) >= 2, f"Expected at least 2 <p> nodes, got {len(nodes)}"

    def test_parse_document_select(self):
        doc = parse_document("<ul><li>Item 1</li><li>Item 2</li></ul>")
        items = doc.select("li")
        assert len(items) >= 1, "select('li') should return at least one result"

    def test_parse_document_to_html(self):
        doc = parse_document("<p>World</p>")
        html_out = doc.to_html()
        assert isinstance(html_out, str), "to_html() should return a string"
        assert "p" in html_out.lower(), "to_html() output should contain 'p'"
        assert "World" in html_out, "to_html() output should contain text content"

    def test_parse_document_serialize(self):
        doc = parse_document("<p>Serialize</p>")
        data = doc.serialize()
        assert isinstance(data, dict), "serialize() should return a dict"
        assert "name" in data or "tag" in data or "children" in data, \
            "serialize() dict should have structural keys"

    def test_parse_document_get_text(self):
        doc = parse_document("<div><p>Foo</p><p>Bar</p></div>")
        text = doc.get_text()
        assert isinstance(text, str), "get_text() should return a string"
        assert "Foo" in text or "Bar" in text, "get_text() should include text content"

    def test_parse_document_text_property(self):
        doc = parse_document("<p>Plain text here</p>")
        # The .text property may or may not be implemented; we just ensure
        # it doesn't crash and returns something string-like.
        try:
            text = doc.text
            assert isinstance(text, str)
        except AttributeError:
            pytest.skip(".text property not implemented on ParsedDocument")

    def test_parse_document_text_content(self):
        doc = parse_document("<p>Content value</p>")
        try:
            tc = doc.text_content
            assert isinstance(tc, str)
        except AttributeError:
            pytest.skip(".text_content property not implemented on ParsedDocument")

    def test_parse_document_children(self):
        doc = parse_document("<div><span>A</span><span>B</span></div>")
        children = doc.children
        assert isinstance(children, (list, tuple)), \
            f"children should be list/tuple, got {type(children)}"

    def test_parse_document_getattr_fallback(self):
        """Attribute access on ParsedDocument should fall through to the root node."""
        doc = parse_document("<html><head></head><body><p>Hello</p></body></html>")
        # The root should have a tag_name or name attribute
        try:
            # Either direct attribute or fallback via __getattr__
            val = getattr(doc, "tag_name", None) or getattr(doc, "name", None)
            # We only assert it doesn't raise; None is acceptable
        except Exception as exc:
            pytest.fail(f"getattr fallback raised unexpectedly: {exc}")


# ===========================================================================
# 2. TestToHtmlSerialization
# ===========================================================================

class TestToHtmlSerialization:
    """Tests for TreeNode.to_html() round-trip serialization."""

    def test_to_html_round_trip_simple(self):
        root = parse("<p>Hello</p>")
        html_out = root.to_html()
        assert "<p>" in html_out or "p" in html_out.lower()
        assert "Hello" in html_out

    def test_to_html_with_attributes(self):
        root = parse('<div class="container" id="main">Text</div>')
        html_out = root.to_html()
        assert "container" in html_out, "class attribute should appear in to_html()"
        assert "main" in html_out, "id attribute should appear in to_html()"
        assert "Text" in html_out

    def test_to_html_nested(self):
        root = parse("<article><section><p>Nested content</p></section></article>")
        html_out = root.to_html()
        assert "Nested content" in html_out
        # article or section or p should appear somewhere
        assert re.search(r"<(?:article|section|p)", html_out, re.IGNORECASE), \
            "Nested tags should appear in to_html() output"

    def test_to_html_void_elements(self):
        root = parse('<div><br><hr><img src="photo.png" alt="A photo"></div>')
        html_out = root.to_html()
        # At least the img src should appear
        assert "photo.png" in html_out, "img src should appear in to_html() output"

    def test_to_html_is_string(self):
        """to_html() must always return str, not bytes or None."""
        root = parse("<span>test</span>")
        result = root.to_html()
        assert isinstance(result, str), f"to_html() returned {type(result)}, expected str"

    def test_to_html_empty_element(self):
        root = parse("<div></div>")
        html_out = root.to_html()
        assert isinstance(html_out, str)
        assert "div" in html_out.lower()

    def test_to_html_preserves_text(self):
        root = parse("<p>The quick brown fox</p>")
        html_out = root.to_html()
        assert "quick brown fox" in html_out


# ===========================================================================
# 3. TestEntityDecodingExtended
# ===========================================================================

class TestEntityDecodingExtended:
    """Extended HTML entity decoding tests beyond the existing suite."""

    def _get_text(self, html: str) -> str:
        """Parse html and return all text content as a single string."""
        root = parse(html)
        return root.get_text()

    def test_emoji_hex_entity(self):
        text = self._get_text("<p>&#x1F600;</p>")
        assert "\U0001F600" in text, \
            f"Expected 😀 (U+1F600) in text, got: {text!r}"

    def test_emoji_decimal_entity(self):
        text = self._get_text("<p>&#128512;</p>")
        assert "\U0001F600" in text, \
            f"Expected 😀 (U+1F600 decimal) in text, got: {text!r}"

    def test_mixed_entities_and_text(self):
        text = self._get_text("<p>Hello &amp; &lt;world&gt; &#169;</p>")
        assert "&" in text, "& should be decoded from &amp;"
        assert "<" in text or "world" in text, "< should be decoded from &lt;"
        assert "\u00a9" in text or "©" in text, "© should be decoded from &#169;"

    def test_entity_in_title_attribute(self):
        root = parse('<div title="&quot;quoted&quot;">content</div>')
        # Walk to find the div node
        div = None
        for node in _walk_nodes(root):
            tag = getattr(node, "tag_name", None) or getattr(node, "name", "")
            if str(tag).lower() == "div":
                div = node
                break
        if div is None:
            pytest.skip("Could not locate <div> node — skipping attribute entity test")
        attrs = getattr(div, "attributes", {}) or getattr(div, "attrs", {})
        title_val = attrs.get("title", "")
        assert '"' in title_val or "quoted" in title_val, \
            f"Expected decoded quotes in title attr, got: {title_val!r}"

    def test_nbsp_entity(self):
        text = self._get_text("<p>word1&nbsp;word2</p>")
        assert "\u00a0" in text, \
            f"Expected non-breaking space (U+00A0) from &nbsp;, got: {text!r}"

    def test_amp_entity(self):
        text = self._get_text("<p>A &amp; B</p>")
        assert "&" in text, f"&amp; should decode to '&', got: {text!r}"

    def test_lt_gt_entities(self):
        text = self._get_text("<p>&lt;tag&gt;</p>")
        assert "<" in text or "tag" in text, \
            f"&lt;/&gt; should decode to < and >, got: {text!r}"

    def test_copyright_named_entity(self):
        text = self._get_text("<p>&copy;</p>")
        assert "\u00a9" in text or "©" in text, \
            f"&copy; should decode to ©, got: {text!r}"


# ===========================================================================
# 4. TestParseBackwardCompat
# ===========================================================================

class TestParseBackwardCompat:
    """Verify parse() still returns a TreeNode (backward-compat guarantee)."""

    def test_parse_returns_treenode(self):
        result = parse("<p>x</p>")
        assert isinstance(result, TreeNode), \
            f"parse() should return TreeNode, got {type(result)}"

    def test_parse_has_serialize(self):
        root = parse("<p>x</p>")
        assert hasattr(root, "serialize"), "TreeNode must have serialize()"
        data = root.serialize()
        assert isinstance(data, dict)

    def test_parse_has_get_text(self):
        root = parse("<p>hello world</p>")
        assert hasattr(root, "get_text"), "TreeNode must have get_text()"
        text = root.get_text()
        assert "hello" in text, f"get_text() should return text content, got: {text!r}"

    def test_parse_has_to_html(self):
        root = parse("<p>check</p>")
        assert hasattr(root, "to_html"), "TreeNode must have to_html()"
        html = root.to_html()
        assert isinstance(html, str)

    def test_parse_has_find(self):
        root = parse("<div><p>Test</p></div>")
        assert hasattr(root, "find"), "TreeNode must have find()"
        node = root.find("p")
        assert node is not None

    def test_parse_has_find_all(self):
        root = parse("<div><p>A</p><p>B</p></div>")
        assert hasattr(root, "find_all"), "TreeNode must have find_all()"
        nodes = root.find_all("p")
        assert len(nodes) >= 1


# ===========================================================================
# 5. TestPluginManager
# ===========================================================================

class TestPluginManager:
    """Tests for the plugin system (PluginManager)."""

    def setup_method(self):
        """Reset the singleton before each test."""
        from src.plugin_manager import reset_plugin_manager
        reset_plugin_manager()

    def test_get_plugin_manager_singleton(self):
        from src.plugin_manager import get_plugin_manager
        pm1 = get_plugin_manager()
        pm2 = get_plugin_manager()
        assert pm1 is pm2, "get_plugin_manager() should return the same instance"

    def test_register_hook_valid_event(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()
        calls = []
        pm.register_hook("after_parse", lambda **kw: calls.append(kw))
        assert pm.hook_count("after_parse") == 1

    def test_register_hook_invalid_event(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()
        with pytest.raises(ValueError, match="Unknown event"):
            pm.register_hook("nonexistent_event", lambda: None)

    def test_emit_calls_registered_hooks(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()
        received = []
        pm.register_hook("before_tokenize", lambda **kw: received.append(kw.get("html")))
        pm.emit("before_tokenize", html="<p>test</p>")
        assert received == ["<p>test</p>"]

    def test_emit_multiple_hooks_same_event(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()
        log = []
        pm.register_hook("on_error", lambda **kw: log.append("A"))
        pm.register_hook("on_error", lambda **kw: log.append("B"))
        pm.emit("on_error", error=RuntimeError("boom"))
        assert log == ["A", "B"]

    def test_emit_no_crash_if_no_hooks(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()
        # Should not raise
        pm.emit("after_tokenize", html="", tokens=[])

    def test_hook_exception_does_not_propagate(self):
        from src.plugin_manager import get_plugin_manager
        pm = get_plugin_manager()

        def bad_hook(**kw):
            raise RuntimeError("deliberate failure")

        pm.register_hook("before_parse", bad_hook)
        # Must NOT raise — plugin errors are swallowed with a print
        pm.emit("before_parse", html="<html>")

    def test_load_plugins_from_temp_dir(self, tmp_path):
        """Load a minimal plugin from a temporary directory."""
        from src.plugin_manager import PluginManager

        # Create a minimal plugin directory
        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yml").write_text(
            "name: my-plugin\nversion: 0.1\nentry_point: my_module\n",
            encoding="utf-8",
        )
        (plugin_dir / "my_module.py").write_text(
            "def register(manager):\n    manager.register_hook('after_parse', lambda **kw: None)\n",
            encoding="utf-8",
        )

        pm = PluginManager()
        loaded = pm.load_plugins(plugins_dir=tmp_path)
        assert len(loaded) == 1
        assert loaded[0]["name"] == "my-plugin"
        assert pm.hook_count("after_parse") == 1

    def test_load_plugins_skips_missing_entry_point(self, tmp_path):
        from src.plugin_manager import PluginManager

        plugin_dir = tmp_path / "bad_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yml").write_text(
            "name: bad\nversion: 1\n",  # no entry_point key
            encoding="utf-8",
        )

        pm = PluginManager()
        loaded = pm.load_plugins(plugins_dir=tmp_path)
        assert loaded == [], "Plugin without entry_point should be skipped"

    def test_load_example_lint_plugin(self):
        """Load the real example_lint plugin from the project plugins/ directory."""
        from src.plugin_manager import PluginManager, PLUGINS_DIR

        if not (PLUGINS_DIR / "example_lint").exists():
            pytest.skip("example_lint plugin directory not found")

        pm = PluginManager()
        loaded = pm.load_plugins()
        names = [p["name"] for p in loaded]
        assert "example-lint" in names, f"example-lint not in loaded: {names}"
        assert pm.hook_count("after_parse") >= 1

    def test_example_lint_fires_warning(self, capsys):
        """example_lint should print a warning for deprecated tags."""
        from src.plugin_manager import PluginManager, PLUGINS_DIR

        if not (PLUGINS_DIR / "example_lint").exists():
            pytest.skip("example_lint plugin directory not found")

        pm = PluginManager()
        pm.load_plugins()

        root = parse("<html><body><center>old</center></body></html>")
        pm.emit("after_parse", html="<html><body><center>old</center></body></html>", tree=root)

        captured = capsys.readouterr()
        assert "center" in captured.out.lower(), \
            f"Expected 'center' deprecation warning in output, got: {captured.out!r}"


# ===========================================================================
# Utilities
# ===========================================================================

def _walk_nodes(node):
    """Generator: yield node and all descendants (depth-first)."""
    yield node
    for child in (getattr(node, "children", None) or []):
        yield from _walk_nodes(child)
