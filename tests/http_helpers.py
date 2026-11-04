"""HTTP test helpers using only isolated client cookies and test credentials."""

from django.http import HttpResponse
from django.test import Client


def csrf_post(
    client: Client,
    path: str,
    data: dict[str, str] | None = None,
    accept: str = "application/json",
) -> HttpResponse:
    return client.post(
        path,
        data or {},
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        HTTP_ACCEPT=accept,
    )
