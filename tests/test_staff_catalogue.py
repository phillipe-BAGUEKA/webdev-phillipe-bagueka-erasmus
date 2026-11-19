"""AC-6–8: personnel catalogue against PostgreSQL and real Django middleware."""

from dataclasses import dataclass
import json

import pytest
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import Client

from src.data.models import Laboratory, User, Workstation
from tests.http_helpers import csrf_post


PAGE = "/staff/catalogue"
API = "/api/staff/catalogue"


@dataclass(frozen=True)
class CatalogueRows:
    first: Laboratory
    second: Laboratory
    workstation: Workstation


@pytest.fixture
def personnel(db: None, generated_password: str) -> User:
    return User.objects.create_user(
        "catalogue@tests.example", generated_password, role=User.Role.PERSONNEL,
    )


@pytest.fixture
def personnel_client(csrf_client: Client, personnel: User) -> Client:
    csrf_client.force_login(personnel)
    return csrf_client


@pytest.fixture
def catalogue_rows(db: None) -> CatalogueRows:
    first = Laboratory.objects.create(name="Premier laboratoire")
    second = Laboratory.objects.create(name="Autre laboratoire")
    workstation = Workstation.objects.create(
        laboratory=first, name="Poste P1", is_operational=False,
    )
    return CatalogueRows(first, second, workstation)


def catalogue_snapshot() -> tuple[list[tuple[int, str]], list[tuple[int, int, str, bool]]]:
    return (
        list(Laboratory.objects.order_by("pk").values_list("id", "name")),
        list(Workstation.objects.order_by("pk").values_list(
            "id", "laboratory_id", "name", "is_operational",
        )),
    )


def laboratory_url(laboratory_id: int) -> str:
    return f"{API}/laboratories/{laboratory_id}"


