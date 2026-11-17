"""Transport parsing limits reject oversized input before Django buffers it."""

import pytest
from django.test import RequestFactory

from src.routes.booking_http import PayloadError, json_object


@pytest.mark.parametrize("label", ["AC-29-oversized-before-body-read"])
def test_body_larger_than_django_default_is_explicit_input_refusal(label: str) -> None:
    request = RequestFactory().post("/", data="x" * 3000000, content_type="application/json")
    with pytest.raises(PayloadError) as caught:
        json_object(request, {"date", "need"}, max_bytes=16384)
    assert caught.value.status == 422
