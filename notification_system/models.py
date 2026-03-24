"""
models.py — SQLAlchemy ORM models for the notification system.

Tables: children, vaccines, vaccination_records, reminders
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    ForeignKey, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from db_engine import Base


# ─── Python Enums (mirror PostgreSQL ENUMs) ───────────────────

class VaccineStatus(str, enum.Enum):
    done     = "done"
    upcoming = "upcoming"
    overdue  = "overdue"


class ReminderPriority(str, enum.Enum):
    normal = "normal"
    urgent = "urgent"


# ─── ORM Models ───────────────────────────────────────────────

class Child(Base):
    __tablename__ = "children"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(Text, nullable=False)
    dob          = Column(Date, nullable=False)
    phone_number = Column(Text, nullable=True)
    email        = Column(Text, nullable=True)
    device_token = Column(Text, nullable=True)
    created_at   = Column(DateTime, nullable=False, default=datetime.utcnow)

    records   = relationship("VaccinationRecord", back_populates="child", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="child", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Child id={self.id} name={self.name!r} dob={self.dob}>"


class Vaccine(Base):
    __tablename__ = "vaccines"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(Text, nullable=False, unique=True)
    due_days = Column(Integer, nullable=False)

    records   = relationship("VaccinationRecord", back_populates="vaccine")
    reminders = relationship("Reminder", back_populates="vaccine")

    def __repr__(self):
        return f"<Vaccine id={self.id} name={self.name!r} due_days={self.due_days}>"


class VaccinationRecord(Base):
    __tablename__ = "vaccination_records"
    __table_args__ = (
        UniqueConstraint("child_id", "vaccine_id", name="uq_child_vaccine"),
    )

    id         = Column(Integer, primary_key=True, index=True)
    child_id   = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_id = Column(Integer, ForeignKey("vaccines.id",  ondelete="CASCADE"), nullable=False)
    status     = Column(SAEnum(VaccineStatus, name="vaccine_status", create_type=False),
                        nullable=False, default=VaccineStatus.upcoming)
    taken_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    child   = relationship("Child",   back_populates="records")
    vaccine = relationship("Vaccine", back_populates="records")

    def __repr__(self):
        return (f"<VaccinationRecord child={self.child_id} "
                f"vaccine={self.vaccine_id} status={self.status}>")


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        UniqueConstraint(
            "child_id", "vaccine_id", "reminder_type", "channel",
            name="uq_reminder_child_vaccine_type_channel"
        ),
    )

    id            = Column(Integer, primary_key=True, index=True)
    child_id      = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_id    = Column(Integer, ForeignKey("vaccines.id",  ondelete="CASCADE"), nullable=False)
    reminder_type = Column(String(20), nullable=False)   # 7_day | 2_day | due_today | overdue_3 | overdue_7
    reminder_date = Column(DateTime, nullable=False)
    sent_status   = Column(Boolean, nullable=False, default=False)
    channel       = Column(String(20), nullable=False)   # sms | whatsapp | email | push
    priority      = Column(SAEnum(ReminderPriority, name="reminder_priority", create_type=False),
                           nullable=False, default=ReminderPriority.normal)
    queued        = Column(Boolean, nullable=False, default=False)
    last_sent_at  = Column(DateTime, nullable=True)

    child   = relationship("Child",   back_populates="reminders")
    vaccine = relationship("Vaccine", back_populates="reminders")

    def __repr__(self):
        return (f"<Reminder child={self.child_id} vaccine={self.vaccine_id} "
                f"type={self.reminder_type} channel={self.channel} sent={self.sent_status}>")
