"""Exercise idempotence, refusal and masked-input behavior on isolated data."""

import getpass
import io
import warnings
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from pytest_django.fixtures import Settings

from src.data.demo import (
    DEMO_EMAILS,
    DEMO_LABS,
    DEMO_MARKER,
    require_demo_database,
    seed_demo_data,
)
from src.data.management.commands import seed_demo
from src.data.models import Laboratory, User
from tools.init_local import prepare_local_state


@pytest.mark.django_db
@pytest.mark.parametrize("criterion", ["AC-47-AC-48-seed"], ids=str)
def test_seed_is_idempotent_and_preserves_passwords(
    criterion: str, generated_password: str
) -> None:
    new_users, new_labs = seed_demo_data()
    assert len(new_users) == 2 and new_labs == 3
    assert all(not user.has_usable_password() for user in new_users)
    new_users[0].set_password(generated_password)
    new_users[0].save(update_fields=["password"])
    original_hash = new_users[0].password
    assert seed_demo_data() == ([], 0)
    assert User.objects.count() == 2
    assert list(Laboratory.objects.values_list("id", "name")) == list(DEMO_LABS.items())
    new_users[0].refresh_from_db()
    assert new_users[0].password == original_hash
    assert new_users[0].check_password(generated_password)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field,value",
    [
        ("role", User.Role.PERSONNEL),
        ("is_staff", True),
        ("is_superuser", True),
        ("is_active", False),
    ],
)
def test_seed_refuses_changed_account_without_writing(
    field: str, value: object
) -> None:
    user = User.objects.create_user(DEMO_EMAILS[0], **{field: value})
    with pytest.raises(ValueError, match="differs"):
        seed_demo_data()
    user.refresh_from_db()
    assert getattr(user, field) == value
    assert User.objects.count() == 1
    assert Laboratory.objects.count() == 0


@pytest.mark.django_db
def test_seed_refuses_lab_conflict_without_partial_creation() -> None:
    Laboratory.objects.create(pk=3, name="Existing data to preserve")
    with pytest.raises(ValueError, match="Laboratory 3 differs"):
        seed_demo_data()
    assert list(Laboratory.objects.values_list("name", flat=True)) == [
        "Existing data to preserve"
    ]
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_guard_refuses_unmarked_or_wrong_database(
    tmp_path: Path, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    demo_path = tmp_path / "demo.sqlite3"
    demo_path.touch()
    settings.DEMO_DATABASE_PATH = demo_path
    settings.DEMO_MARKER_PATH = tmp_path / "demo.marker"
    with pytest.raises(ValueError, match="other than"):
        require_demo_database()
    monkeypatch.setitem(connection.settings_dict, "NAME", demo_path)
    with pytest.raises(ValueError, match="marker"):
        require_demo_database()
    settings.DEMO_MARKER_PATH.write_text("wrong", encoding="utf-8")
    with pytest.raises(ValueError, match="marker"):
        require_demo_database()
    settings.DEMO_MARKER_PATH.write_text(DEMO_MARKER, encoding="utf-8")
    require_demo_database()


@pytest.mark.django_db
def test_command_no_input_and_rerun_never_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(seed_demo, "require_demo_database", lambda: None)
    prompt = Mock(side_effect=AssertionError("Unexpected password prompt"))
    monkeypatch.setattr(seed_demo.getpass, "getpass", prompt)
    output = io.StringIO()
    call_command("seed_demo", no_input=True, stdout=output)
    call_command("seed_demo", no_input=True, stdout=output)
    assert "Created: 0 accounts, 0 laboratories" in output.getvalue()
    assert User.objects.count() == 2
    assert all(not user.has_usable_password() for user in User.objects.all())
    prompt.assert_not_called()


@pytest.mark.django_db
def test_command_refuses_unmarked_database_before_writes() -> None:
    with pytest.raises(CommandError, match="other than"):
        call_command("seed_demo", no_input=True)
    assert User.objects.count() == 0 and Laboratory.objects.count() == 0


@pytest.mark.django_db
def test_command_refuses_noninteractive_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(seed_demo, "require_demo_database", lambda: None)
    monkeypatch.setattr(seed_demo.sys.stdin, "isatty", lambda: False)
    with pytest.raises(CommandError, match="real terminal"):
        call_command("seed_demo")
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_interactive_password_is_hashed_without_output(
    monkeypatch: pytest.MonkeyPatch, generated_password: str
) -> None:
    monkeypatch.setattr(seed_demo, "require_demo_database", lambda: None)
    monkeypatch.setattr(seed_demo.sys.stdin, "isatty", lambda: True)
    prompt = Mock(return_value=generated_password)
    monkeypatch.setattr(seed_demo.getpass, "getpass", prompt)
    output = io.StringIO()
    call_command("seed_demo", stdout=output)
    assert prompt.call_count == 4
    assert all(user.check_password(generated_password) for user in User.objects.all())
    assert generated_password not in output.getvalue()
    prompt.reset_mock()
    call_command("seed_demo", stdout=output)
    prompt.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("failure", ["mismatch", "weak", "interrupt", "echo_warning"])
def test_interrupted_or_invalid_password_keeps_account_unusable(
    failure: str, monkeypatch: pytest.MonkeyPatch, generated_password: str
) -> None:
    user = User.objects.create_user(DEMO_EMAILS[0])

    def warn_instead_of_echo(prompt: str) -> str:
        warnings.warn("Cannot hide input", getpass.GetPassWarning)
        raise AssertionError("Visible input must never be reached")

    if failure == "echo_warning":
        monkeypatch.setattr(seed_demo.getpass, "getpass", warn_instead_of_echo)
        expected_error = getpass.GetPassWarning
    elif failure == "interrupt":
        monkeypatch.setattr(
            seed_demo.getpass, "getpass", Mock(side_effect=KeyboardInterrupt)
        )
        expected_error = KeyboardInterrupt
    else:
        values = [generated_password, generated_password + "different"]
        if failure == "weak":
            values = ["", ""]
        monkeypatch.setattr(seed_demo.getpass, "getpass", Mock(side_effect=values))
        expected_error = CommandError
    with pytest.raises(expected_error):
        seed_demo.choose_password(user)
    user.refresh_from_db()
    assert not user.has_usable_password()


def test_local_initialization_preserves_existing_key_without_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare_local_state(tmp_path)
    secret_path = tmp_path / ".local" / "django-dev-key"
    initial_stat = secret_path.stat()
    monkeypatch.setattr(
        "tools.init_local.secrets.token_urlsafe",
        Mock(side_effect=AssertionError("Key must not be replaced")),
    )
    prepare_local_state(tmp_path)
    assert secret_path.stat().st_mtime_ns == initial_stat.st_mtime_ns
    assert (tmp_path / "data" / "demo.marker").read_text(
        encoding="utf-8"
    ) == DEMO_MARKER


def test_local_initialization_refuses_existing_unmarked_database(
    tmp_path: Path,
) -> None:
    (tmp_path / "data").mkdir()
    database_path = tmp_path / "data" / "demo.sqlite3"
    database_path.touch()
    with pytest.raises(RuntimeError, match="unmarked"):
        prepare_local_state(tmp_path)
    assert not (tmp_path / "data" / "demo.marker").exists()
    assert not (tmp_path / ".local").exists()
