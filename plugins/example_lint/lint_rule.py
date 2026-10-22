"""
plugins/example_lint/lint_rule.py — Deprecated HTML Tag Linter Plugin.

This example plugin hooks into the ``after_parse`` event and traverses the
parsed DOM tree to emit warnings for any deprecated HTML tags it finds.

Deprecated tags checked:   <center>, <font>, <marquee>, <blink>

These tags are part of the legacy presentational HTML specification and have
been removed from the HTML Living Standard.  Modern CSS should be used instead.
"""

from __future__ import annotations

from typing import Any

# Tags that are deprecated in the HTML Living Standard.
DEPRECATED_TAGS = frozenset(["center", "font", "marquee", "blink"])


def _walk(node: Any, found: list) -> None:
    """Recursively walk a TreeNode tree and collect deprecated tag names."""
    tag_name = getattr(node, "tag_name", None) or getattr(node, "name", None)
    if tag_name and str(tag_name).lower() in DEPRECATED_TAGS:
        found.append(str(tag_name).lower())

    children = getattr(node, "children", []) or []
    for child in children:
        _walk(child, found)


def _on_after_parse(html: str = "", tree: Any = None, **kwargs: Any) -> None:
    """
    Hook callback for the ``after_parse`` event.

    Walks the tree looking for deprecated tags and prints a warning for each
    unique tag found.

    Parameters
    ----------
    html:
        The original HTML source string (provided by the emit call).
    tree:
        The root ``TreeNode`` returned by the parser.
    **kwargs:
        Additional keyword arguments (ignored for forward‑compatibility).
    """
    if tree is None:
        return

    found: list[str] = []
    _walk(tree, found)

    unique_tags = sorted(set(found))
    for tag in unique_tags:
        count = found.count(tag)
        plural = "s" if count > 1 else ""
        print(
            f"[example-lint] WARNING: Deprecated tag <{tag}> found "
            f"{count} time{plural}. "
            f"Use CSS equivalents instead."
        )


def register(manager: Any) -> None:
    """
    Entry point called by PluginManager when loading this plugin.

    Registers the ``after_parse`` hook so deprecated‑tag linting runs
    automatically after every parse operation.

    Parameters
    ----------
    manager:
        The ``PluginManager`` instance.
    """
    manager.register_hook("after_parse", _on_after_parse)
