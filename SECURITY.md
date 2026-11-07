# Security Policy — Agentic AI HTML5 Parser

## Supported Versions

| Version | Supported |
|---|---|
| 1.4.x (current) | ✅ Yes |
| 1.3.x | ⚠️ Critical fixes only |
| < 1.3.0 | ❌ No |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. **Email:** Send details to `opoka2010@gmail.com` with the subject line:
   `[SECURITY] Agentic-HTML5-Parser — <brief description>`

2. **Include in your report:**
   - A description of the vulnerability
   - Steps to reproduce the issue
   - The potential impact (e.g., parser crash, memory exhaustion, code injection)
   - Any suggested fix (optional but appreciated)

3. **Response time:** You will receive an acknowledgement within **48 hours** and a full response within **7 days**.

### What Happens Next

- If the vulnerability is confirmed, a fix will be developed and released as a patch version.
- You will be credited in the `CHANGELOG.md` and release notes (unless you prefer to remain anonymous).
- If the issue is not a valid security concern, we will explain why and may direct you to open a regular GitHub Issue instead.

## Security Design of This Project

This project includes several built-in security measures documented in `README.md`:

1. **API Key Protection:** `.env` file is gitignored; never committed to version control.
2. **Input Validation:** Parser validates and sanitises all HTML input before processing.
3. **Resource Limits:** Robustness Wrapper enforces a 50ms timeout and memory caps per parse.
4. **Bounded Repair Loop:** Hard cap of 3 repair iterations prevents infinite LLM execution loops.
5. **Static Analysis:** `scripts/run_security_audit.py` performs AST-level vulnerability scanning on the codebase.
6. **STRIDE Threat Model:** 6-point threat model (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) validated against the full pipeline.

## Scope

Security reports are **in scope** for:
- Parser crashes caused by crafted HTML input
- Memory exhaustion or denial-of-service via crafted input
- LLM prompt injection through the agent pipeline
- API key leakage or credential exposure

Security reports are **out of scope** for:
- Vulnerabilities in third-party dependencies (report these to the respective project)
- Issues that require physical access to the host machine
- Social engineering attacks

---

*Last updated: November 2026*
