"""Read the minimal laboratory catalogue through the ORM."""

from .models import Laboratory


def list_laboratories() -> list[dict[str, int | str]]:
    return list(Laboratory.objects.order_by("id").values("id", "name"))
