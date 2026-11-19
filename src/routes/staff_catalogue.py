"""HTTP adapters for the personnel catalogue, with Django session and CSRF."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services import staff_catalogue
from src.services.access import require_staff_actor

from .booking_http import api_methods, json_object
from .pages import render_staff_page
from .session import current_actor


def requested_name(request: HttpRequest) -> object:
    return json_object(request, {"name"}, max_bytes=4096)["name"]


@never_cache
@require_GET
def catalogue_page(request: HttpRequest) -> HttpResponse:
    return render_staff_page(request, "staff_catalogue.html")


@api_methods("GET", "POST")
def catalogue_api(request: HttpRequest) -> JsonResponse:
    actor = require_staff_actor(current_actor(request))
    if request.method == "GET":
        return JsonResponse({"laboratories": staff_catalogue.list_catalogue(actor)})
    laboratory = staff_catalogue.create_laboratory(actor, requested_name(request))
    return JsonResponse({"laboratory": laboratory}, status=201)


@api_methods("PATCH")
def laboratory_api(request: HttpRequest, laboratory_id: int) -> JsonResponse:
    actor = require_staff_actor(current_actor(request))
    laboratory = staff_catalogue.rename_laboratory(
        actor, laboratory_id, requested_name(request),
    )
    return JsonResponse({"laboratory": laboratory})


@api_methods("POST")
def workstations_api(request: HttpRequest, laboratory_id: int) -> JsonResponse:
    actor = require_staff_actor(current_actor(request))
    workstation = staff_catalogue.create_workstation(
        actor, laboratory_id, requested_name(request),
    )
    return JsonResponse({"workstation": workstation}, status=201)


@api_methods("PATCH")
def workstation_api(
    request: HttpRequest, laboratory_id: int, workstation_id: int,
) -> JsonResponse:
    actor = require_staff_actor(current_actor(request))
    workstation = staff_catalogue.rename_workstation(
        actor, laboratory_id, workstation_id, requested_name(request),
    )
    return JsonResponse({"workstation": workstation})


@api_methods("PATCH")
def workstation_state_api(
    request: HttpRequest, laboratory_id: int, workstation_id: int,
) -> JsonResponse:
    actor = require_staff_actor(current_actor(request))
    desired = json_object(request, {"is_operational"}, max_bytes=4096)
    workstation = staff_catalogue.set_workstation_state(
        actor, laboratory_id, workstation_id, desired["is_operational"],
    )
    return JsonResponse({"workstation": workstation})
