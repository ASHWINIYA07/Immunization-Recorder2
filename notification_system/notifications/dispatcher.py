"""
dispatcher.py — Route and deliver notifications across channels.

Responsibilities:
  - Route reminder to correct sender (sms / whatsapp / email / push)
  - Enforce quiet hours (10 PM – 7 AM) → queue instead of sending
  - Retry failed sends up to NOTIFICATION_RETRY_ATTEMPTS times
  - Update sent_status, queued, last_sent_at in the reminders table
"""
import logging
import time
from datetime import datetime
from typing import Optional

from config import (
    NOTIFICATION_RETRY_ATTEMPTS,
    NOTIFICATION_RETRY_DELAY_SEC,
    QUIET_HOUR_START,
    QUIET_HOUR_END,
)
from db_engine import get_db
from models import Child, Reminder, Vaccine
from notifications.email_sender import send_email
from notifications.push_sender import send_push
from notifications.sms_sender import send_sms
from notifications.whatsapp_sender import send_whatsapp

logger = logging.getLogger(__name__)


# ─── Message Templates ────────────────────────────────────────

def build_message(reminder_type: str, vaccine_name: str, priority: str) -> str:
    """Return a human-readable notification message."""
    prefix = "🚨 URGENT: " if priority == "urgent" else ""

    templates = {
        "7_day":    f"{prefix}Reminder: Your child needs {vaccine_name} in 7 days. Please plan your clinic visit.",
        "2_day":    f"{prefix}Reminder: Your child needs {vaccine_name} in 2 days. Please visit the hospital soon.",
        "due_today":f"{prefix}Today is vaccination day! Your child's {vaccine_name} is due today. Please visit the hospital.",
        "overdue_3":f"{prefix}Important: {vaccine_name} was due 3 days ago and is overdue. Please visit the hospital immediately.",
        "overdue_7":f"{prefix}URGENT: {vaccine_name} is 7 days overdue. Immediate medical attention required. Visit your healthcare provider now.",
    }
    return templates.get(reminder_type, f"{prefix}Vaccination reminder: {vaccine_name}.")


def build_subject(reminder_type: str, vaccine_name: str) -> str:
    """Return email subject line."""
    subjects = {
        "7_day":    f"Vaccination Reminder — {vaccine_name} in 7 days",
        "2_day":    f"Vaccination Reminder — {vaccine_name} in 2 days",
        "due_today":f"Today: {vaccine_name} Vaccination Due",
        "overdue_3":f"⚠️ Overdue: {vaccine_name} missed 3 days ago",
        "overdue_7":f"🚨 URGENT: {vaccine_name} overdue by 7 days",
    }
    return subjects.get(reminder_type, f"Vaccination Reminder — {vaccine_name}")


# ─── Quiet Hours ──────────────────────────────────────────────

def is_quiet_hour(now: Optional[datetime] = None) -> bool:
    """
    Return True if the current time is inside the quiet window (10 PM – 7 AM).
    During quiet hours, notifications are queued, not sent.
    """
    now = now or datetime.now()
    h = now.hour
    if QUIET_HOUR_START > QUIET_HOUR_END:
        # Window crosses midnight e.g. 22 → 7
        return h >= QUIET_HOUR_START or h < QUIET_HOUR_END
    return QUIET_HOUR_START <= h < QUIET_HOUR_END


# ─── Senders registry ─────────────────────────────────────────

def _dispatch_channel(channel: str, child: Child, message: str, subject: str) -> bool:
    """Call the correct sender for the given channel."""
    if channel == "sms":
        return send_sms(child.phone_number or "", message)
    elif channel == "whatsapp":
        return send_whatsapp(child.phone_number or "", message)
    elif channel == "email":
        return send_email(child.email or "", subject, message)
    elif channel == "push":
        return send_push(child.device_token or "", subject, message)
    else:
        logger.error("Unknown channel: %s", channel)
        return False


# ─── Retry Loop ───────────────────────────────────────────────

def _send_with_retry(channel: str, child: Child, message: str, subject: str) -> bool:
    """Attempt to send with exponential-style retry."""
    for attempt in range(1, NOTIFICATION_RETRY_ATTEMPTS + 1):
        success = _dispatch_channel(channel, child, message, subject)
        if success:
            return True
        if attempt < NOTIFICATION_RETRY_ATTEMPTS:
            delay = NOTIFICATION_RETRY_DELAY_SEC * attempt
            logger.warning(
                "Send failed (attempt %d/%d) via %s for child=%d — retrying in %ds …",
                attempt, NOTIFICATION_RETRY_ATTEMPTS, channel, child.id, delay
            )
            time.sleep(delay)
    logger.error(
        "All %d delivery attempts failed via %s for child=%d.",
        NOTIFICATION_RETRY_ATTEMPTS, channel, child.id
    )
    return False


# ─── Public API ───────────────────────────────────────────────

def dispatch_reminder(reminder: Reminder) -> None:
    """
    Dispatch a single reminder record. Updates sent_status, queued, last_sent_at.
    """
    with get_db() as session:
        reminder = session.merge(reminder)       # attach to this session
        child   = session.get(Child,   reminder.child_id)
        vaccine = session.get(Vaccine, reminder.vaccine_id)

        if not child or not vaccine:
            logger.error("dispatch_reminder: missing child or vaccine for reminder %d", reminder.id)
            return

        message = build_message(reminder.reminder_type, vaccine.name, reminder.priority.value)
        subject = build_subject(reminder.reminder_type, vaccine.name)

        if is_quiet_hour():
            logger.info(
                "Quiet hours active — queuing reminder %d (child=%s vaccine=%s channel=%s)",
                reminder.id, child.name, vaccine.name, reminder.channel
            )
            reminder.queued = True
            return   # session committed by context manager

        success = _send_with_retry(reminder.channel, child, message, subject)
        reminder.sent_status  = success
        reminder.queued       = False
        reminder.last_sent_at = datetime.utcnow()

        if success:
            logger.info(
                "✅ Reminder sent | child=%s vaccine=%s type=%s channel=%s",
                child.name, vaccine.name, reminder.reminder_type, reminder.channel
            )
        else:
            logger.error(
                "❌ Reminder delivery failed | child=%s vaccine=%s type=%s channel=%s",
                child.name, vaccine.name, reminder.reminder_type, reminder.channel
            )


def flush_queued_reminders() -> None:
    """
    Attempt to deliver all previously-queued (unsent) reminders.
    Called at the start of each scheduler run after quiet hours end.
    """
    if is_quiet_hour():
        logger.info("Still in quiet hours — skipping queue flush.")
        return

    with get_db() as session:
        queued = (
            session.query(Reminder)
            .filter(Reminder.queued == True, Reminder.sent_status == False)  # noqa: E712
            .all()
        )

    if not queued:
        return

    logger.info("Flushing %d queued reminders …", len(queued))
    for reminder in queued:
        dispatch_reminder(reminder)
