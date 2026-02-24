# Release v1.3.0 (Draft)

This is a draft of the release notes for v1.3.0. Use this as the body for a GitHub release.

Highlights
- Added production-grade pipeline with selector agent and semantic compliance auditor.
- Full attribute parsing and improved FSM-based parser.
- End-to-end pipeline, diffs, and PPTX/DOCX report generation.

Changes
- Added `src/preprocessor.py`, `src/generator.py` for IR → HTML rendering.
- Added `end_to_end.py` to run the full pipeline and generate reports.
- Added tests and CI workflow.

How to reproduce
1. Run `python -m venv .venv` and activate the environment.
2. `pip install -r requirements.txt`
3. `python -m pytest` to run tests.
4. `python end_to_end.py` to generate reports and outputs.

Notes
- This release is prepared for demonstration and internal review. Create the GitHub release from the `v1.3.0` tag and attach artifacts as needed.
