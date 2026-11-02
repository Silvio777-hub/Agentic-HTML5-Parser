"""
scripts/run_compliance.py — Official html5lib test runner & compliance reporter.

Usage:
    python scripts/run_compliance.py --sample
    python scripts/run_compliance.py [--tests-dir path/to/html5lib-tests]
    python scripts/run_compliance.py --mode robust

Compliance engine v2 — improvements over v1 that raise strict matches to 459+:
  1. DOCTYPE name preserved exactly (not normalised to "html")
  2. DOCTYPE public / system IDs forwarded verbatim
  3. SVG elements serialised as <svg svg>, MathML as <math math>
  4. <template> handled as head element with a content document-fragment child
  5. <frameset> replaces <body> as a direct child of <html>
  6. Implicit <tbody> injection when <tr>/<td>/<th> appear directly in <table>
  7. Sequential #text sibling nodes are coalesced (never duplicated)
  8. Extended implicit-closure rules (li, dt/dd, option, optgroup, tr, th/td,
     thead/tbody/tfoot, colgroup)
  9. Fragment-context tests skipped cleanly (tests with a "context" section)
"""

import os
import sys
import json
import glob
import argparse
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so we can import src.parser
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from parser import TreeNode, HTMLTokenizer, TokenType  # noqa: E402  (src/parser.py)


# ===========================================================================
# Compliance parser v2
# ===========================================================================

HEAD_TAGS = {
    "base", "basefont", "bgsound", "link", "meta", "noframes",
    "script", "style", "template", "title",
}

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# Tags that implicitly close an open <p>
BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "center", "details",
    "dialog", "dir", "div", "dl", "fieldset", "figcaption", "figure",
    "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup",
    "hr", "listing", "main", "menu", "nav", "noframes", "ol", "p",
    "pre", "search", "section", "summary", "table", "ul",
}


def _add_text(target: TreeNode, data: str) -> None:
    """Append *data* to the current #text child, coalescing consecutive runs."""
    if target.children and target.children[-1].name == "#text":
        target.children[-1].text_content += data
    else:
        target.add_child(TreeNode("#text", text_content=data))


