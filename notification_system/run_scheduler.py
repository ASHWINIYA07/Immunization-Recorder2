"""
run_scheduler.py — Main entry point for the Immunization Notification System.

Startup sequence:
  1. Load .env configuration
  2. Create all PostgreSQL tables (idempotent)
  3. Sync latest children / vaccines / records from FastAPI backend
  4. Schedule daily reminder job at 7:00 AM
  5. Optionally run the job immediately for testing

Usage:
  cd d:\\iMMunizaTIon\\Immunization-Recorder2\\notification_system
  python run_scheduler.py

  # Run once immediately (for testing, no scheduler loop):
  python run_scheduler.py --run-now
"""
import argparse
import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import SCHEDULER_HOUR, SCHEDULER_MINUTE
from db_engine import create_all_tables
from db_sync import sync_all
from reminder_engine import run_reminder_job

# ─── Logging Setup ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("notification_system.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def startup() -> None:
    """Run all initialization steps before the scheduler starts."""
    logger.info("──────────────────────────────────────────────")
    logger.info(" ImmuniTrack Notification System — Starting Up")
    logger.info("──────────────────────────────────────────────")

    # 1. Ensure PostgreSQL tables exist
    logger.info("Step 1/2 — Creating / verifying database tables …")
    create_all_tables()

    # 2. Sync backend data into PostgreSQL
    logger.info("Step 2/2 — Syncing data from FastAPI backend …")
    sync_all()

    logger.info("Startup complete.")


def start_scheduler() -> None:
    """Start the APScheduler blocking scheduler."""
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    scheduler.add_job(
        func=run_reminder_job,
        trigger=CronTrigger(
            hour=SCHEDULER_HOUR,
            minute=SCHEDULER_MINUTE,
        ),
        id="daily_reminder_job",
        name="Daily Immunization Reminder",
        replace_existing=True,
        misfire_grace_time=3600,   # allow up to 1h late start
    )

    # Also sync backend data daily (5 min before reminders run)
    scheduler.add_job(
        func=sync_all,
        trigger=CronTrigger(
            hour=SCHEDULER_HOUR,
            minute=max(0, SCHEDULER_MINUTE - 5),
        ),
        id="daily_sync_job",
        name="Daily Backend Data Sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    logger.info(
        "Scheduler started — reminder job runs daily at %02d:%02d IST.",
        SCHEDULER_HOUR, SCHEDULER_MINUTE,
    )
    logger.info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ImmuniTrack Notification System"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the reminder job immediately (once) and exit — useful for testing.",
    )
    args = parser.parse_args()

    startup()

    if args.run_now:
        logger.info("--run-now flag detected — running reminder job immediately.")
        run_reminder_job()
        logger.info("Done. Exiting.")
    else:
        start_scheduler()
