"""Read-only personnel consultation against the two real booking services."""

from dataclasses import dataclass
from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from src.data.models import Booking, Laboratory, User, Workstation
from src.routes.booking_http import utc_text
from src.services.access import Actor, AuthenticationRequired
from src.services.staff_bookings import list_staff_bookings
from tests.http_helpers import csrf_post

STAFF_PAGE = "/staff/bookings"
STAFF_API = "/api/staff/bookings"


@dataclass(frozen=True)
class BookingScenario:
    personnel: User
    first: Booking
    second: Booking


@pytest.fixture
def booking_scenario(db: None, generated_password: str) -> BookingScenario:
    personnel = User.objects.create_user(
        "personnel@tests.example", generated_password, role=User.Role.PERSONNEL,
    )
    student = User.objects.create_user("first@tests.example")
    django_staff = User.objects.create_user("second@tests.example", is_staff=True)
    laboratory = Laboratory.objects.create(name="Laboratoire de test")
    first_station = Workstation.objects.create(laboratory=laboratory, name="Poste A")
    second_station = Workstation.objects.create(laboratory=laboratory, name="Poste B")
    start = (timezone.now() + timedelta(days=7)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    first = Booking.objects.create(
        owner=student, workstation=first_station, starts_at=start, ends_at=end,
    )
    second = Booking.objects.create(
        owner=django_staff, workstation=second_station, starts_at=start, ends_at=end,
    )
    return BookingScenario(personnel, first, second)


def booking_snapshot() -> list[dict[str, object]]:
    return list(Booking.objects.order_by("pk").values())


@pytest.mark.parametrize("criterion", ["AC-9-AC-40"], ids=str)
def test_personnel_consults_two_owners_in_stable_order(
    booking_scenario: BookingScenario, csrf_client: Client, generated_password: str, criterion: str,
) -> None:
    before = booking_snapshot()
    personnel = booking_scenario.personnel
    assert not personnel.is_staff
    login = csrf_post(csrf_client, "/api/auth/login", {
        "email": personnel.email, "password": generated_password, "next": STAFF_PAGE,
    })
    assert login.json() == {"redirect": STAFF_PAGE}

    labs = csrf_client.get("/labs")
    assert labs.status_code == 200
    assert f'href="{STAFF_PAGE}">Espace du personnel' in labs.content.decode()
    page = csrf_client.get(STAFF_PAGE)
    assert page.status_code == 200
    html = page.content.decode()
    assert '<h1>Espace du personnel</h1>' in html
    assert f'href="{STAFF_PAGE}" aria-current="page"' in html
    assert "Laboratoire de test" not in html
    assert "no-store" in page.headers["Cache-Control"]

    response = csrf_client.get(STAFF_API)
    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]
    assert response.json() == {"bookings": [
        {
            "id": booking.pk,
            "owner_id": booking.owner_id,
            "laboratory_name": booking.workstation.laboratory.name,
            "workstation_name": booking.workstation.name,
            "starts_at": utc_text(booking.starts_at),
            "ends_at": utc_text(booking.ends_at),
            "status": "future",
        }
        for booking in (booking_scenario.second, booking_scenario.first)
    ]}
    assert csrf_client.get("/api/bookings").json() == {"bookings": []}
    assert booking_snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-9"], ids=str)
def test_staff_sort_prioritizes_start_before_booking_id(
    booking_scenario: BookingScenario, criterion: str,
) -> None:
    first = booking_scenario.first
    first.starts_at += timedelta(days=1)
    first.ends_at += timedelta(days=1)
    first.save(update_fields=["starts_at", "ends_at"])
    before = booking_snapshot()
    client = Client()
    client.force_login(booking_scenario.personnel)
    response = client.get(STAFF_API)
    assert response.status_code == 200
    assert [row["id"] for row in response.json()["bookings"]] == [
        first.pk, booking_scenario.second.pk,
    ]
    assert booking_snapshot() == before


@pytest.mark.parametrize("owner", ["first", "second"], ids=["AC-5-AC-9-student", "AC-5-AC-9-is_staff"])
def test_students_keep_personal_history_and_are_denied_staff_routes(
    booking_scenario: BookingScenario, owner: str,
) -> None:
    before = booking_snapshot()
    booking = getattr(booking_scenario, owner)
    client = Client()
    client.force_login(booking.owner)
    assert STAFF_PAGE not in client.get("/labs").content.decode()
    assert client.get(STAFF_PAGE).status_code == 403
    denied = client.get(STAFF_API)
    assert denied.status_code == 403
    assert denied.json() == {"error": "Accès réservé au personnel."}
    personal = client.get("/api/bookings")
    assert personal.status_code == 200
    assert [row["id"] for row in personal.json()["bookings"]] == [booking.pk]
    assert booking_snapshot() == before
    booking.owner.refresh_from_db()
    assert booking.owner.role == User.Role.STUDENT
    assert booking.owner.is_staff == (owner == "second")


@pytest.mark.parametrize("condition", ["anonymous", "deactivated"], ids=["AC-9-anonymous", "AC-9-inactive"])
def test_staff_pages_and_api_require_an_active_session(
    booking_scenario: BookingScenario, condition: str,
) -> None:
    client = Client()
    if condition == "deactivated":
        personnel = booking_scenario.personnel
        client.force_login(personnel)
        personnel.is_active = False
        personnel.save(update_fields=["is_active"])
    before = booking_snapshot()
    page = client.get(STAFF_PAGE)
    assert page.status_code == 302
    assert page.url == f"/login?next={STAFF_PAGE}"
    response = client.get(STAFF_API)
    assert response.status_code == 401
    assert response.json() == {"error": "Connexion requise."}
    assert booking_snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-9"], ids=str)
def test_staff_api_is_read_only_including_empty_listing(
    db: None, csrf_client: Client, criterion: str,
) -> None:
    personnel = User.objects.create_user("empty-personnel@tests.example", role=User.Role.PERSONNEL)
    csrf_client.force_login(personnel)
    empty = csrf_client.get(STAFF_API)
    assert empty.status_code == 200
    assert empty.json() == {"bookings": []}
    csrf_denied = csrf_client.post(STAFF_API)
    assert csrf_denied.status_code == 403
    assert set(csrf_denied.json()) == {"error"}
    denied = csrf_post(csrf_client, STAFF_API, {})
    assert denied.status_code == 405 and denied.headers["Allow"] == "GET"
    assert booking_snapshot() == []


@pytest.mark.parametrize("criterion", ["AC-9"], ids=str)
def test_staff_service_rejects_inactive_actor_without_a_request(criterion: str) -> None:
    with pytest.raises(AuthenticationRequired):
        list_staff_bookings(Actor(1, "inactive@tests.example", User.Role.PERSONNEL, False))
