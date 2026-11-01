"""
tests/test_parallel_and_utils.py
=================================
Unit tests for src/parallel_runner.py and src/utils.py.

Coverage targets
----------------
* run_agents_parallel() — ordering, exception propagation, timeout
* ArtifactManager      — init creates dirs; save/load round-trips; list_artifacts
* PatchManager         — create_patch produces valid unified diff
* ReportGenerator      — create_test_report and create_repair_report schemas

These tests are fully offline (no API keys required).
"""

import json
import time
from pathlib import Path

import pytest
import yaml

from src.parallel_runner import run_agents_parallel
from src.utils import ArtifactManager, PatchManager, ReportGenerator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_constant(value):
    """Return a zero-argument callable that returns *value*."""
    return lambda: value


def _slow_fn(delay: float, value):
    """Return a zero-argument callable that sleeps then returns *value*."""
    def fn():
        time.sleep(delay)
        return value
    return fn


def _raising_fn(exc_type, message):
    """Return a zero-argument callable that raises an exception."""
    def fn():
        raise exc_type(message)
    return fn


# ---------------------------------------------------------------------------
# run_agents_parallel — ordering
# ---------------------------------------------------------------------------

class TestRunAgentsParallelOrdering:
    """Results must match input ordering regardless of completion speed."""

    def test_single_callable(self):
        results = run_agents_parallel([_make_constant(42)])
        assert results == [42]

    def test_two_callables_fast_first(self):
        # fn[0] finishes in ~0.05 s, fn[1] finishes in ~0.1 s
        results = run_agents_parallel([
            _slow_fn(0.05, "first"),
            _slow_fn(0.10, "second"),
        ], timeout=5)
        assert results == ["first", "second"]

    def test_two_callables_slow_first(self):
        # fn[0] finishes in ~0.15 s, fn[1] finishes in ~0.02 s
        # Despite fn[1] completing first, result[0] must still be fn[0]'s value.
        results = run_agents_parallel([
            _slow_fn(0.15, "slow"),
            _slow_fn(0.02, "fast"),
        ], timeout=5)
        assert results[0] == "slow"
        assert results[1] == "fast"

    def test_three_callables_ordering(self):
        fns = [_make_constant(i * 10) for i in range(3)]
        results = run_agents_parallel(fns, timeout=5)
        assert results == [0, 10, 20]

    def test_returns_list(self):
        results = run_agents_parallel([_make_constant("x")])
        assert isinstance(results, list)

    def test_empty_list(self):
        results = run_agents_parallel([], timeout=5)
        assert results == []

    def test_string_and_dict_results(self):
        results = run_agents_parallel([
            _make_constant({"key": "val"}),
            _make_constant("string_result"),
        ], timeout=5)
        assert results[0] == {"key": "val"}
        assert results[1] == "string_result"


# ---------------------------------------------------------------------------
# run_agents_parallel — exception propagation
# ---------------------------------------------------------------------------

class TestRunAgentsParallelExceptions:
    """Exceptions inside worker threads must be re-raised in the caller."""

    def test_raises_value_error(self):
        with pytest.raises(ValueError, match="boom"):
            run_agents_parallel([_raising_fn(ValueError, "boom")], timeout=5)

    def test_raises_runtime_error(self):
        with pytest.raises(RuntimeError):
            run_agents_parallel([_raising_fn(RuntimeError, "agent crash")], timeout=5)

    def test_exception_from_one_of_two(self):
        """Even if only one callable fails the whole call must raise."""
        with pytest.raises(Exception):
            run_agents_parallel([
                _make_constant("ok"),
                _raising_fn(ValueError, "bad agent"),
            ], timeout=5)


# ---------------------------------------------------------------------------
# run_agents_parallel — timeout
# ---------------------------------------------------------------------------

class TestRunAgentsParallelTimeout:
    """Tasks that exceed the timeout must raise TimeoutError."""

    def test_timeout_raised(self):
        # sleep much longer than the allowed timeout
        with pytest.raises(TimeoutError):
            run_agents_parallel([_slow_fn(10.0, "never")], timeout=1)

    def test_no_timeout_when_fast_enough(self):
        """Should NOT raise when callable finishes well within timeout."""
        results = run_agents_parallel([_slow_fn(0.1, "done")], timeout=10)
        assert results == ["done"]


# ---------------------------------------------------------------------------
# ArtifactManager — directory initialisation
# ---------------------------------------------------------------------------

