"""Catalogue access policy shared by HTTP and future MCP adapters."""

from src.data import labs

from .access import Actor, require_authenticated


def list_laboratories(actor: Actor | None) -> list[dict[str, int | str]]:
    require_authenticated(actor)
    return labs.list_laboratories()
