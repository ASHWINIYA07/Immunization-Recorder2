"""
test_reminder_engine.py — Unit tests for reminder engine logic.

Tests run without any database or network connections.
Run with: pytest tests/test_reminder_engine.py -v
"""
import sys
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import notification_system modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from reminder_engine import compute_reminder_types
from models import VaccineStatus
from notifications.dispatcher import is_quiet_hour, build_message, build_subject


# ─── compute_reminder_types ───────────────────────────────────

class TestComputeReminderTypes:
    """Tests for the core date-diff → reminder type logic."""

    def _due(self, days_from_today: int) -> date:
        """Helper: due_date = today + days_from_today."""
        return date.today() + timedelta(days=days_from_today)

    def test_7_day_reminder(self):
        types = compute_reminder_types(
            self._due(7), date.today(), VaccineStatus.upcoming
        )
        assert "7_day" in types

    def test_2_day_reminder(self):
        types = compute_reminder_types(
            self._due(2), date.today(), VaccineStatus.upcoming
        )
        assert "2_day" in types

    def test_due_today_reminder(self):
        types = compute_reminder_types(
            self._due(0), date.today(), VaccineStatus.upcoming
        )
        assert "due_today" in types

    def test_overdue_3_reminder(self):
        types = compute_reminder_types(
            self._due(-3), date.today(), VaccineStatus.overdue
        )
        assert "overdue_3" in types

    def test_overdue_7_reminder(self):
        types = compute_reminder_types(
            self._due(-7), date.today(), VaccineStatus.overdue
        )
        assert "overdue_7" in types

    def test_overdue_7_not_triggered_if_done(self):
        """If vaccine is already done, overdue reminders should NOT be created."""
        types = compute_reminder_types(
            self._due(-7), date.today(), VaccineStatus.done
        )
        assert "overdue_7" not in types

    def test_overdue_3_not_triggered_if_done(self):
        types = compute_reminder_types(
            self._due(-3), date.today(), VaccineStatus.done
        )
        assert "overdue_3" not in types

    def test_no_reminder_for_non_milestone_day(self):
        """Day 5 before due is not a milestone — no reminders."""
        types = compute_reminder_types(
            self._due(5), date.today(), VaccineStatus.upcoming
        )
        assert types == []

    def test_no_reminder_day_after_due_not_matching(self):
        """Day -1 (1 day overdue) is not a milestone."""
        types = compute_reminder_types(
            self._due(-1), date.today(), VaccineStatus.overdue
        )
        assert types == []

    def test_multiple_reminders_possible(self):
        """If both 7_day and 2_day accidentally share a date, only the matching one fires."""
        # This verifies that compute_reminder_types uses exact equality
        types_7 = compute_reminder_types(self._due(7), date.today(), VaccineStatus.upcoming)
        types_2 = compute_reminder_types(self._due(2), date.today(), VaccineStatus.upcoming)
        assert "7_day" in types_7
        assert "7_day" not in types_2


# ─── Quiet Hours ──────────────────────────────────────────────

class TestQuietHours:
    """Tests for is_quiet_hour() with mocked datetime.now()."""

    def _mock_now(self, hour: int):
        from datetime import datetime
        return datetime(2026, 3, 23, hour, 0, 0)

    def test_22_is_quiet(self):
        assert is_quiet_hour(self._mock_now(22)) is True

    def test_23_is_quiet(self):
        assert is_quiet_hour(self._mock_now(23)) is True

    def test_midnight_is_quiet(self):
        assert is_quiet_hour(self._mock_now(0)) is True

    def test_3am_is_quiet(self):
        assert is_quiet_hour(self._mock_now(3)) is True

    def test_7am_is_not_quiet(self):
        assert is_quiet_hour(self._mock_now(7)) is False

    def test_12pm_is_not_quiet(self):
        assert is_quiet_hour(self._mock_now(12)) is False

    def test_21_is_not_quiet(self):
        assert is_quiet_hour(self._mock_now(21)) is False

    def test_6am_is_quiet(self):
        assert is_quiet_hour(self._mock_now(6)) is True


# ─── Message Building ─────────────────────────────────────────

class TestMessageBuilding:
    def test_overdue_7_includes_urgent(self):
        msg = build_message("overdue_7", "Penta-1", "urgent")
        assert "URGENT" in msg
        assert "Penta-1" in msg

    def test_overdue_3_normal_alert(self):
        msg = build_message("overdue_3", "BCG", "normal")
        assert "BCG" in msg
        assert "URGENT" not in msg

    def test_due_today_message(self):
        msg = build_message("due_today", "Polio 1", "normal")
        assert "today" in msg.lower()
        assert "Polio 1" in msg

    def test_7_day_subject(self):
        subj = build_subject("7_day", "MMR 1")
        assert "7 days" in subj
        assert "MMR 1" in subj

    def test_overdue_7_subject_urgent(self):
        subj = build_subject("overdue_7", "DTP 1")
        assert "URGENT" in subj or "overdue" in subj.lower()


# ─── Escalation ───────────────────────────────────────────────

class TestEscalation:
    def test_overdue_7_priority_is_urgent(self):
        from reminder_engine import _priority_for
        from models import ReminderPriority
        assert _priority_for("overdue_7") == ReminderPriority.urgent

    def test_overdue_3_priority_is_normal(self):
        from reminder_engine import _priority_for
        from models import ReminderPriority
        assert _priority_for("overdue_3") == ReminderPriority.normal

    def test_7_day_priority_is_normal(self):
        from reminder_engine import _priority_for
        from models import ReminderPriority
        assert _priority_for("7_day") == ReminderPriority.normal