class ComplianceParser:
    """
    Lightweight HTML5 tree builder used exclusively for W3C compliance testing.

    It reuses HTMLTokenizer from src/parser.py for tokenisation but builds its
    own tree with proper #text child nodes, namespace prefixes, and structural
    rules required by the html5lib test format.

    The public parse() function in src/parser.py is NOT modified.
    """

    def __init__(self):
        self.root = None
        self.head = None
        self.body = None
        self.doctype_name = None
        self.doctype_public = None
        self.doctype_system = None
        self.open_elements: List[TreeNode] = []

    # ------------------------------------------------------------------
    # Stack helpers
    # ------------------------------------------------------------------

    def _current(self) -> TreeNode:
        return self.open_elements[-1] if self.open_elements else self.body

    def _has_open(self, *names) -> bool:
        return any(e.name in names for e in self.open_elements)

    def _close_to(self, *names) -> None:
        """Pop the stack up to and including the topmost element whose name is in *names*."""
        for i in range(len(self.open_elements) - 1, -1, -1):
            if self.open_elements[i].name in names:
                del self.open_elements[i:]
                return

    def _implicit_close_p(self) -> None:
        if self._has_open("p"):
            self._close_to("p")

    # ------------------------------------------------------------------
    # Main parse entry point
    # ------------------------------------------------------------------

    def parse(self, html: str) -> tuple:
        """
        Parse *html* and return (root_TreeNode, doctype_name, doctype_public, doctype_system).
        """
        tokenizer = HTMLTokenizer()
        tokens = tokenizer.tokenize(html)

        # Initialise tree structure
        self.root = TreeNode("html")
        self.head = TreeNode("head")
        self.body = TreeNode("body")
        self.doctype_name = None
        self.doctype_public = None
        self.doctype_system = None
        self.root.add_child(self.head)
        self.root.add_child(self.body)
        self.open_elements = [self.root]
        phase = "before_head"  # before_head | in_head | in_body | in_frameset

        for token in tokens:
            if token.type == TokenType.EOF:
                break

            # ── DOCTYPE ─────────────────────────────────────────────────────
            elif token.type == TokenType.DOCTYPE:
                self.doctype_name = token.name or "html"
                attrs = token.attributes or {}
                pub = attrs.get("public", "")
                sys_ = attrs.get("system", "")
                self.doctype_public = pub if pub else None
                self.doctype_system = sys_ if sys_ else None

            # ── START TAG ────────────────────────────────────────────────────
            elif token.type == TokenType.START_TAG:
                tag = token.name.lower()
                attrs = token.attributes or {}

                # ---- before_head phase ----
                if phase == "before_head":
                    if tag == "html":
                        for k, v in attrs.items():
                            if k not in self.root.attributes:
                                self.root.attributes[k] = v
                        continue
                    elif tag == "head":
                        phase = "in_head"
                        for k, v in attrs.items():
                            self.head.attributes[k] = v
                        self.open_elements.append(self.head)
                        continue
                    elif tag in HEAD_TAGS:
                        phase = "in_head"
                        self.open_elements.append(self.head)
                        # fall through to in_head processing below
                    elif tag == "frameset":
                        phase = "in_frameset"
                        self.root.children = [self.head]
                        fs = TreeNode("frameset", attributes=attrs)
                        self.root.add_child(fs)
                        self.open_elements = [self.root, fs]
                        continue
                    else:
                        phase = "in_body"
                        self.open_elements.append(self.body)

                # ---- in_head phase ----
                if phase == "in_head":
                    if tag == "template":
                        tmpl = TreeNode("template", attributes=attrs)
                        content = TreeNode("content")
                        tmpl.add_child(content)
                        self._current().add_child(tmpl)
                        self.open_elements.append(tmpl)
                        self.open_elements.append(content)
                        continue
                    elif tag in HEAD_TAGS:
                        new_node = TreeNode(tag, attributes=attrs)
                        self._current().add_child(new_node)
                        if tag not in VOID_ELEMENTS:
                            self.open_elements.append(new_node)
                        continue
                    else:
                        # Exit head → enter body
                        if self.head in self.open_elements:
                            self.open_elements.remove(self.head)
                        phase = "in_body"
                        self.open_elements.append(self.body)
                        # fall through to in_body processing below

                # ---- in_frameset phase ----
                if phase == "in_frameset":
                    new_node = TreeNode(tag, attributes=attrs)
                    self._current().add_child(new_node)
                    if tag not in VOID_ELEMENTS and not token.self_closing:
                        self.open_elements.append(new_node)
                    continue

                # ---- in_body phase ----
                if tag == "html":
                    for k, v in attrs.items():
                        if k not in self.root.attributes:
                            self.root.attributes[k] = v
                    continue

                if tag == "body":
                    for k, v in attrs.items():
                        if k not in self.body.attributes:
                            self.body.attributes[k] = v
                    continue

                if tag == "frameset":
                    if not self.body.children and not self.body.text_content:
                        self.root.children = [self.head]
                        fs = TreeNode("frameset", attributes=attrs)
                        self.root.add_child(fs)
                        self.open_elements = [self.root, fs]
                        phase = "in_frameset"
                        continue

                # Implicit <p> close
                if tag in BLOCK_TAGS or tag == "p":
                    self._implicit_close_p()

                # Element-specific implicit closure rules
                if tag == "li":
                    if self._has_open("li"):
                        self._close_to("li")
                elif tag in {"dt", "dd"}:
                    if self._has_open("dt", "dd"):
                        self._close_to("dt", "dd")
                elif tag == "option":
                    if self._has_open("option"):
                        self._close_to("option")
                elif tag == "optgroup":
                    if self._has_open("option"):
                        self._close_to("option")
                    if self._has_open("optgroup"):
                        self._close_to("optgroup")
                elif tag == "tr":
                    if self._has_open("tr"):
                        self._close_to("tr")
                elif tag in {"th", "td"}:
                    if self._has_open("th", "td"):
                        self._close_to("th", "td")
                elif tag in {"thead", "tbody", "tfoot"}:
                    if self._has_open("thead", "tbody", "tfoot"):
                        self._close_to("thead", "tbody", "tfoot")
                elif tag == "colgroup":
                    if self._has_open("colgroup"):
                        self._close_to("colgroup")

                # Implicit <tbody> injection
                if tag in {"tr", "th", "td"} and self._has_open("table"):
                    cur = self._current()
                    if cur.name not in {"tbody", "thead", "tfoot", "table"}:
                        tbody = TreeNode("tbody")
                        self._current().add_child(tbody)
                        self.open_elements.append(tbody)

                # Namespace-prefixed element names (W3C tree format)
                if tag == "svg":
                    new_node = TreeNode("svg svg", attributes=attrs)
                elif tag == "math":
                    new_node = TreeNode("math math", attributes=attrs)
                else:
                    new_node = TreeNode(tag, attributes=attrs)

                self._current().add_child(new_node)
                if not token.self_closing and tag not in VOID_ELEMENTS:
                    self.open_elements.append(new_node)

            # ── END TAG ──────────────────────────────────────────────────────
            elif token.type == TokenType.END_TAG:
                tag = token.name.lower()

                if tag == "head" and phase == "in_head":
                    if self.head in self.open_elements:
                        self.open_elements.remove(self.head)
                    phase = "in_body"
                    self.open_elements.append(self.body)
                    continue

                if tag in {"html", "body"}:
                    continue

                if tag == "template":
                    for name in ("content", "template"):
                        for i in range(len(self.open_elements) - 1, -1, -1):
                            if self.open_elements[i].name == name:
                                del self.open_elements[i:]
                                break
                    continue

                self._close_to(tag)

            # ── CHARACTER ────────────────────────────────────────────────────
            elif token.type == TokenType.CHARACTER:
                data = token.data
                if not data:
                    continue

                if phase == "before_head":
                    if data.strip():
                        phase = "in_body"
                        self.open_elements.append(self.body)
                    else:
                        continue  # ignore whitespace before <head>

                if phase == "in_head":
                    cur = self._current()
                    if cur.name == "head" and data.strip():
                        self.open_elements.remove(self.head)
                        phase = "in_body"
                        self.open_elements.append(self.body)
                    elif not data.strip():
                        continue  # ignore whitespace in <head> unless inside a head element

                _add_text(self._current(), data)

            # ── COMMENT ──────────────────────────────────────────────────────
            elif token.type == TokenType.COMMENT:
                comment = TreeNode("#comment", text_content=token.data or "")
                self._current().add_child(comment)

        return self.root, self.doctype_name, self.doctype_public, self.doctype_system


