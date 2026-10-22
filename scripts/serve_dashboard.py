"""
scripts/serve_dashboard.py — Local HTTP Server & Live HTML Parser API.

This script launches a lightweight Python HTTP server that:
1. Serves the static Quality Dashboard (HTML, CSS, JS) at http://localhost:8080/dashboard/
2. Provides a live REST API endpoint (POST /api/parse) that accepts raw HTML and
   executes our Python parser with full execution tracing in real-time.
3. Provides a differential diff endpoint (POST /api/diff) that compares our parser's
   DOM tree side-by-side against BeautifulSoup4 as a differential oracle.
4. Automatically runs sample compliance tests on startup so fresh data is always present.

Usage:
    python scripts/serve_dashboard.py [--port 8080] [--no-browser]
"""

import os
import sys
import json
import time
import argparse
import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Ensure project root is available in sys.path for internal imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import our custom HTML5 parser and tracing functions
from src.parser import parse_with_trace, tokenize, parse

# Import BeautifulSoup4 for differential oracle comparisons
try:
    from bs4 import BeautifulSoup, Tag, NavigableString
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def serialize_bs4_node(node):
    """
    Recursively serialize a BeautifulSoup node into our standard tree dict format.
    Compatible with how our parser serializes TreeNode objects.
    """
    if isinstance(node, NavigableString):
        text = str(node).strip()
        if not text:
            return None
        return {"name": "#text", "attributes": {}, "text_content": text, "children": []}
    elif isinstance(node, Tag):
        children = []
        for child in node.children:
            sc = serialize_bs4_node(child)
            if sc:
                children.append(sc)
        attrs = {}
        for k, v in node.attrs.items():
            attrs[k] = " ".join(v) if isinstance(v, list) else str(v)
        return {
            "name": node.name,
            "attributes": attrs,
            "text_content": "",
            "children": children
        }
    return None


def parse_with_bs4_structured(html_str):
    """
    Parse HTML with BeautifulSoup4 using html.parser backend and return
    a tree dict compatible with our parser's serialized format.
    """
    soup = BeautifulSoup(html_str, "html.parser")
    children = [sc for child in soup.children if (sc := serialize_bs4_node(child))]
    return {"name": "html", "attributes": {}, "text_content": "", "children": children}


def tree_signature(node):
    """
    Compute a compact structural signature string from a tree dict,
    used to compare DOM topology between parsers.
    """
    if not isinstance(node, dict):
        return ""
    name = node.get("name", "")
    children = node.get("children", [])
    return f"{name}({'|'.join(tree_signature(c) for c in children)})"


class DashboardAndAPIRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP Request Handler that serves static files and handles
    live parsing POST requests from the interactive dashboard playground.

    Endpoints:
        GET  /dashboard/   — Serves the static HTML5 dashboard
        POST /api/parse    — Parse HTML with our parser, return DOM + trace
        POST /api/diff     — Differential oracle: compare our parser vs BS4 side-by-side
        POST /api/run_tests — Run pytest suite and return pass/fail counts
    """

    def do_POST(self):
        """Handle incoming POST requests for live HTML parsing and differential oracle."""
        parsed_url = urlparse(self.path)

        # -------------------------------------------------------
        # POST /api/diff — Differential DOM Visualizer Endpoint
        # Compares our Agentic parser vs BeautifulSoup4 oracle
        # -------------------------------------------------------
        if parsed_url.path == "/api/diff":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(post_data) if post_data else {}
                raw_html = payload.get("html", "")

                # Measure tokenizer stage separately
                t_tok0 = time.perf_counter()
                tokenize(raw_html)
                tokenizer_ms = round((time.perf_counter() - t_tok0) * 1000.0, 3)

                # Measure parser stage separately
                t_par0 = time.perf_counter()
                parse(raw_html)
                parser_ms = round((time.perf_counter() - t_par0) * 1000.0, 3)

                # Time our full parser with trace
                t0 = time.perf_counter()
                our_res = parse_with_trace(raw_html)
                diff_ms = round((time.perf_counter() - t0) * 1000.0, 3)
                our_tree = our_res.get("tree", {})

                # Time BeautifulSoup4 parser
                if BS4_AVAILABLE:
                    t1 = time.perf_counter()
                    bs4_tree = parse_with_bs4_structured(raw_html)
                    t_bs4 = round((time.perf_counter() - t1) * 1000.0, 3)
                else:
                    bs4_tree = {"name": "N/A", "attributes": {}, "text_content": "BeautifulSoup4 not installed.", "children": []}
                    t_bs4 = 0.0

                our_sig = tree_signature(our_tree)
                bs4_sig = tree_signature(bs4_tree)

                response_payload = {
                    "success": True,
                    "input_html": raw_html,
                    "our_tree": our_tree,
                    "bs4_tree": bs4_tree,
                    "diff_ms": diff_ms,
                    "tokenizer_ms": tokenizer_ms,
                    "parser_ms": parser_ms,
                    "our_duration_ms": diff_ms,
                    "bs4_duration_ms": t_bs4,
                    "is_match": (our_sig == bs4_sig),
                    "our_signature": our_sig,
                    "bs4_signature": bs4_sig
                }
                self._send_json(200, response_payload)

            except Exception as exc:
                self._send_json(500, {"success": False, "error": str(exc)})
            return

        # -------------------------------------------------------
        # POST /api/parse — Live Interactive Playground Endpoint
        # Accepts JSON: {"html": "<markup>"} → DOM + trace + tokens
        # Returns per-stage timing: tokenizer_ms, parser_ms, duration_ms
        # -------------------------------------------------------
        if parsed_url.path == "/api/parse":
            try:
                # Read incoming request payload
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(post_data) if post_data else {}
                raw_html = payload.get("html", "")

                # Measure tokenizer stage independently
                t_tok0 = time.perf_counter()
                tokenize(raw_html)
                tokenizer_ms = round((time.perf_counter() - t_tok0) * 1000.0, 3)

                # Measure parser stage independently (tree-building only)
                t_par0 = time.perf_counter()
                parse(raw_html)
                parser_ms = round((time.perf_counter() - t_par0) * 1000.0, 3)

                # Execute our Agentic AI HTML5 Parser with full execution tracing
                result = parse_with_trace(raw_html)

                response_payload = {
                    "success": True,
                    "input_length": len(raw_html),
                    "tokens": result.get("tokens", []),
                    "tree": result.get("tree", {}),
                    "trace": result.get("trace", {}),
                    "duration_ms": round(result.get("trace", {}).get("duration", 0) * 1000.0, 3),
                    "tokenizer_ms": tokenizer_ms,
                    "parser_ms": parser_ms,
                }
                self._send_json(200, response_payload)

            except Exception as exc:
                self._send_json(500, {"success": False, "error": str(exc)})
            return

        # -------------------------------------------------------
        # POST /api/run_tests — Run pytest suite and return results
        # Returns JSON: {success, output, passed, failed, total}
        # -------------------------------------------------------
        if parsed_url.path == "/api/run_tests":
            try:
                tests_dir = os.path.join(PROJECT_ROOT, "tests")
                proc = subprocess.run(
                    [sys.executable, "-m", "pytest", tests_dir, "-q", "--tb=line"],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                output = proc.stdout + proc.stderr

                # Parse pytest summary line: "X passed[, Y failed] in Zs"
                passed = failed = 0
                for line in output.splitlines():
                    line_stripped = line.strip()
                    if "passed" in line_stripped or "failed" in line_stripped or "error" in line_stripped:
                        import re
                        m_passed = re.search(r"(\d+)\s+passed", line_stripped)
                        m_failed = re.search(r"(\d+)\s+(?:failed|error)", line_stripped)
                        if m_passed:
                            passed = int(m_passed.group(1))
                        if m_failed:
                            failed = int(m_failed.group(1))

                total = passed + failed
                self._send_json(200, {
                    "success": proc.returncode == 0,
                    "output": output,
                    "passed": passed,
                    "failed": failed,
                    "total": total,
                    "return_code": proc.returncode,
                })
            except subprocess.TimeoutExpired:
                self._send_json(200, {
                    "success": False,
                    "output": "Test run timed out after 120 seconds.",
                    "passed": 0,
                    "failed": 0,
                    "total": 0,
                    "return_code": -1,
                })
            except Exception as exc:
                self._send_json(500, {"success": False, "error": str(exc)})
            return

        # Unhandled POST route
        self.send_error(404, "Endpoint Not Found")

    def _send_json(self, status_code, payload):
        """Helper: serialize payload to JSON and send HTTP response."""
        response_bytes = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        """Handle pre-flight CORS OPTIONS requests for API endpoints."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress verbose request logs unless there is an error."""
        if args and len(args) >= 2 and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)


def run_initial_compliance():
    """Run compliance test runner on startup to ensure data/compliance_results.json is fresh."""
    print("Running initial compliance check on sample test cases...")
    runner_script = os.path.join(PROJECT_ROOT, "scripts", "run_compliance.py")
    result = subprocess.run([sys.executable, runner_script, "--sample"], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("[Warning] Compliance runner reported an issue during initial run.")


def start_server(port: int = 8080, open_browser: bool = True):
    """Start local HTTP server rooted at the project workspace directory."""
    os.chdir(PROJECT_ROOT)
    server_address = ("", port)

    try:
        httpd = HTTPServer(server_address, DashboardAndAPIRequestHandler)
    except OSError:
        # Fallback to alternate port 8081 if 8080 is currently occupied
        port = 8081
        server_address = ("", port)
        httpd = HTTPServer(server_address, DashboardAndAPIRequestHandler)

    dashboard_url = f"http://localhost:{port}/dashboard/"
    print("\n" + "=" * 70)
    print(f"  [OK] Compliance Dashboard & Live API Server Running!")
    print(f"  --> Dashboard URL:        {dashboard_url}")
    print(f"  --> Live Parse API:       POST http://localhost:{port}/api/parse")
    print(f"  --> Differential Diff:    POST http://localhost:{port}/api/diff")
    print("=" * 70)
    print("  Press Ctrl+C in terminal to stop the server.\n")

    if open_browser:
        try:
            webbrowser.open(dashboard_url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve the HTML5 Parser Compliance Dashboard & Live API")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    run_initial_compliance()
    start_server(port=args.port, open_browser=not args.no_browser)
