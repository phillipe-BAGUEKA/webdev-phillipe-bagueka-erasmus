"""Guarded, reversible manipulation of one fictitious demonstration laboratory."""

import json
import os
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import transaction

from .demo import DEMO_LABS, require_demo_database
from .labs import list_laboratories
from .models import Laboratory


def snapshot_path(path: Path) -> Path:
    """Keep snapshots beside the known demo database, outside tracked sources."""
    resolved = path.resolve()
    directory = Path(settings.DEMO_DATABASE_PATH).resolve().parent
    if resolved.parent != directory or resolved.suffix != ".json":
        raise ValueError("The snapshot must be a JSON file in the demo directory.")
    return resolved


def read_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(snapshot_path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"version", "database", "lab"}:
        raise ValueError("Invalid snapshot structure.")
    lab = payload["lab"]
    if (
        payload["version"] != 1
        or payload["database"] != str(Path(settings.DEMO_DATABASE_PATH).resolve())
        or not isinstance(lab, dict)
        or set(lab) != {"id", "name"}
        or type(lab["id"]) is not int
        or lab["id"] not in DEMO_LABS
        or lab["name"] != DEMO_LABS[lab["id"]]
    ):
        raise ValueError("Snapshot does not match this demo database/laboratory.")
    return lab


def check_demo_target() -> None:
    require_demo_database()
    fields = {field.name for field in Laboratory._meta.local_fields}
    if fields != {"id", "name"} or Laboratory._meta.related_objects:
        raise ValueError("The model changed; review the demo procedure first.")


def inspect_laboratories() -> list[dict[str, int | str]]:
    check_demo_target()
    return list_laboratories()


def backup_laboratory(lab_id: int, path: Path) -> None:
    """Write an exclusive, durable snapshot before any removal can be requested."""
    check_demo_target()
    lab = Laboratory.objects.filter(pk=lab_id).values("id", "name").first()
    if lab is None or lab["name"] != DEMO_LABS.get(lab_id):
        raise ValueError("Expected fictitious demonstration laboratory not found.")
    payload = {
        "version": 1,
        "database": str(Path(settings.DEMO_DATABASE_PATH).resolve()),
        "lab": lab,
    }
    with snapshot_path(path).open("x", encoding="utf-8") as snapshot:
        json.dump(payload, snapshot, ensure_ascii=False, indent=2)
        snapshot.flush()
        os.fsync(snapshot.fileno())


@transaction.atomic
def withdraw_laboratory(path: Path) -> None:
    check_demo_target()
    saved = read_snapshot(path)
    lab = Laboratory.objects.filter(pk=saved["id"]).first()
    if lab is None or lab.name != saved["name"]:
        raise ValueError("Laboratory missing or changed; no removal performed.")
    lab.delete()


@transaction.atomic
def restore_laboratory(path: Path) -> bool:
    """Restore the same fields/id; a divergent existing row is never overwritten."""
    check_demo_target()
    saved = read_snapshot(path)
    existing = Laboratory.objects.filter(pk=saved["id"]).first()
    if existing is not None:
        if existing.name != saved["name"]:
            raise ValueError("Conflicting laboratory; restoration refused.")
        return False
    Laboratory.objects.create(**saved)
    return True
