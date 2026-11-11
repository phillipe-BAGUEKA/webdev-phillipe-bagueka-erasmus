"""Profile safety checks with synthetic credentials; no local secret is opened."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from django.core.exceptions import ImproperlyConfigured

from src.config.postgres_config import database_settings, load_profile
from tools import setup_postgres


def test_native_permissions_on_new_empty_profile(tmp_path: Path) -> None:
    profile = tmp_path / "empty-profile.json"
    profile.touch()
    setup_postgres.restrict_profile_permissions(profile)
    assert profile.read_bytes() == b""
    if setup_postgres.sys.platform == "win32":
        acl = setup_postgres.subprocess.check_output(
            ["icacls", str(profile)], text=True,
        )
        assert "(I)" not in acl


@pytest.mark.parametrize("existing", ["role", "database"])
def test_existing_postgres_object_aborts_before_ddl_or_profiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing: str,
) -> None:
    monkeypatch.setattr(setup_postgres, "ROOT", tmp_path)
    monkeypatch.setattr(setup_postgres.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: "synthetic-admin")
    monkeypatch.setattr(setup_postgres.getpass, "getpass", lambda prompt: "synthetic")
    connection = MagicMock()
    cursor = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    identity = ("5433", "lab_booking_1a", str(setup_postgres.EXPECTED_DATA))
    cursor.fetchone.side_effect = (
        [identity, (1,)] if existing == "role" else [identity, None, (1,)]
    )
    monkeypatch.setattr(setup_postgres.psycopg, "connect", Mock(return_value=connection))
    with pytest.raises(RuntimeError, match="already exists"):
        setup_postgres.provision()
    assert not (tmp_path / ".local").exists()
    assert all(call.args[0].startswith("SELECT") for call in cursor.execute.call_args_list)


def test_same_named_cluster_in_other_directory_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(setup_postgres, "ROOT", tmp_path)
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = ("5433", "lab_booking_1a", str(tmp_path / "other"))
    with pytest.raises(RuntimeError, match="identity"):
        setup_postgres.provision(connection)
    assert not (tmp_path / ".local").exists()
    assert cursor.execute.call_count == 1


def test_windows_profile_acl_is_applied_before_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(setup_postgres.sys, "platform", "win32")
    monkeypatch.setattr(
        setup_postgres.subprocess, "check_output",
        Mock(return_value='"synthetic-user","S-1-5-21-123"\n'),
    )
    command = Mock()
    monkeypatch.setattr(setup_postgres.subprocess, "run", command)
    profile = tmp_path / "empty-profile.json"
    profile.touch()
    setup_postgres.restrict_profile_permissions(profile)
    assert profile.read_bytes() == b""
    command.assert_called_once_with(
        ["icacls", str(profile), "/inheritance:r", "/grant:r",
         "*S-1-5-21-123:(F)"], check=True, capture_output=True,
    )


@pytest.mark.parametrize(
    "kind,name", [("dev", "lab_booking_1a"), ("test", "test_lab_booking_1a")]
)
def test_profile_has_separate_database_and_role(
    tmp_path: Path, kind: str, name: str,
) -> None:
    profile = {
        "name": name, "user": f"lab_booking_1a_{kind}",
        "password": "synthetic-password", "django_key": "synthetic-key",
    }
    path = tmp_path / f"postgres-1a-{kind}.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    database = database_settings(load_profile(kind, tmp_path))
    assert database["ENGINE"] == "django.db.backends.postgresql"
    assert database["PORT"] == "5433"
    assert database["NAME"] == name
    assert database["USER"] == profile["user"]
    assert database["OPTIONS"]["passfile"] == ""
    profile["name"] = "data/demo.sqlite3"
    path.write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(ImproperlyConfigured):
        load_profile(kind, tmp_path)


@pytest.mark.parametrize("content", [None, "not-json", "[]", "{}"])
def test_missing_or_invalid_profile_fails_closed(
    tmp_path: Path, content: str | None,
) -> None:
    if content is not None:
        (tmp_path / "postgres-1a-test.json").write_text(content, encoding="utf-8")
    with pytest.raises(ImproperlyConfigured):
        load_profile("test", tmp_path)


def test_unknown_profile_cannot_select_arbitrary_file(tmp_path: Path) -> None:
    with pytest.raises(ImproperlyConfigured):
        load_profile("../other", tmp_path)


def test_provisioning_refuses_noninteractive_password_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(setup_postgres.sys.stdin, "isatty", lambda: False)
    with pytest.raises(RuntimeError, match="interactive"):
        setup_postgres.provision()


def test_existing_profile_is_not_read_or_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(setup_postgres, "ROOT", tmp_path)
    monkeypatch.setattr(setup_postgres.sys.stdin, "isatty", lambda: True)
    directory = tmp_path / ".local"
    directory.mkdir()
    profile = directory / "postgres-1a-dev.json"
    profile.write_text("synthetic-existing-data", encoding="utf-8")
    with pytest.raises(RuntimeError, match="already exists"):
        setup_postgres.provision()
    assert profile.read_text(encoding="utf-8") == "synthetic-existing-data"


@pytest.mark.django_db
def test_postgresql_identity_and_existing_schema() -> None:
    from django.db import connection

    if connection.vendor != "postgresql":
        pytest.skip("Use tests.settings_postgres for live PostgreSQL proof.")
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        assert cursor.fetchone() == ("test_lab_booking_1a", "lab_booking_1a_test")
    tables = connection.introspection.table_names()
    assert {"data_user", "data_laboratory", "django_session"}.issubset(tables)
    assert "data_booking" in tables
    assert "data_workstation" in tables
