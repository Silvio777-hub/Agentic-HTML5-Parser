"""
scripts/serve_dashboard.py — Local HTTP Server & Live HTML Parser API.

This script launches a lightweight Python HTTP server that:
1. Serves the static Quality Dashboard (HTML, CSS, JS) at http://localhost:8080/dashboard/
2. Provides a live REST API endpoint (POST /api/parse) that accepts raw HTML and
   executes our Python parser with full execution tracing in real-time.
3. Automatically runs sample compliance tests on startup so fresh data is always present.

Usage:
    python scripts/serve_dashboard.py [--port 8080] [--no-browser]
"""

import os
import sys
import json
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


class DashboardAndAPIRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP Request Handler that serves static files and handles
    live parsing POST requests from the interactive dashboard playground.
    """

    def do_POST(self):
        """Handle incoming POST requests for live HTML parsing."""
        parsed_url = urlparse(self.path)

        # Handle POST /api/parse — Live Interactive Playground REST endpoint
        # Accepts JSON payload: {"html": "<markup>"} and returns parsed DOM + telemetry
        if parsed_url.path == "/api/parse":
            try:
                # Step 1: Read incoming request payload length from HTTP headers
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                
                # 2. Parse request JSON payload
                payload = json.loads(post_data) if post_data else {}
                raw_html = payload.get("html", "")

                # 3. Execute our Agentic AI HTML5 Parser with execution tracing
                result = parse_with_trace(raw_html)

                # 4. Prepare JSON response payload
                response_payload = {
                    "success": True,
                    "input_length": len(raw_html),
                    "tokens": result.get("tokens", []),
                    "tree": result.get("tree", {}),
                    "trace": result.get("trace", {}),
                    "duration_ms": round(result.get("trace", {}).get("duration", 0) * 1000.0, 3)
                }
                response_bytes = json.dumps(response_payload, indent=2).encode("utf-8")

                # 5. Send HTTP 200 OK headers
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")  # Allow cross-origin if needed
                self.end_headers()

                # 6. Write response body
                self.wfile.write(response_bytes)

            except Exception as exc:
                # Handle any parser or JSON decoding errors gracefully
                error_response = json.dumps({"success": False, "error": str(exc)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(error_response)))
                self.end_headers()
                self.wfile.write(error_response)
        else:
            # For unhandled POST routes, return 404 Not Found
            self.send_error(404, "Endpoint Not Found")

    def do_OPTIONS(self):
        """Handle pre-flight CORS OPTIONS requests for API endpoints."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


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
    print(f"  --> Dashboard URL: {dashboard_url}")
    print(f"  --> Live Parse API: POST http://localhost:{port}/api/parse")
    print("=" * 70)
    print("  Press Ctrl+C in terminal to stop the server.\n")

    # Automatically launch user's default browser if requested
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

    # Step 1: Ensure compliance results exist
    run_initial_compliance()
    
    # Step 2: Start server
    start_server(port=args.port, open_browser=not args.no_browser)
