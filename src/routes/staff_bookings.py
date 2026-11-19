"""Read-only page and JSON listing for the personnel business role."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services.staff_bookings import list_staff_bookings

from .booking_http import api_methods, utc_text
from .pages import render_staff_page
from .session import current_actor


@never_cache
@require_GET
def reservations_page(request: HttpRequest) -> HttpResponse:
    return render_staff_page(request, "staff_bookings.html")


@api_methods("GET")
def reservations_api(request: HttpRequest) -> JsonResponse:
    bookings = list_staff_bookings(current_actor(request))
    return JsonResponse({"bookings": [
        {
            "id": booking.booking_id,
            "owner_id": booking.owner_id,
            "laboratory_name": booking.laboratory_name,
            "workstation_name": booking.workstation_name,
            "starts_at": utc_text(booking.starts_at),
            "ends_at": utc_text(booking.ends_at),
            "status": booking.status,
            "is_operational": booking.is_operational,
        }
        for booking in bookings
    ]})
