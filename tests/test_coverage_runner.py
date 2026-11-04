"""Gate failures must propagate; synthetic fixtures never replace measured reports."""

import copy
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from tools import check_coverage


def example_report() -> dict:
    return {
        "meta": {"branch_coverage": True},
        "totals": {"num_statements": 100, "covered_lines": 80,
                   "num_branches": 10, "covered_branches": 9},
        "files": {
            "src/services/access.py": {"summary": {
                "num_statements": 10, "covered_lines": 10,
                "num_branches": 2, "covered_branches": 2}},
            "mcp-server/server.py": {"summary": {"covered_lines": 50}},
        },
    }


def test_exact_threshold_and_missing_source() -> None:
    report = example_report()
    assert check_coverage.check_report(report, set(report["files"])) == []
    assert check_coverage.check_report(report, {"missing.py"})


@pytest.mark.parametrize("failure", [
    "global", "service-lines", "service-branches", "no-services",
    "no-server", "no-branches", "no-lines",
])
def test_gate_refuses_bad_measurements(failure: str) -> None:
    report = copy.deepcopy(example_report())
    if failure == "global":
        report["totals"]["covered_lines"] = 79
    elif failure.startswith("service-"):
        key = "covered_lines" if failure == "service-lines" else "covered_branches"
        report["files"]["src/services/access.py"]["summary"][key] -= 1
    elif failure == "no-services":
        del report["files"]["src/services/access.py"]
    elif failure == "no-server":
        report["files"]["mcp-server/server.py"]["summary"]["covered_lines"] = 0
    elif failure == "no-branches":
        report["meta"]["branch_coverage"] = False
    else:
        report["totals"]["num_statements"] = 0
    assert check_coverage.check_report(report, set())


def test_inventory_includes_migrations_helpers_and_server(tmp_path: Path) -> None:
    for name in ("manage.py", "src/data/migrations/0001.py", "tools/task.py",
                 "mcp-server/server.py", "mcp-server/test_server.py",
                 "tests/test_example.py", ".venv/lib/third_party.py"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    assert check_coverage.production_files(tmp_path) == {
        "manage.py", "src/data/migrations/0001.py", "tools/task.py",
        "mcp-server/server.py",
    }


def test_measure_stops_on_test_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = Mock(side_effect=subprocess.CalledProcessError(1, ["test-command"]))
    monkeypatch.setattr(check_coverage.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        check_coverage.measure(tmp_path)
    assert run.call_count == 1


@pytest.mark.parametrize("case", ["pass", "gate", "test", "report"])
def test_main_exit_status_is_honest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    monkeypatch.setattr(check_coverage, "BASE_DIR", tmp_path)
    report = example_report()
    if case == "gate":
        report["totals"]["covered_lines"] = 79
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    calls = []

    def run(command: list[str], **kwargs: object) -> None:
        calls.append(command)
        if case == "test":
            raise subprocess.CalledProcessError(1, command)
        if "json" in command:
            target = Path(command[-1])
            target.write_text("invalid" if case == "report" else json.dumps(report))

    monkeypatch.setattr(check_coverage.subprocess, "run", run)
    result = check_coverage.main()
    assert result == (0 if case == "pass" else 1)
    if case != "test":
        assert any("combine" in command for command in calls)
        assert any("unittest" in command for command in calls)
