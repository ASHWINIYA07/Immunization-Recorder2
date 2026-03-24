"""
config.py — Centralized configuration loader.

Reads all settings from environment variables (with .env file support).
Copy .env.example to .env and fill in your credentials before running.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this file
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _require(key: str) -> str:
    """Return env var or raise a descriptive error."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {key}. "
            f"Copy .env.example to .env and fill in your credentials."
        )
    return value


# ─── Database ─────────────────────────────────────────────────
DB_URL: str = os.getenv(
    "DB_URL",
    "postgresql://postgres:postgres123@localhost:5432/immunization_db"
)

# ─── FastAPI Backend ───────────────────────────────────────────
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

# ─── Twilio ───────────────────────────────────────────────────
TWILIO_ACCOUNT_SID: str  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_PHONE: str   = os.getenv("TWILIO_FROM_PHONE", "")
TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# ─── Email (Gmail SMTP) ────────────────────────────────────────
SMTP_HOST: str       = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int       = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str       = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str   = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")

# ─── Push API ─────────────────────────────────────────────────
PUSH_API_URL: str = os.getenv("PUSH_API_URL", "")

# ─── Scheduler ────────────────────────────────────────────────
SCHEDULER_HOUR: int   = int(os.getenv("SCHEDULER_HOUR", "7"))
SCHEDULER_MINUTE: int = int(os.getenv("SCHEDULER_MINUTE", "0"))

# ─── Quiet Hours ──────────────────────────────────────────────
QUIET_HOUR_START: int = int(os.getenv("QUIET_HOUR_START", "22"))  # 10 PM
QUIET_HOUR_END: int   = int(os.getenv("QUIET_HOUR_END", "7"))     # 7 AM

# ─── Notification Retry ───────────────────────────────────────
NOTIFICATION_RETRY_ATTEMPTS: int = int(os.getenv("NOTIFICATION_RETRY_ATTEMPTS", "3"))
NOTIFICATION_RETRY_DELAY_SEC: int = int(os.getenv("NOTIFICATION_RETRY_DELAY_SEC", "5"))
