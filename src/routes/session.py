"""Translate the authenticated HTTP session into a service actor."""

from urllib.parse import urlsplit

from django.http import HttpRequest
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from src.services.access import Actor


def current_actor(request: HttpRequest) -> Actor | None:
    user = request.user
    if not user.is_authenticated:
        return None
    return Actor(
        user_id=user.pk,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


def safe_return_path(value: str) -> str:
    """Keep post-login destinations on the allowlist of protected pages."""
    fallback = reverse("laboratories")
    target = value.strip()
    if not url_has_allowed_host_and_scheme(target, allowed_hosts=set()):
        return fallback
    if urlsplit(target).path not in {fallback, reverse("staff-bookings")}:
        return fallback
    return target


def wants_json(request: HttpRequest) -> bool:
    return "application/json" in request.headers.get("Accept", "")