def json_write(
    client: Client, method: str, url: str, data: dict[str, object], *,
    csrf: bool = True,
) -> HttpResponse:
    headers = {}
    if csrf:
        headers["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
    return client.generic(
        method, url, json.dumps(data), content_type="application/json", **headers,
    )


def mutation_paths(rows: CatalogueRows) -> list[tuple[str, str]]:
    laboratory = laboratory_url(rows.first.pk)
    return [
        ("POST", API),
        ("PATCH", laboratory),
        ("POST", f"{laboratory}/workstations"),
        ("PATCH", f"{laboratory}/workstations/{rows.workstation.pk}"),
    ]


@pytest.mark.parametrize("criterion", ["AC-6-AC-7-AC-8-AC-40"], ids=str)
def test_catalogue_create_rename_and_reload(
    csrf_client: Client, personnel: User, generated_password: str, criterion: str,
) -> None:
    assert not personnel.is_staff
    login = csrf_post(csrf_client, "/api/auth/login", {
        "email": personnel.email, "password": generated_password, "next": PAGE,
    })
    assert login.json() == {"redirect": PAGE}
    assert f'href="{PAGE}"' in csrf_client.get("/staff/bookings").content.decode()
    assert csrf_client.get(API).json() == {"laboratories": []}

    laboratory = json_write(csrf_client, "POST", API, {"name": " Laboratoire A "})
    assert laboratory.status_code == 201
    lab_id = laboratory.json()["laboratory"]["id"]
    assert laboratory.json() == {"laboratory": {"id": lab_id, "name": "Laboratoire A"}}
    assert Laboratory.objects.count() == 1
    lab_url = laboratory_url(lab_id)
    station = json_write(csrf_client, "POST", f"{lab_url}/workstations", {"name": "Poste A"})
    assert station.status_code == 201
    station_id = station.json()["workstation"]["id"]
    assert station.json() == {"workstation": {
        "id": station_id, "name": "Poste A", "laboratory_id": lab_id,
    }}
    assert Workstation.objects.count() == 1

    renamed_lab = json_write(csrf_client, "PATCH", lab_url, {"name": "Laboratoire B"})
    assert renamed_lab.status_code == 200
    assert renamed_lab.json() == {"laboratory": {"id": lab_id, "name": "Laboratoire B"}}
    renamed_station = json_write(
        csrf_client, "PATCH", f"{lab_url}/workstations/{station_id}", {"name": "Poste B"},
    )
    assert renamed_station.status_code == 200
    assert renamed_station.json() == {"workstation": {
        "id": station_id, "name": "Poste B", "laboratory_id": lab_id,
    }}

    page = csrf_client.get(PAGE)
    assert page.status_code == 200
    assert f'href="{PAGE}" aria-current="page"' in page.content.decode()
    assert "no-store" in page.headers["Cache-Control"]
    listing = csrf_client.get(API)
    assert listing.status_code == 200
    assert "no-store" in listing.headers["Cache-Control"]
    assert listing.json() == {"laboratories": [
        {"id": lab_id, "name": "Laboratoire B", "workstations": [
            {"id": station_id, "name": "Poste B"},
        ]},
    ]}
    assert catalogue_snapshot() == (
        [(lab_id, "Laboratoire B")], [(station_id, lab_id, "Poste B", True)],
    )


@pytest.mark.parametrize("criterion", ["AC-7-AC-8"], ids=str)
def test_postgres_workstation_names_unique_per_laboratory(
    personnel_client: Client, catalogue_rows: CatalogueRows, criterion: str,
) -> None:
    rows = catalogue_rows
    first_path = f"{laboratory_url(rows.first.pk)}/workstations"
    second_path = f"{laboratory_url(rows.second.pk)}/workstations"
    before = catalogue_snapshot()
    duplicate = json_write(personnel_client, "POST", first_path, {"name": " Poste P1 "})
    assert duplicate.status_code == 409
    assert set(duplicate.json()) == {"error"}
    assert catalogue_snapshot() == before

    other = json_write(personnel_client, "POST", second_path, {"name": "Poste P1"})
    assert other.status_code == 201
    assert other.json()["workstation"]["laboratory_id"] == rows.second.pk
    another = Workstation.objects.create(laboratory=rows.first, name="Poste P2")
    before = catalogue_snapshot()
    renamed = json_write(
        personnel_client, "PATCH", f"{first_path}/{another.pk}", {"name": "Poste P1"},
    )
    assert renamed.status_code == 409
    assert catalogue_snapshot() == before

    renamed = json_write(
        personnel_client, "PATCH", f"{first_path}/{rows.workstation.pk}", {"name": "Poste P3"},
    )
    assert renamed.status_code == 200
    rows.workstation.refresh_from_db()
    assert rows.workstation.name == "Poste P3"
    assert rows.workstation.laboratory_id == rows.first.pk
    assert rows.workstation.is_operational is False

    listing = personnel_client.get(API)
    assert listing.status_code == 200
    assert listing.json() == {"laboratories": [
        {"id": rows.first.pk, "name": rows.first.name, "workstations": [
            {"id": rows.workstation.pk, "name": "Poste P3"},
            {"id": another.pk, "name": "Poste P2"},
        ]},
        {"id": rows.second.pk, "name": rows.second.name, "workstations": [
            {"id": other.json()["workstation"]["id"], "name": "Poste P1"},
        ]},
    ]}


@pytest.mark.parametrize("django_staff", [False, True], ids=["AC-5-student", "AC-5-is_staff"])
def test_student_cannot_apply_catalogue_mutations(
    csrf_client: Client, catalogue_rows: CatalogueRows, django_staff: bool,
) -> None:
    student = User.objects.create_user("student-catalogue@tests.example", is_staff=django_staff)
    csrf_client.force_login(student)
    before = catalogue_snapshot()
    assert PAGE not in csrf_client.get("/labs").content.decode()
    assert csrf_client.get(PAGE).status_code == 403
    assert csrf_client.get(API).status_code == 403
    for method, path in mutation_paths(catalogue_rows):
        response = json_write(csrf_client, method, path, {"name": "Refus attendu"})
        assert response.status_code == 403
        assert response.json() == {"error": "Accès réservé au personnel."}
    student.refresh_from_db()
    assert student.role == User.Role.STUDENT and student.is_staff == django_staff
    assert catalogue_snapshot() == before


@pytest.mark.parametrize("active_session", [False, True], ids=["AC-5-no-session", "AC-5-inactive"])
def test_catalogue_rejects_missing_or_inactive_session(
    csrf_client: Client, personnel: User, catalogue_rows: CatalogueRows, active_session: bool,
) -> None:
    if active_session:
        csrf_client.force_login(personnel)
        personnel.is_active = False
        personnel.save(update_fields=["is_active"])
    before = catalogue_snapshot()
    page = csrf_client.get(PAGE)
    assert page.status_code == 302 and page.url == f"/login?next={PAGE}"
    assert csrf_client.get(API).status_code == 401
    for method, path in mutation_paths(catalogue_rows):
        denied = json_write(csrf_client, method, path, {"name": "Refus attendu"})
        assert denied.status_code == 401
        assert denied.json() == {"error": "Connexion requise."}
    assert catalogue_snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-6-AC-7-AC-8"], ids=str)
def test_each_write_requires_csrf_and_rejects_unexpected_fields(
    personnel_client: Client, catalogue_rows: CatalogueRows, criterion: str,
) -> None:
    before = catalogue_snapshot()
    for method, path in mutation_paths(catalogue_rows):
        missing_token = json_write(personnel_client, method, path, {"name": "Refus"}, csrf=False)
        assert missing_token.status_code == 403
        assert "vérification de sécurité" in missing_token.json()["error"]
        unexpected = json_write(personnel_client, method, path, {
            "name": "Refus", "is_operational": False, "laboratory_id": catalogue_rows.second.pk,
        })
        assert unexpected.status_code == 422
    assert catalogue_snapshot() == before


@pytest.mark.parametrize("name", [None, 7, "  ", "x" * 151, "a\0b", "\ud800"], ids=[
    "AC-6-null", "AC-6-number", "AC-6-blank", "AC-6-length", "AC-6-nul", "AC-6-unicode",
])
def test_bad_names_leave_catalogue_unchanged(personnel_client: Client, name: object) -> None:
    before = catalogue_snapshot()
    invalid = json_write(personnel_client, "POST", API, {"name": name})
    assert invalid.status_code == 422
    assert catalogue_snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-7-AC-8"], ids=str)
def test_unknown_identifiers_and_wrong_parent_are_404(
    personnel_client: Client, catalogue_rows: CatalogueRows, criterion: str,
) -> None:
    rows = catalogue_rows
    missing = laboratory_url(rows.second.pk + 1)
    before = catalogue_snapshot()
    wrong_parent = f"{laboratory_url(rows.second.pk)}/workstations/{rows.workstation.pk}"
    assert json_write(personnel_client, "PATCH", missing, {"name": "Renommé"}).status_code == 404
    assert json_write(personnel_client, "POST", f"{missing}/workstations", {"name": "Poste"}).status_code == 404
    assert json_write(personnel_client, "PATCH", wrong_parent, {"name": "Renommé"}).status_code == 404
    assert catalogue_snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-7"], ids=str)
def test_catalogue_does_not_translate_other_integrity_errors_to_name_conflicts(
    personnel_client: Client, catalogue_rows: CatalogueRows, criterion: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = catalogue_snapshot()

    def fail_create(**values: object) -> Workstation:
        raise IntegrityError("synthetic internal details")

    monkeypatch.setattr(Workstation.objects, "create", fail_create)
    response = json_write(
        personnel_client, "POST", f"{laboratory_url(catalogue_rows.first.pk)}/workstations",
        {"name": "Poste"},
    )
    assert response.status_code == 500
    assert response.json() == {"error": "Erreur interne."}
    assert catalogue_snapshot() == before
