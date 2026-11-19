"""Render sign-in, laboratories and safe CSRF errors."""

from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services.access import AuthenticationRequired, require_authenticated
from src.services.staff_bookings import StaffAccessDenied, require_staff_actor

from .forms import LoginForm
from .booking_http import API_ROUTE_NAMES
from .session import current_actor, safe_return_path, wants_json


@never_cache
@require_GET
def login_page(request: HttpRequest) -> HttpResponse:
    destination = safe_return_path(request.GET.get("next", ""))
    if current_actor(request) is not None:
        return redirect(destination)
    return render(
        request,
        "login.html",
        {
            "form": LoginForm(),
            "next": destination,
            "logged_out": request.GET.get("logged_out") == "1",
        },
    )


@never_cache
@require_GET
def laboratories_page(request: HttpRequest) -> HttpResponse:
    try:
        actor = require_authenticated(current_actor(request))
    except AuthenticationRequired:
        return redirect_to_login(request.get_full_path(), login_url=reverse("login"))
    try:
        require_staff_actor(actor)
    except StaffAccessDenied:
        staff_can_view_bookings = False
    else:
        staff_can_view_bookings = True
    return render(request, "labs.html", {
        "actor": actor,
        "staff_can_view_bookings": staff_can_view_bookings,
    })


@never_cache
def csrf_failure(request: HttpRequest, reason: str = "") -> HttpResponse:
    message = (
        "La vérification de sécurité a échoué. Recharge la page puis réessaie."
    )
    match = request.resolver_match
    if (match is not None and match.url_name in API_ROUTE_NAMES) or wants_json(request):
        return JsonResponse({"error": message}, status=403)
    return render(request, "csrf_error.html", {"error": message}, status=403)
