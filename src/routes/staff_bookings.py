"""Read-only page and JSON listing for the personnel business role."""

from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services.access import AuthenticationRequired
from src.services.staff_bookings import StaffAccessDenied, list_staff_bookings, require_staff_actor

from .booking_http import STAFF_ACCESS_MESSAGE, api_methods, utc_text
from .session import current_actor


@never_cache
@require_GET
def reservations_page(request: HttpRequest) -> HttpResponse:
    try:
        require_staff_actor(current_actor(request))
    except AuthenticationRequired:
        return redirect_to_login(request.get_full_path(), login_url=reverse("login"))
    except StaffAccessDenied:
        return HttpResponseForbidden(STAFF_ACCESS_MESSAGE, content_type="text/plain; charset=utf-8")
    return render(request, "staff_bookings.html", {"staff_can_view_bookings": True})


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
        }
        for booking in bookings
    ]})
