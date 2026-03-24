"""
reminder_engine.py — Daily APScheduler job that evaluates vaccine due dates
and creates / dispatches reminders.

Reminder Types:
  7_day    → due_date - today == 7
  2_day    → due_date - today == 2
  due_today→ due_date == today
  overdue_3→ today - due_date == 3 (status != done)
  overdue_7→ today - due_date == 7 (status != done) — URGENT priority

Escalation:
  overdue_7 reminders are flagged priority='urgent'.

Quiet Hours:
  Handled by dispatcher — engine only creates DB rows; delivery may be queued.

Duplicate Prevention:
  Uses ON CONFLICT DO NOTHING — same (child, vaccine, type, channel)
  is never inserted twice.
"""
import logging
from datetime import date, timedelta
from typing import List, Tuple

from sqlalchemy.dialects.postgresql import insert as pg_insert

from db_engine import get_db
from models import Child, Reminder, ReminderPriority, VaccinationRecord, Vaccine, VaccineStatus
from notifications.dispatcher import dispatch_reminder, flush_queued_reminders

logger = logging.getLogger(__name__)

# All notification channels in use
CHANNELS: List[str] = ["sms", "whatsapp", "email", "push"]

# (days_diff, reminder_type, days_sign)
# days_sign: +1 = upcoming, -1 = overdue
_REMINDER_CONFIG: List[Tuple[int, str, str]] = [
    (7,  "7_day",    "upcoming"),
    (2,  "2_day",    "upcoming"),
    (0,  "due_today","today"),
    (-3, "overdue_3","overdue"),
    (-7, "overdue_7","overdue"),
]


def compute_reminder_types(due_date: date, today: date, status: VaccineStatus) -> List[str]:
    """
    Return the list of reminder_type strings that apply for a given
    due_date/today/status combination.
    """
    delta = (due_date - today).days
    result = []
    for days_diff, rtype, kind in _REMINDER_CONFIG:
        if kind == "upcoming" and delta == days_diff:
            result.append(rtype)
        elif kind == "today" and delta == 0:
            result.append(rtype)
        elif kind == "overdue" and delta == days_diff and status != VaccineStatus.done:
            result.append(rtype)
    return result


def _priority_for(reminder_type: str) -> ReminderPriority:
    return ReminderPriority.urgent if reminder_type == "overdue_7" else ReminderPriority.normal


def _create_reminder_row(session, child_id: int, vaccine_id: int,
                         reminder_type: str, channel: str) -> None:
    """
    Insert a reminder row if it doesn't already exist.
    ON CONFLICT DO NOTHING prevents duplicates.
    """
    from datetime import datetime
    stmt = (
        pg_insert(Reminder)
        .values(
            child_id      = child_id,
            vaccine_id    = vaccine_id,
            reminder_type = reminder_type,
            reminder_date = datetime.utcnow(),
            sent_status   = False,
            channel       = channel,
            priority      = _priority_for(reminder_type),
            queued        = False,
        )
        .on_conflict_do_nothing(
            index_elements=None,
            constraint="uq_reminder_child_vaccine_type_channel",
        )
    )
    session.execute(stmt)


def run_reminder_job() -> None:
    """
    Main scheduler job. Runs once daily at 7:00 AM.

    Steps:
    1. Flush any queued (quiet-hours-delayed) reminders from previous runs.
    2. For each active vaccination record, compute reminder types for today.
    3. Insert reminder rows (deduped) into the reminders table.
    4. Dispatch each newly-created or still-unsent reminder.
    """
    today = date.today()
    logger.info("=== Reminder job started for %s ===", today)

    # Step 1: flush queued reminders from overnight
    flush_queued_reminders()

    new_reminder_ids: List[int] = []

    # Step 2 & 3: compute and insert
    with get_db() as session:
        records: List[VaccinationRecord] = (
            session.query(VaccinationRecord)
            .filter(VaccinationRecord.status != VaccineStatus.done)
            .all()
        )

        logger.info("Processing %d active vaccination records …", len(records))

        for record in records:
            child:   Child   = session.get(Child,   record.child_id)
            vaccine: Vaccine = session.get(Vaccine, record.vaccine_id)

            if not child or not vaccine:
                continue

            due_date = child.dob + timedelta(days=vaccine.due_days)
            reminder_types = compute_reminder_types(due_date, today, record.status)

            if not reminder_types:
                continue

            for rtype in reminder_types:
                for channel in CHANNELS:
                    _create_reminder_row(session, child.id, vaccine.id, rtype, channel)

    # Step 4: dispatch all unsent reminders (newly created + previous failures)
    with get_db() as session:
        unsent: List[Reminder] = (
            session.query(Reminder)
            .filter(Reminder.sent_status == False, Reminder.queued == False)  # noqa: E712
            .all()
        )

    logger.info("Dispatching %d unsent reminders …", len(unsent))
    for reminder in unsent:
        dispatch_reminder(reminder)

    logger.info("=== Reminder job finished for %s ===", today)
