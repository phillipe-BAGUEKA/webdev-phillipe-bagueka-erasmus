"""Database reads and writes for the staff catalogue."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TypedDict

from django.db import IntegrityError, transaction

from .models import Laboratory, Workstation


class NamedEntity(TypedDict):
    id: int
    name: str


class CatalogueLaboratory(NamedEntity):
    workstations: list[NamedEntity]


class NamedWorkstation(NamedEntity):
    laboratory_id: int


class WorkstationNameConflict(Exception):
    """The database rejected a repeated workstation name in one laboratory."""


def list_catalogue() -> list[CatalogueLaboratory]:
    """Read the ordered laboratory tree, including empty laboratories."""
    rows = Laboratory.objects.order_by("id", "workstation__id").values_list(
        "id", "name", "workstation__id", "workstation__name",
    )
    laboratories: dict[int, CatalogueLaboratory] = {}
    for row in rows:
        laboratory_id, laboratory_name, workstation_id, workstation_name = row
        laboratory = laboratories.setdefault(laboratory_id, {
            "id": laboratory_id, "name": laboratory_name, "workstations": [],
        })
        if workstation_id is not None:
            laboratory["workstations"].append({
                "id": workstation_id, "name": workstation_name,
            })
    return list(laboratories.values())


def create_laboratory(name: str) -> NamedEntity:
    laboratory = Laboratory.objects.create(name=name)
    return {"id": laboratory.pk, "name": laboratory.name}


def rename_laboratory(laboratory_id: int, name: str) -> NamedEntity | None:
    changed = Laboratory.objects.filter(pk=laboratory_id).update(name=name)
    if not changed:
        return None
    return {"id": laboratory_id, "name": name}


@contextmanager
def _workstation_write() -> Iterator[None]:
    try:
        with transaction.atomic():
            yield
    except IntegrityError as error:
        cause = error.__cause__
        diagnostic = getattr(cause, "diag", None)
        name = getattr(diagnostic, "constraint_name", None)
        sqlstate = getattr(cause, "sqlstate", None)
        if name == "workstation_name_in_lab" and sqlstate == "23505":
            raise WorkstationNameConflict from error
        raise


def create_workstation(
    laboratory_id: int, name: str,
) -> NamedWorkstation | None:
    """Keep the verified parent present until insertion completes."""
    with _workstation_write():
        laboratories = Laboratory.objects.select_for_update()
        if not laboratories.filter(pk=laboratory_id).exists():
            return None
        workstation = Workstation.objects.create(
            laboratory_id=laboratory_id, name=name,
        )
        return {
            "id": workstation.pk,
            "name": workstation.name,
            "laboratory_id": laboratory_id,
        }


def rename_workstation(
    laboratory_id: int, workstation_id: int, name: str,
) -> NamedWorkstation | None:
    """Update only the name of a workstation in the specified laboratory."""
    with _workstation_write():
        changed = Workstation.objects.filter(
            pk=workstation_id, laboratory_id=laboratory_id,
        ).update(name=name)
        if not changed:
            return None
        return {
            "id": workstation_id,
            "name": name,
            "laboratory_id": laboratory_id,
        }
