"""AC-48 reversible demo procedure on isolated database rows and temporary files."""

import io
import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from pytest_django.fixtures import Settings

from src.data import demo_labs
from src.data.demo import DEMO_LABS, seed_demo_data
from src.data.models import Laboratory, User


@pytest.fixture(autouse=True, params=["AC-48-demo"], ids=str)
def criterion_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def demo_snapshot(
    db: None, tmp_path: Path, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> Path:
    # Exercise the historical snapshot logic independently of its SQLite-only guard.
    # The new relation guard is tested separately: real 1B use must stay refused.
    settings.DEMO_DATABASE_PATH = tmp_path / "demo.sqlite3"
    monkeypatch.setattr(demo_labs, "check_demo_target", lambda: None)
    seed_demo_data()
    return tmp_path / "demo-lab-2.json"


def test_backup_withdraw_restore_preserves_accounts_and_other_rows(
    demo_snapshot: Path,
) -> None:
    before_users = list(User.objects.values())
    original = list(Laboratory.objects.values("id", "name"))
    output = io.StringIO()
    call_command("demo_labs", "list", stdout=output)
    assert "Disposable demo:" in output.getvalue()
    call_command("demo_labs", "backup", "--id", "2", "--snapshot", str(demo_snapshot))
    assert list(Laboratory.objects.values("id", "name")) == original
    assert json.loads(demo_snapshot.read_text())['lab'] == {
        "id": 2, "name": DEMO_LABS[2]
    }
    call_command("demo_labs", "withdraw", "--snapshot", str(demo_snapshot))
    assert list(Laboratory.objects.values_list("id", flat=True)) == [1, 3]
    assert demo_snapshot.exists()
    call_command("demo_labs", "restore", "--snapshot", str(demo_snapshot))
    call_command("demo_labs", "restore", "--snapshot", str(demo_snapshot))
    assert list(Laboratory.objects.values("id", "name")) == original
    assert list(User.objects.values()) == before_users


def test_missing_or_existing_backup_never_removes_data(demo_snapshot: Path) -> None:
    with pytest.raises(CommandError):
        call_command("demo_labs", "withdraw", "--snapshot", str(demo_snapshot))
    demo_labs.backup_laboratory(2, demo_snapshot)
    with pytest.raises(FileExistsError):
        demo_labs.backup_laboratory(2, demo_snapshot)
    assert Laboratory.objects.count() == 3


@pytest.mark.parametrize(
    "case", ["invalid-json", "wrong-db", "wrong-name", "bad-shape"]
)
def test_invalid_snapshot_refused_before_modification(
    demo_snapshot: Path, case: str
) -> None:
    demo_labs.backup_laboratory(2, demo_snapshot)
    payload = json.loads(demo_snapshot.read_text())
    if case == "wrong-db":
        payload["database"] = "another-database"
    elif case == "wrong-name":
        payload["lab"]["name"] = "Modified"
    elif case == "bad-shape":
        payload = []
    content = "not-json" if case == "invalid-json" else json.dumps(payload)
    demo_snapshot.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        demo_labs.withdraw_laboratory(demo_snapshot)
    assert Laboratory.objects.count() == 3


def test_changed_row_or_restore_conflict_is_preserved(demo_snapshot: Path) -> None:
    demo_labs.backup_laboratory(2, demo_snapshot)
    Laboratory.objects.filter(pk=2).update(name="Changed data to preserve")
    with pytest.raises(ValueError, match="changed"):
        demo_labs.withdraw_laboratory(demo_snapshot)
    with pytest.raises(ValueError, match="Conflicting"):
        demo_labs.restore_laboratory(demo_snapshot)
    assert Laboratory.objects.get(pk=2).name == "Changed data to preserve"


def test_non_demo_lab_and_outside_path_are_refused(demo_snapshot: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        demo_labs.backup_laboratory(99, demo_snapshot)
    with pytest.raises(ValueError, match="JSON file"):
        demo_labs.backup_laboratory(2, demo_snapshot.parent.parent / "outside.json")
    assert Laboratory.objects.count() == 3


@pytest.mark.django_db
def test_command_refuses_real_guard_before_any_operation() -> None:
    with pytest.raises(CommandError, match="other than"):
        call_command("demo_labs", "list")
    assert User.objects.count() == Laboratory.objects.count() == 0


@pytest.mark.django_db
def test_original_demo_procedure_refuses_new_relations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(demo_labs, "require_demo_database", lambda: None)
    with pytest.raises(ValueError, match="model changed"):
        demo_labs.check_demo_target()
    assert User.objects.count() == Laboratory.objects.count() == 0
