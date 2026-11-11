"""PostgreSQL schema guarantees only; no service, permission or race proof."""

from datetime import datetime, timedelta, timezone

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError

from src.data.models import Booking, Laboratory, User, Workstation

Catalogue = tuple[Laboratory, Workstation, Workstation, User, User]


@pytest.fixture
def catalogue(db: None) -> Catalogue:
    assert connection.vendor == "postgresql"
    lab = Laboratory.objects.create(name="Isolated schema laboratory")
    first = Workstation.objects.create(laboratory=lab, name="Post A")
    second = Workstation.objects.create(laboratory=lab, name="Post B")
    owner = User.objects.create_user("owner@schema.example")
    other = User.objects.create_user("other@schema.example")
    return lab, first, second, owner, other


def create_booking(owner: User, station: Workstation, offset: int = 0) -> Booking:
    start = datetime(2030, 1, 7, 8, tzinfo=timezone.utc) + timedelta(minutes=offset)
    return Booking.objects.create(
        owner=owner, workstation=station, starts_at=start,
        ends_at=start + timedelta(hours=1),
    )


@pytest.mark.parametrize("criterion", ["AC-15-schema"], ids=str)
def test_valid_booking_persists_aware_instants(catalogue: Catalogue, criterion: str) -> None:
    _, first, _, owner, _ = catalogue
    booking = create_booking(owner, first)
    booking.refresh_from_db()
    assert booking.owner_id == owner.pk and booking.workstation_id == first.pk
    assert booking.ends_at - booking.starts_at == timedelta(hours=1)
    assert booking.created_at.tzinfo is not None
    assert booking.starts_at.tzinfo is not None and booking.cancelled_at is None
    assert Booking.objects.count() == 1


@pytest.mark.parametrize("minutes", [-60, 0, 30, 120], ids=lambda n: f"AC-16-schema-{n}")
def test_invalid_interval_rejected_without_row(catalogue: Catalogue, minutes: int) -> None:
    _, first, _, owner, _ = catalogue
    start = datetime(2030, 1, 7, 8, tzinfo=timezone.utc)
    with pytest.raises(DatabaseError) as error, transaction.atomic():
        Booking.objects.create(
            owner=owner, workstation=first, starts_at=start,
            ends_at=start + timedelta(minutes=minutes),
        )
    # Reversed ranges are also rejected by PostgreSQL's range constructor.
    assert error.value.__cause__.sqlstate in {"23514", "22000"}
    if minutes >= 0:
        assert error.value.__cause__.diag.constraint_name in {
            "booking_positive_interval", "booking_one_hour"
        }
    assert Booking.objects.count() == 0


@pytest.mark.parametrize("offset", [0, 30], ids=lambda n: f"AC-17-schema-{n}")
def test_same_workstation_overlap_rejected(catalogue: Catalogue, offset: int) -> None:
    _, first, _, owner, other = catalogue
    original = create_booking(owner, first)
    with pytest.raises(IntegrityError) as error, transaction.atomic():
        create_booking(other, first, offset)
    assert error.value.__cause__.diag.constraint_name == "booking_workstation_no_overlap"
    assert list(Booking.objects.values_list("pk", flat=True)) == [original.pk]


@pytest.mark.parametrize("offset", [0, 30], ids=lambda n: f"AC-18-schema-{n}")
def test_same_owner_overlap_on_other_station_rejected(catalogue: Catalogue, offset: int) -> None:
    _, first, second, owner, _ = catalogue
    original = create_booking(owner, first)
    with pytest.raises(IntegrityError) as error, transaction.atomic():
        create_booking(owner, second, offset)
    assert error.value.__cause__.diag.constraint_name == "booking_owner_no_overlap"
    assert list(Booking.objects.values_list("pk", flat=True)) == [original.pk]


@pytest.mark.parametrize("criterion", ["AC-19-schema"], ids=str)
def test_consecutive_half_open_intervals_are_allowed(catalogue: Catalogue, criterion: str) -> None:
    _, first, _, owner, _ = catalogue
    before = create_booking(owner, first)
    after = create_booking(owner, first, 60)
    assert before.ends_at == after.starts_at
    assert Booking.objects.count() == 2


@pytest.mark.parametrize("criterion", ["AC-25-schema-AC-28-schema"], ids=str)
def test_cancelled_row_retained_but_excluded_from_both_conflicts(
    catalogue: Catalogue, criterion: str,
) -> None:
    _, first, _, owner, _ = catalogue
    original = create_booking(owner, first)
    original.cancelled_at = datetime(2029, 1, 1, tzinfo=timezone.utc)
    original.save(update_fields=["cancelled_at"])
    replacement = create_booking(owner, first)
    original.refresh_from_db()
    assert original.cancelled_at is not None
    assert replacement.pk != original.pk and Booking.objects.count() == 2


def test_workstation_names_unique_only_inside_laboratory(catalogue: Catalogue) -> None:
    lab, first, _, _, _ = catalogue
    with pytest.raises(IntegrityError), transaction.atomic():
        Workstation.objects.create(laboratory=lab, name=first.name)
    other_lab = Laboratory.objects.create(name="Other isolated lab")
    Workstation.objects.create(laboratory=other_lab, name=first.name)
    assert Workstation.objects.count() == 3


@pytest.mark.parametrize("criterion", ["AC-14-schema"], ids=str)
def test_postgresql_timezone_columns_and_non_admin_role(
    catalogue: Catalogue, criterion: str,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name='data_booking' "
            "AND column_name IN ('starts_at','ends_at','created_at','cancelled_at')"
        )
        assert dict(cursor.fetchall()) == {
            name: "timestamp with time zone"
            for name in ("starts_at", "ends_at", "created_at", "cancelled_at")
        }
        cursor.execute(
            "SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles "
            "WHERE rolname=current_user"
        )
        assert cursor.fetchone() == (False, False, False)


@pytest.mark.parametrize("target", ["lab", "station", "owner"])
def test_orm_protects_references(catalogue: Catalogue, target: str) -> None:
    lab, first, _, owner, _ = catalogue
    booking = create_booking(owner, first)
    obj = {"lab": lab, "station": first, "owner": owner}[target]
    with pytest.raises(ProtectedError):
        obj.delete()
    assert Booking.objects.get(pk=booking.pk).owner_id == owner.pk
    assert type(obj).objects.filter(pk=obj.pk).exists()


@pytest.mark.parametrize("target", ["lab", "station", "owner"])
def test_raw_database_delete_cannot_cascade(catalogue: Catalogue, target: str) -> None:
    lab, first, _, owner, _ = catalogue
    booking = create_booking(owner, first)
    obj = {"lab": lab, "station": first, "owner": owner}[target]
    with pytest.raises(IntegrityError), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                f'DELETE FROM "{obj._meta.db_table}" WHERE id = %s', [obj.pk]
            )
        connection.check_constraints()
    assert Booking.objects.filter(pk=booking.pk).exists()
    assert type(obj).objects.filter(pk=obj.pk).exists()