class TestArtifactManagerInit:
    """ArtifactManager.__init__ must create the four sub-directories."""

    def test_creates_subdirectories(self, tmp_path):
        am = ArtifactManager("run_001", tmp_path / "run_001")
        assert (tmp_path / "run_001" / "spec").is_dir()
        assert (tmp_path / "run_001" / "patches").is_dir()
        assert (tmp_path / "run_001" / "reports").is_dir()
        assert (tmp_path / "run_001" / "traces").is_dir()

    def test_run_id_stored(self, tmp_path):
        am = ArtifactManager("my_run", tmp_path / "my_run")
        assert am.run_id == "my_run"

    def test_idempotent_init(self, tmp_path):
        """Calling init twice on the same run_dir must not raise."""
        run_dir = tmp_path / "run_dup"
        ArtifactManager("run_dup", run_dir)
        ArtifactManager("run_dup", run_dir)   # second call — must be fine


# ---------------------------------------------------------------------------
# ArtifactManager — save / load specification
# ---------------------------------------------------------------------------

class TestArtifactManagerSpec:

    @pytest.fixture
    def am(self, tmp_path):
        return ArtifactManager("test_run", tmp_path / "test_run")

    def test_save_specification_returns_path(self, am):
        spec = {"name": "HTML5", "version": "0.1"}
        path = am.save_specification(spec)
        assert isinstance(path, Path)
        assert path.exists()

    def test_save_specification_creates_yaml(self, am):
        spec = {"name": "HTML5", "rules": {"void_elements": ["br", "img"]}}
        path = am.save_specification(spec)
        loaded = yaml.safe_load(path.read_text())
        assert loaded["name"] == "HTML5"
        assert "br" in loaded["rules"]["void_elements"]

    def test_load_specification_roundtrip(self, am):
        spec = {"name": "HTML5", "version": "0.1", "rules": {"p_closure": True}}
        am.save_specification(spec)
        loaded = am.load_specification()
        assert loaded["name"] == "HTML5"
        assert loaded["rules"]["p_closure"] is True

    def test_load_specification_missing_returns_empty(self, am):
        result = am.load_specification()
        assert result == {}

    def test_load_empty_yaml_file(self, am):
        """An empty YAML file should return {} rather than raise."""
        spec_file = am.spec_dir / "spec.yml"
        spec_file.write_text("")
        result = am.load_specification()
        assert result == {}


# ---------------------------------------------------------------------------
# ArtifactManager — save_patch
# ---------------------------------------------------------------------------

class TestArtifactManagerPatch:

    @pytest.fixture
    def am(self, tmp_path):
        return ArtifactManager("test_run", tmp_path / "test_run")

    def test_save_patch_creates_file(self, am):
        path = am.save_patch("--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new\n")
        assert path.exists()
        assert path.name == "code.patch"

    def test_save_patch_content_preserved(self, am):
        content = "--- a\n+++ b\n@@ -0,0 +1 @@\n+hello\n"
        path = am.save_patch(content, "my.patch")
        assert path.read_text() == content

    def test_save_patch_custom_name(self, am):
        path = am.save_patch("dummy", "repair_001.patch")
        assert path.name == "repair_001.patch"


# ---------------------------------------------------------------------------
# ArtifactManager — save_report
# ---------------------------------------------------------------------------

class TestArtifactManagerReport:

    @pytest.fixture
    def am(self, tmp_path):
        return ArtifactManager("test_run", tmp_path / "test_run")

    def test_save_report_creates_file(self, am):
        path = am.save_report({"status": "ok"})
        assert path.exists()

    def test_save_report_valid_json(self, am):
        data = {"passed": 10, "failed": 0, "errors": []}
        path = am.save_report(data)
        loaded = json.loads(path.read_text())
        assert loaded["passed"] == 10

    def test_save_report_custom_name(self, am):
        path = am.save_report({}, "custom_report.json")
        assert path.name == "custom_report.json"


# ---------------------------------------------------------------------------
# ArtifactManager — save_trace
# ---------------------------------------------------------------------------

class TestArtifactManagerTrace:

    @pytest.fixture
    def am(self, tmp_path):
        return ArtifactManager("test_run", tmp_path / "test_run")

    def test_save_trace_creates_file(self, am):
        trace = {"events": [{"t": 0.0, "agent": "SpecAgent", "action": "start"}]}
        path = am.save_trace(trace)
        assert path.exists()
        loaded = json.loads(path.read_text())
        assert loaded["events"][0]["agent"] == "SpecAgent"


# ---------------------------------------------------------------------------
# ArtifactManager — list_artifacts
# ---------------------------------------------------------------------------

