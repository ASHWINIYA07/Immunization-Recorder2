"""
db_sync.py — Pull data from the FastAPI backend and upsert into PostgreSQL.

Syncs:
  - children       (from GET /children)
  - vaccines       (derived from schedule entries)
  - vaccination_records (from GET /schedule/{child_id})

Run this before the scheduler starts to ensure the DB is current.
"""
import logging
from datetime import date, datetime
from typing import Dict, List

from sqlalchemy.dialects.postgresql import insert as pg_insert

from api_client import get_children, get_schedule, APIError
from db_engine import get_db
from models import Child, Vaccine, VaccinationRecord, VaccineStatus

logger = logging.getLogger(__name__)

# IAP default vaccine schedule (days from birth) — used as fallback if
# the backend does not return due_days explicitly
_FALLBACK_DUE_DAYS: Dict[str, int] = {
    "BCG":                    0,
    "Hepatitis B (Birth)":    0,
    "DTP 1":                 42,
    "DTP 2":                 70,
    "DTP 3":                 98,
    "Polio 1":               42,
    "Polio 2":               70,
    "Polio 3":               98,
    "Penta-1":               42,
    "Penta-2":               70,
    "Penta-3":               98,
    "Rotavirus 1":           42,
    "Rotavirus 2":           70,
    "Rotavirus 3":           98,
    "PCV 1":                 42,
    "PCV 2":                 70,
    "PCV Booster":          365,
    "IPV 1":                 42,
    "IPV 2":                 70,
    "Measles":              270,
    "MMR 1":                270,
    "MMR 2":                540,
    "Varicella 1":          365,
    "Varicella 2":          540,
    "Typhoid":              730,
    "Hepatitis A 1":        365,
    "Hepatitis A 2":        548,
    "DTP Booster 1":        548,
    "DTP Booster 2":       1825,
}


def _parse_date(value: str) -> date:
    """Parse YYYY-MM-DD date string."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def _upsert_child(session, child_data: Dict) -> Child:
    """Insert or update a child row and return the ORM object."""
    child_id = child_data.get("id")
    dob_raw  = child_data.get("dob", "")

    stmt = (
        pg_insert(Child)
        .values(
            id           = child_id,
            name         = child_data.get("name", ""),
            dob          = _parse_date(dob_raw) if dob_raw else date.today(),
            phone_number = child_data.get("phone_number") or child_data.get("phone"),
            email        = child_data.get("email"),
            device_token = child_data.get("device_token"),
        )
        .on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name":         pg_insert(Child).excluded.name,
                "dob":          pg_insert(Child).excluded.dob,
                "phone_number": pg_insert(Child).excluded.phone_number,
                "email":        pg_insert(Child).excluded.email,
                "device_token": pg_insert(Child).excluded.device_token,
            },
        )
    )
    session.execute(stmt)
    return session.query(Child).filter(Child.id == child_id).one()


def _upsert_vaccine(session, vaccine_name: str, due_days: int) -> Vaccine:
    """Insert or update a vaccine row."""
    stmt = (
        pg_insert(Vaccine)
        .values(name=vaccine_name, due_days=due_days)
        .on_conflict_do_update(
            index_elements=["name"],
            set_={"due_days": pg_insert(Vaccine).excluded.due_days},
        )
    )
    session.execute(stmt)
    return session.query(Vaccine).filter(Vaccine.name == vaccine_name).one()


def _upsert_record(session, child_id: int, vaccine_id: int,
                   status: str, taken_date=None) -> None:
    """Insert or update a vaccination record."""
    try:
        vax_status = VaccineStatus(status)
    except ValueError:
        vax_status = VaccineStatus.upcoming

    taken = _parse_date(taken_date) if taken_date else None

    stmt = (
        pg_insert(VaccinationRecord)
        .values(
            child_id   = child_id,
            vaccine_id = vaccine_id,
            status     = vax_status,
            taken_date = taken,
        )
        .on_conflict_do_update(
            constraint="uq_child_vaccine",
            set_={
                "status":     pg_insert(VaccinationRecord).excluded.status,
                "taken_date": pg_insert(VaccinationRecord).excluded.taken_date,
            },
        )
    )
    session.execute(stmt)


def sync_all() -> None:
    """
    Main sync entry point.
    Fetches all children and their vaccination schedules from the backend
    and upserts into PostgreSQL.
    """
    logger.info("Starting backend ↔ PostgreSQL sync …")

    try:
        children_data: List[Dict] = get_children()
    except APIError as exc:
        logger.error("Cannot fetch children from API: %s", exc)
        return

    if not children_data:
        logger.warning("No children returned from API — nothing to sync.")
        return

    with get_db() as session:
        for child_data in children_data:
            child_id = child_data.get("id")
            if not child_id:
                logger.warning("Child data missing id, skipping: %s", child_data)
                continue

            try:
                child = _upsert_child(session, child_data)
                logger.info("Synced child: %s (id=%s)", child.name, child.id)
            except Exception as exc:
                logger.error("Failed to upsert child %s: %s", child_id, exc)
                continue

            try:
                schedule: List[Dict] = get_schedule(child_id)
            except APIError as exc:
                logger.error("Cannot fetch schedule for child %s: %s", child_id, exc)
                continue

            for entry in schedule:
                vaccine_name = entry.get("vaccine", "")
                if not vaccine_name:
                    continue

                # Resolve due_days: prefer backend value, then fallback map
                due_days = (
                    entry.get("due_days")
                    or _FALLBACK_DUE_DAYS.get(vaccine_name)
                    or 0
                )

                try:
                    vaccine = _upsert_vaccine(session, vaccine_name, due_days)
                    _upsert_record(
                        session,
                        child_id   = child.id,
                        vaccine_id = vaccine.id,
                        status     = entry.get("status", "upcoming"),
                        taken_date = entry.get("taken_date"),
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to upsert record child=%s vaccine=%s: %s",
                        child_id, vaccine_name, exc
                    )

    logger.info("Sync complete.")
