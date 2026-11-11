"""Measure all project Python, including TP1 subprocesses; enforce separate gates."""

import json
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[1]


def production_files(root: Path) -> set[str]:
    """Inventory executable source, excluding only tests and generated/vendor dirs."""
    paths = set()
    skipped = {".git", ".venv", ".local", "node_modules", "__pycache__", "tests"}
    for directory, folders, files in os.walk(root):
        folders[:] = [name for name in folders if name not in skipped]
        for name in files:
            path = (Path(directory) / name).relative_to(root).as_posix()
            if name.endswith(".py") and path != "mcp-server/test_server.py":
                paths.add(path)
    return paths


def check_report(report: dict[str, Any], expected_files: set[str]) -> list[str]:
    files = {name.replace("\\", "/"): data for name, data in report["files"].items()}
    problems = []
    missing = expected_files - set(files)
    if missing:
        problems.append("Missing production files: " + ", ".join(sorted(missing)))
    if not report["meta"]["branch_coverage"]:
        problems.append("Branch measurement is absent.")
    totals = report["totals"]
    if not totals["num_statements"]:
        problems.append("No executable Python measured.")
    elif totals["covered_lines"] * 100 < totals["num_statements"] * 80:
        problems.append("Global line coverage is below 80%.")
    services = [
        data["summary"] for path, data in files.items()
        if path.startswith("src/services/")
    ]
    statements = sum(data["num_statements"] for data in services)
    covered = sum(data["covered_lines"] for data in services)
    branches = sum(data["num_branches"] for data in services)
    covered_branches = sum(data["covered_branches"] for data in services)
    if not statements or not branches:
        problems.append("No executable service lines/branches measured.")
    elif covered != statements or covered_branches != branches:
        problems.append("Service lines and branches must each reach 100%.")
    server = files.get("mcp-server/server.py", {}).get("summary", {})
    if not server.get("covered_lines", 0):
        problems.append("No executed TP1 server lines measured.")
    print(
        f"Global lines: {totals['covered_lines']}/{totals['num_statements']}; "
        f"branches: {totals['covered_branches']}/{totals['num_branches']}"
    )
    print(
        f"Services: lines {covered}/{statements}; "
        f"branches {covered_branches}/{branches}"
    )
    return problems


def measure(root: Path, postgresql: bool = False) -> Path:
    """Keep each run separate so old successful data cannot mask a failed run."""
    output = root / ".local" / "coverage" / uuid4().hex
    output.mkdir(parents=True)
    environment = os.environ.copy()
    environment["COVERAGE_FILE"] = str(output / ".coverage")
    environment["COVERAGE_RCFILE"] = str(root / ".coveragerc")
    pytest_arguments = ["run", "-m", "pytest", "tests", "-q"]
    if postgresql:
        pytest_arguments += [
            "--ds=tests.settings_postgres", "--reuse-db", "-k",
            "not test_guard_refuses_unmarked_or_wrong_database",
        ]
    commands = [
        pytest_arguments,
        [
            "run", "-m", "unittest", "discover", "-s", "mcp-server",
            "-p", "test_*.py", "-v",
        ],
        ["combine", "--keep"],
        ["report"],
        ["json", "-o", str(output / "coverage.json")],
    ]
    for arguments in commands:
        subprocess.run(
            [sys.executable, "-m", "coverage", *arguments],
            cwd=root, env=environment, check=True,
        )
    return output / "coverage.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgresql", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        print("Coverage database: PostgreSQL" if arguments.postgresql else "Coverage database: SQLite")
        report_path = measure(BASE_DIR, postgresql=arguments.postgresql)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        problems = check_report(report, production_files(BASE_DIR))
        print(f"Coverage report: {report_path}")
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    except (subprocess.CalledProcessError, OSError, ValueError, KeyError) as error:
        print(f"Coverage check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
