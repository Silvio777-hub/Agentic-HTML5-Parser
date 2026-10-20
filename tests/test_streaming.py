"""
tests/test_streaming.py — Unit tests for parse_stream and tokenize_stream APIs.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from parser import tokenize_stream, parse_stream, TokenType


def test_tokenize_stream_basic():
    chunks = ["<div", " class='test'", ">", "<span>Hello", "</span></div>"]
    tokens = list(tokenize_stream(chunks))
    assert len(tokens) > 0
    tag_names = [t.name for t in tokens if t.name]
    assert "div" in tag_names
    assert "span" in tag_names


def test_parse_stream_incremental_build():
    chunks = [
        "<html><head><title>Streaming Test</title></head>",
        "<body><main>",
        "<p>Paragraph 1</p>",
        "<p>Paragraph 2</p>",
        "</main></body></html>"
    ]
    updates = list(parse_stream(chunks))
    assert len(updates) == len(chunks)
    assert updates[-1]["accumulated_bytes"] > updates[0]["accumulated_bytes"]
    final_tree = updates[-1]["tree"]
    assert final_tree["name"] == "html"
