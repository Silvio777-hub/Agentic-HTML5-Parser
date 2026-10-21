"""
tests/test_entity_decoding.py — Tests for HTML5 Entity and Character Reference Decoding.

Covers:
- Named entities (&amp;, &lt;, &gt;, &quot;, &apos;, &nbsp;, &copy;, &euro;)
- Numeric decimal references (&#60;, &#38;, &#169;)
- Numeric hexadecimal references (&#x3c;, &#x3C;, &#x26;)
- Entity decoding within attribute values (<a href="...?a=1&amp;b=2">)
- Unescaped ampersand fallback behavior (& not followed by valid entity)
"""

import pytest
from src.parser import parse, tokenize, TokenType


class TestHTMLEntityDecoding:
    """Validates HTML5 character reference resolution across text and attributes."""

    def test_named_entities_in_text(self):
        html = "<p>&lt;div&gt; &amp; &quot;quote&quot; &apos;apostrophe&apos; &copy; &euro;</p>"
        tree = parse(html)
        text = tree.find("p").text
        assert "<div>" in text
        assert "&" in text
        assert '"quote"' in text
        assert "'apostrophe'" in text
        assert "©" in text
        assert "€" in text

    def test_numeric_decimal_entities(self):
        html = "<p>Decimal entities: &#60;tag&#62; and &#38; and &#169;</p>"
        tree = parse(html)
        text = tree.find("p").text
        assert "<tag>" in text
        assert "&" in text
        assert "©" in text

    def test_numeric_hex_entities(self):
        html = "<p>Hex entities: &#x3c;tag&#x3e; and &#x26; and &#xA9;</p>"
        tree = parse(html)
        text = tree.find("p").text
        assert "<tag>" in text
        assert "&" in text
        assert "©" in text

    def test_entities_in_attribute_values(self):
        html = '<a href="search?query=AI&amp;lang=en&amp;sort=desc" title="&quot;Search&quot;">Click</a>'
        tree = parse(html)
        link = tree.find("a")
        assert link is not None
        assert link.attributes.get("href") == "search?query=AI&lang=en&sort=desc"
        assert link.attributes.get("title") == '"Search"'

    def test_unescaped_ampersand_fallback(self):
        """Standalone ampersands not forming valid references should be preserved verbatim."""
        html = "<p>AT&T and Barnes & Noble and & alone</p>"
        tree = parse(html)
        text = tree.find("p").text
        assert "AT&T" in text
        assert "Barnes & Noble" in text
        assert "& alone" in text

    def test_entities_in_token_stream(self):
        """Verify tokens emitted reflect decoded characters."""
        html = "<p>5 &lt; 10</p>"
        tokens = tokenize(html)
        char_tokens = [t.data for t in tokens if t.type == TokenType.CHARACTER]
        text_joined = "".join(char_tokens)
        assert "5 < 10" in text_joined
