"""Business rules shared by the staff catalogue's transport adapters."""

from src.data import staff_catalogue as data

from .access import Actor, require_staff_actor
from .booking_creation import WorkstationNotFound
from .booking_reads import LaboratoryNotFound


class InvalidCatalogueName(ValueError):
    """A catalogue name must fit the database name field."""


class DuplicateWorkstationName(ValueError):
    """A workstation already uses this name in the requested laboratory."""


class InvalidWorkstationState(ValueError):
    """The requested operational state must be a boolean."""


def _validated_name(value: object) -> str:
    if type(value) is not str:
        raise InvalidCatalogueName
    name = value.strip()
    if not 1 <= len(name) <= 150 or "\0" in name:
        raise InvalidCatalogueName
    try:
        name.encode("utf-8")
    except UnicodeEncodeError:
        raise InvalidCatalogueName from None
    return name


def list_catalogue(actor: Actor | None) -> list[data.CatalogueLaboratory]:
    require_staff_actor(actor)
    return data.list_catalogue()


def create_laboratory(actor: Actor | None, name: object) -> data.NamedEntity:
    require_staff_actor(actor)
    return data.create_laboratory(_validated_name(name))


def rename_laboratory(
    actor: Actor | None, laboratory_id: int, name: object,
) -> data.NamedEntity:
    require_staff_actor(actor)
    laboratory = data.rename_laboratory(laboratory_id, _validated_name(name))
    if laboratory is None:
        raise LaboratoryNotFound
    return laboratory


def create_workstation(
    actor: Actor | None, laboratory_id: int, name: object,
) -> data.CreatedWorkstation:
    require_staff_actor(actor)
    try:
        workstation = data.create_workstation(
            laboratory_id, _validated_name(name),
        )
    except data.WorkstationNameConflict as error:
        raise DuplicateWorkstationName from error
    if workstation is None:
        raise LaboratoryNotFound
    return workstation


def rename_workstation(
    actor: Actor | None, laboratory_id: int, workstation_id: int, name: object,
) -> data.NamedWorkstation:
    require_staff_actor(actor)
    try:
        workstation = data.rename_workstation(
            laboratory_id, workstation_id, _validated_name(name),
        )
    except data.WorkstationNameConflict as error:
        raise DuplicateWorkstationName from error
    if workstation is None:
        raise WorkstationNotFound
    return workstation


def set_workstation_state(
    actor: Actor | None, laboratory_id: int, workstation_id: int,
    is_operational: object,
) -> data.WorkstationState:
    """Set the requested state of a workstation in the staff catalogue."""
    require_staff_actor(actor)
    if type(is_operational) is not bool:
        raise InvalidWorkstationState
    workstation = data.set_workstation_state(
        laboratory_id, workstation_id, is_operational,
    )
    if workstation is None:
        raise WorkstationNotFound
    return workstation
