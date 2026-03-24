"""
sms_sender.py — Send SMS notifications via Twilio.

Usage:
    from notifications.sms_sender import send_sms
    send_sms("+919876543210", "Reminder: Your child needs Penta-1 in 2 days.")
"""
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE

logger = logging.getLogger(__name__)

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise RuntimeError(
                "Twilio credentials not configured. "
                "Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
            )
        _client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return _client


def send_sms(to_number: str, message: str) -> bool:
    """
    Send an SMS message.

    Args:
        to_number: Recipient phone in E.164 format, e.g. "+919876543210"
        message:   Message body text.

    Returns:
        True on success, False on failure.
    """
    if not to_number:
        logger.warning("send_sms called with empty to_number — skipping.")
        return False

    try:
        client = _get_client()
        msg = client.messages.create(
            body=message,
            from_=TWILIO_FROM_PHONE,
            to=to_number,
        )
        logger.info("SMS sent to %s | SID=%s", to_number, msg.sid)
        return True
    except TwilioRestException as exc:
        logger.error("Twilio SMS error to %s: %s", to_number, exc)
        return False
    except Exception as exc:
        logger.error("Unexpected SMS error to %s: %s", to_number, exc)
        return False