class TestArtifactManagerList:

    @pytest.fixture
    def am(self, tmp_path):
        return ArtifactManager("test_run", tmp_path / "test_run")

    def test_list_empty(self, am):
        listing = am.list_artifacts()
        assert listing == {"specs": [], "patches": [], "reports": [], "traces": []}

    def test_list_after_saves(self, am):
        am.save_specification({"x": 1})
        am.save_patch("diff", "p.patch")
        am.save_report({"r": 2})
        listing = am.list_artifacts()
        assert "spec.yml" in listing["specs"]
        assert "p.patch" in listing["patches"]
        assert "report.json" in listing["reports"]


# ---------------------------------------------------------------------------
# PatchManager — create_patch
# ---------------------------------------------------------------------------

class TestPatchManager:

    def test_creates_unified_diff(self):
        old = "line1\nline2\nline3\n"
        new = "line1\nline2 modified\nline3\n"
        patch = PatchManager.create_patch(old, new, "test.py")
        assert "--- a/test.py" in patch
        assert "+++ b/test.py" in patch
        assert "+line2 modified" in patch
        assert "-line2" in patch

    def test_identical_files_empty_patch(self):
        content = "no changes here\n"
        patch = PatchManager.create_patch(content, content, "same.py")
        # Identical input → empty patch string
        assert patch == ""

    def test_add_lines(self):
        old = ""
        new = "new line\n"
        patch = PatchManager.create_patch(old, new, "added.py")
        assert "+new line" in patch

    def test_remove_lines(self):
        old = "remove me\n"
        new = ""
        patch = PatchManager.create_patch(old, new, "removed.py")
        assert "-remove me" in patch

    def test_custom_filename_in_patch(self):
        patch = PatchManager.create_patch("a\n", "b\n", "mymodule.py")
        assert "mymodule.py" in patch

    def test_returns_string(self):
        result = PatchManager.create_patch("x\n", "y\n")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# ReportGenerator — create_test_report
# ---------------------------------------------------------------------------

class TestReportGeneratorTestReport:

    def test_basic_schema(self):
        report = ReportGenerator.create_test_report(10, 2, ["err1"])
        assert "timestamp" in report
        assert report["summary"]["passed"] == 10
        assert report["summary"]["failed"] == 2
        assert report["summary"]["total"] == 12
        assert "err1" in report["errors"]

    def test_success_rate_calculation(self):
        report = ReportGenerator.create_test_report(8, 2, [])
        assert abs(report["summary"]["success_rate"] - 0.8) < 1e-9

    def test_zero_total_no_division_error(self):
        report = ReportGenerator.create_test_report(0, 0, [])
        assert report["summary"]["success_rate"] == 0

    def test_traces_empty_by_default(self):
        report = ReportGenerator.create_test_report(5, 0, [])
        assert report["traces"] == {}

    def test_traces_included_when_provided(self):
        traces = {"agent": "TestAgent", "duration": 1.23}
        report = ReportGenerator.create_test_report(5, 0, [], traces=traces)
        assert report["traces"]["agent"] == "TestAgent"

    def test_all_passing(self):
        report = ReportGenerator.create_test_report(139, 0, [])
        assert report["summary"]["success_rate"] == 1.0

    def test_all_failing(self):
        report = ReportGenerator.create_test_report(0, 5, ["e1", "e2"])
        assert report["summary"]["success_rate"] == 0.0
        assert len(report["errors"]) == 2


# ---------------------------------------------------------------------------
# ReportGenerator — create_repair_report
# ---------------------------------------------------------------------------

class TestReportGeneratorRepairReport:

    def _make_test_report(self, passed, failed):
        return ReportGenerator.create_test_report(passed, failed, [])

    def test_basic_schema(self):
        before = self._make_test_report(5, 5)
        after  = self._make_test_report(9, 1)
        report = ReportGenerator.create_repair_report("--- patch ---", before, after)
        assert "timestamp" in report
        assert "patch" in report
        assert "results" in report
        assert "before" in report["results"]
        assert "after" in report["results"]
        assert "improvement" in report["results"]

    def test_improvement_calculation(self):
        before = self._make_test_report(5, 5)   # success_rate = 0.5
        after  = self._make_test_report(9, 1)   # success_rate = 0.9
        report = ReportGenerator.create_repair_report("patch", before, after)
        assert abs(report["results"]["improvement"] - 0.4) < 1e-9

    def test_patch_truncated_at_500(self):
        long_patch = "x" * 600
        report = ReportGenerator.create_repair_report(long_patch,
                     self._make_test_report(1, 0),
                     self._make_test_report(1, 0))
        assert len(report["patch"]) == 500

    def test_negative_improvement_allowed(self):
        """Repair can sometimes make things worse — must not crash."""
        before = self._make_test_report(9, 1)   # 0.9
        after  = self._make_test_report(5, 5)   # 0.5
        report = ReportGenerator.create_repair_report("bad patch", before, after)
        assert report["results"]["improvement"] < 0