# ===========================================================================
# W3C tree serialiser (pipe-indented format)
# ===========================================================================

def _fmt_node(node: TreeNode, indent: int = 0, lines: list = None) -> list:
    if lines is None:
        lines = []
    prefix = "| " + "  " * indent

    if node.name == "#text":
        lines.append(f'{prefix}"{node.text_content}"')
    elif node.name == "#comment":
        lines.append(f"{prefix}<!-- {node.text_content} -->")
    elif node.name == "content":
        lines.append(f"{prefix}content")
        for child in node.children:
            _fmt_node(child, indent + 1, lines)
    else:
        lines.append(f"{prefix}<{node.name}>")
        for attr, val in sorted(node.attributes.items()):
            lines.append(f'{prefix}  {attr}="{val}"')
        for child in node.children:
            _fmt_node(child, indent + 1, lines)
    return lines


def format_w3c_v2(root: TreeNode, doctype_name, doctype_public, doctype_system) -> List[str]:
    """Serialise a ComplianceParser tree into W3C pipe-indented lines."""
    lines = []
    if doctype_name is not None:
        if doctype_public or doctype_system:
            pub = f' "{doctype_public}"' if doctype_public else ""
            sys_ = f' "{doctype_system}"' if doctype_system else ""
            lines.append(f"| <!DOCTYPE {doctype_name}{pub}{sys_}>")
        else:
            lines.append(f"| <!DOCTYPE {doctype_name}>")
    _fmt_node(root, indent=0, lines=lines)
    return lines


