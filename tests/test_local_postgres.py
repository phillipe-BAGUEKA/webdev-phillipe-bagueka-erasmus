"""Cluster lifecycle safety on synthetic paths; never initialize a real server."""

from pathlib import Path
import subprocess
from unittest.mock import Mock

import pytest

from tools import local_postgres


def test_existing_cluster_is_never_reinitialized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(local_postgres, "DATA", tmp_path)
    with pytest.raises(RuntimeError, match="existing"):
        local_postgres.initialize()


def test_pg_ctl_does_not_capture_inherited_background_pipes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = Mock()
    monkeypatch.setattr(local_postgres.subprocess, "run", run)
    local_postgres.run_pg("pg_ctl.exe", "status")
    assert run.call_args.kwargs["stdout"] == subprocess.DEVNULL
    assert run.call_args.kwargs["stderr"] == subprocess.DEVNULL
    assert "capture_output" not in run.call_args.kwargs


def test_initdb_failure_removes_only_its_temporary_password_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "local"
    monkeypatch.setattr(local_postgres, "DATA", tmp_path / "new-cluster")
    monkeypatch.setattr(local_postgres, "PROFILE", directory / "bootstrap.json")
    monkeypatch.setattr(local_postgres, "ROOT", tmp_path)
    monkeypatch.setattr(local_postgres, "PORT", 0)
    monkeypatch.setattr(local_postgres.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(local_postgres.getpass, "getpass", lambda prompt: "synthetic")
    run = Mock(side_effect=RuntimeError("Synthetic initialization failure"))
    monkeypatch.setattr(local_postgres, "run_pg", run)
    with pytest.raises(RuntimeError, match="Synthetic"):
        local_postgres.initialize()
    assert not list(directory.glob("lab-booking-initdb-*"))
    assert (directory / "bootstrap.json").exists()
    assert "synthetic" not in repr(run.call_args)
