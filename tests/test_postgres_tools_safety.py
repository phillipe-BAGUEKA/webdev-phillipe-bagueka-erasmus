"""Exercise lifecycle/provisioning contracts with synthetic state, never real DDL."""

import importlib
import json
from pathlib import Path
import sys
from unittest.mock import MagicMock, Mock

import pytest

from tools import local_postgres, setup_postgres


@pytest.mark.parametrize("valid", [True, False])
def test_connection_identity_is_checked_before_return(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, valid: bool,
) -> None:
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"user": "synthetic", "password": "synthetic"}))
    monkeypatch.setattr(local_postgres, "PROFILE", profile)
    monkeypatch.setattr(local_postgres, "DATA", tmp_path / "expected")
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (
        str(tmp_path / ("expected" if valid else "wrong")), "lab_booking_1a", "5433"
    )
    monkeypatch.setattr(local_postgres.psycopg, "connect", Mock(return_value=connection))
    if valid:
        assert local_postgres.connect() is connection
        connection.close.assert_not_called()
    else:
        with pytest.raises(RuntimeError, match="identity"):
            local_postgres.connect()
        connection.close.assert_called_once()


def test_fresh_provisioning_has_minimal_roles_and_private_distinct_profiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(setup_postgres, "ROOT", tmp_path)
    connection = MagicMock()
    connection.__enter__.return_value = connection
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.side_effect = [
        ("5433", "lab_booking_1a", str(setup_postgres.EXPECTED_DATA)),
        None, None, None, None,
    ]
    setup_postgres.provision(connection)
    profiles = [json.loads((tmp_path / ".local" / f"postgres-1a-{k}.json").read_text())
                for k in ("dev", "test")]
    assert profiles[0]["password"] != profiles[1]["password"]
    assert profiles[0]["django_key"] != profiles[1]["django_key"]
    statements = [call.args[0].as_string() for call in cursor.execute.call_args_list
                  if not isinstance(call.args[0], str)]
    assert len(statements) == 6
    assert sum("CREATE DATABASE" in statement for statement in statements) == 2
    assert sum("REVOKE ALL" in statement for statement in statements) == 2
    for statement in statements:
        if "CREATE ROLE" in statement:
            assert all(flag in statement for flag in (
                "NOSUPERUSER", "NOCREATEDB", "NOCREATEROLE", "NOBYPASSRLS"
            ))
    output = capsys.readouterr()
    assert all(p["password"] not in output.out + output.err for p in profiles)


@pytest.mark.parametrize("action", ["init", "provision", "start", "stop", "status", "verify"])
def test_cli_dispatch_uses_only_dedicated_helpers(
    monkeypatch: pytest.MonkeyPatch, action: str,
) -> None:
    monkeypatch.setattr(sys, "argv", ["local_postgres.py", action])
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value.fetchone.return_value = ("test",)
    connect = Mock(return_value=connection)
    init, start, provision, run = Mock(), Mock(), Mock(), Mock()
    monkeypatch.setattr(local_postgres, "connect", connect)
    monkeypatch.setattr(local_postgres, "initialize", init)
    monkeypatch.setattr(local_postgres, "start", start)
    monkeypatch.setattr(local_postgres, "provision", provision)
    monkeypatch.setattr(local_postgres, "run_pg", run)
    assert local_postgres.main() == 0
    if action == "init":
        init.assert_called_once()
        connect.assert_not_called()
    elif action == "start":
        start.assert_called_once()
        connect.assert_not_called()
    elif action == "provision":
        provision.assert_called_once_with(connection)
    elif action == "stop":
        assert str(local_postgres.DATA) in run.call_args.args
        assert "stop" in run.call_args.args
    else:
        connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT version()"
        )


def test_cli_failure_never_echoes_exception_contents(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(sys, "argv", ["local_postgres.py", "verify"])
    monkeypatch.setattr(local_postgres, "connect", Mock(side_effect=RuntimeError("synthetic-secret")))
    assert local_postgres.main() == 1
    assert "synthetic-secret" not in capsys.readouterr().err


@pytest.mark.parametrize("module,kind", [
    ("src.config.postgres", "dev"), ("tests.settings_postgres", "test")
])
def test_settings_select_explicit_postgres_profiles_without_sqlite_secret(
    monkeypatch: pytest.MonkeyPatch, module: str, kind: str,
) -> None:
    from src.config import postgres_config

    loader = Mock(return_value={
        "name": "synthetic-db", "user": "synthetic-role",
        "password": "synthetic", "django_key": "synthetic-key",
    })
    monkeypatch.setattr(postgres_config, "load_profile", loader)
    monkeypatch.delitem(sys.modules, module, raising=False)
    settings = importlib.import_module(module)
    loader.assert_called_once_with(kind)
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert settings.DATABASES["default"]["PORT"] == "5433"
    if kind == "test":
        assert settings.DATABASES["default"]["TEST"]["NAME"] == "test_lab_booking_1a"
    else:
        assert settings.SECRET_KEY == "synthetic-key"
    # Do not leave a synthetic settings module cached for other tests.
    sys.modules.pop(module, None)