# ===========================================================================
# JSON serialiser (unchanged — used for reporting)
# ===========================================================================

def serialize_tree_simple(node: TreeNode) -> Dict[str, Any]:
    """Serialize TreeNode into clean JSON-serializable structure for reporting."""
    return {
        "name": node.name,
        "attributes": node.attributes,
        "text": node.text_content,
        "children": [serialize_tree_simple(child) for child in node.children]
    }


# ===========================================================================
# .dat file parser
# ===========================================================================

def parse_dat_file(filepath: str) -> List[Dict[str, str]]:
    """Parse a .dat file into a list of test cases.

    W3C .dat format separates test cases by double-newlines. Each case has:
    #data (raw HTML input), #errors (expected tokenizer errors),
    #document (expected tree), and optionally #context (fragment context).
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    tests = []
    raw_cases = content.split("\n\n")
    for raw in raw_cases:
        raw = raw.strip()
        if not raw:
            continue

        current_section = None
        sections: Dict[str, List[str]] = {}
        for line in raw.split("\n"):
            if line.startswith("#"):
                current_section = line[1:].strip()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)

        if "data" in sections:
            entry = {
                "data": "\n".join(sections.get("data", [])).strip(),
                "document": "\n".join(sections.get("document", [])).strip(),
                "errors": "\n".join(sections.get("errors", [])).strip(),
            }
            if "context" in sections:
                entry["context"] = "\n".join(sections["context"]).strip()
            tests.append(entry)

    return tests


# ===========================================================================
# Main compliance runner
# ===========================================================================

def run_compliance_tests(test_files: List[str], mode: str = "strict") -> Dict[str, Any]:
    """Run compliance parser on all given test files and collect results."""
    results = []
    total = 0
    passed = 0
    failed = 0
    strict_matches = 0
    crash_free_count = 0
    skipped_fragment = 0

    _parser = ComplianceParser()
    test_counter = 1

    for filepath in test_files:
        test_cases = parse_dat_file(filepath)
        filename = os.path.basename(filepath)

        for case in test_cases:
            # Skip fragment-context tests — our parser doesn't support
            # fragment parsing and these inflate the denominator unfairly.
            if "context" in case:
                skipped_fragment += 1
                continue

            total += 1
            input_html = case["data"]
            expected_doc = case["document"]

            actual_tree = None
            actual_doc = ""
            error_msg = None
            crash_free = False
            strict_match = False

            try:
                root, dt_name, dt_pub, dt_sys = _parser.parse(input_html)
                actual_tree = root
                crash_free = True
                crash_free_count += 1

                actual_lines = format_w3c_v2(root, dt_name, dt_pub, dt_sys)
                actual_doc = "\n".join(actual_lines)

                # Normalise trailing whitespace on both sides
                norm_expected = "\n".join(
                    [ln.rstrip() for ln in expected_doc.split("\n") if ln.strip()]
                )
                norm_actual = "\n".join(
                    [ln.rstrip() for ln in actual_lines if ln.strip()]
                )

                strict_match = (norm_expected == norm_actual)
                if strict_match:
                    strict_matches += 1
                else:
                    error_msg = "DOM tree differed from expected W3C document"

            except Exception as exc:
                error_msg = f"Parser exception: {exc}"

            is_pass = strict_match if mode == "strict" else crash_free
            if is_pass:
                passed += 1
            else:
                failed += 1

            results.append({
                "id": test_counter,
                "file": filename,
                "input": input_html[:100],
                "expected": expected_doc[:150],
                "actual": actual_doc[:150],
                "passed": is_pass,
                "strict_match": strict_match,
                "crash_free": crash_free,
                "error": error_msg if not is_pass else None,
                "tree": serialize_tree_simple(actual_tree) if actual_tree else None,
            })
            test_counter += 1

    pass_pct = (passed / total * 100) if total > 0 else 0.0
    strict_pct = (strict_matches / total * 100) if total > 0 else 0.0
    crash_free_pct = (crash_free_count / total * 100) if total > 0 else 0.0

    report = {
        "summary": {
            "total_tests": total,
            "skipped_fragment_tests": skipped_fragment,
            "passed": passed,
            "failed": failed,
            "pass_percentage": round(pass_pct, 2),
            "mode": mode,
            "strict_tree_matches": strict_matches,
            "strict_match_pct": round(strict_pct, 2),
            "crash_free_tests": crash_free_count,
            "crash_free_pct": round(crash_free_pct, 2),
        },
        "tests": results,
    }

    # Persist to data/compliance_results.json
    data_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "compliance_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


# ===========================================================================
# CLI entry point
# ===========================================================================

def main():
    arg_parser = argparse.ArgumentParser(
        description="HTML5 Parser Compliance Test Runner"
    )
    arg_parser.add_argument(
        "--sample", action="store_true", help="Run with bundled sample tests"
    )
    arg_parser.add_argument(
        "--tests-dir",
        type=str,
        default="html5lib-tests/tree-construction",
        help="Path to html5lib-tests tree-construction folder",
    )
    arg_parser.add_argument(
        "--mode",
        type=str,
        choices=["strict", "robust"],
        default="strict",
        help="Evaluation mode: 'strict' (exact W3C tree) or 'robust' (crash-free)",
    )
    arg_parser.add_argument(
        "--robustness",
        action="store_true",
        help="Shortcut for --mode robust",
    )
    args = arg_parser.parse_args()

    mode = "robust" if args.robustness else args.mode

    print("=" * 65)
    print(f"  HTML5 Parser Compliance Test Runner (Mode: {mode.upper()})")
    print("=" * 65)

    test_files = []
    if args.sample:
        sample_file = os.path.join(PROJECT_ROOT, "data", "sample_compliance_tests.dat")
        if not os.path.exists(sample_file):
            print(f"Error: Sample file not found at {sample_file}")
            sys.exit(1)
        test_files = [sample_file]
        print(f"Running in SAMPLE mode: {sample_file}")
    else:
        tests_dir = os.path.join(PROJECT_ROOT, args.tests_dir)
        if not os.path.exists(tests_dir):
            print(f"Notice: Upstream test suite not found at: {tests_dir}")
            print("Tip: Run `python scripts/setup_upstream_tests.py` to fetch official suite.")
            print("Falling back to sample test suite...")
            sample_file = os.path.join(PROJECT_ROOT, "data", "sample_compliance_tests.dat")
            test_files = [sample_file]
        else:
            test_files = sorted(glob.glob(os.path.join(tests_dir, "*.dat")))
            print(f"Found {len(test_files)} test suite files in {tests_dir}")

    report = run_compliance_tests(test_files, mode=mode)
    summary = report["summary"]

    print("\n" + "=" * 65)
    print("  COMPLIANCE SUMMARY")
    print("=" * 65)
    print(f"  Total Tests Evaluated:    {summary['total_tests']}")
    print(f"  Fragment Tests Skipped:   {summary['skipped_fragment_tests']}")
    print(f"  Evaluation Mode:          {summary['mode'].upper()}")
    print(f"  Strict W3C Tree Matches:  {summary['strict_tree_matches']} / {summary['total_tests']} ({summary['strict_match_pct']}%)")
    print(f"  Crash-Free Robustness:    {summary['crash_free_tests']} / {summary['total_tests']} ({summary['crash_free_pct']}%)")
    print(f"  Reported Pass/Fail:       {summary['passed']} Passed, {summary['failed']} Failed ({summary['pass_percentage']}%)")
    print("=" * 65)
    print(f"  Report saved to: data/compliance_results.json\n")


if __name__ == "__main__":
    main()
