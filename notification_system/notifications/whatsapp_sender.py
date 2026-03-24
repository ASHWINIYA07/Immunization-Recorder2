"""
whatsapp_sender.py — Send WhatsApp notifications via Twilio WhatsApp API.

Supports both Twilio Sandbox ("whatsapp:+14155238886") and production senders.

Usage:
    from notifications.whatsapp_sender import send_whatsapp
    send_whatsapp("+919876543210", "Reminder: Vaccination due today!")
"""
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

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


def _to_whatsapp(phone: str) -> str:
    """Normalise a phone number to Twilio WhatsApp format."""
    phone = phone.strip()
    if phone.startswith("whatsapp:"):
        return phone
    if not phone.startswith("+"):
        phone = "+" + phone
    return f"whatsapp:{phone}"


def send_whatsapp(to_number: str, message: str) -> bool:
    """
    Send a WhatsApp message via Twilio.

    Args:
        to_number: Recipient phone in E.164 format, e.g. "+919876543210"
        message:   Message body text.

    Returns:
        True on success, False on failure.
    """
    if not to_number:
        logger.warning("send_whatsapp called with empty to_number — skipping.")
        return False

    to_wa   = _to_whatsapp(to_number)
    from_wa = TWILIO_WHATSAPP_FROM

    if not from_wa:
        logger.error("TWILIO_WHATSAPP_FROM not configured — cannot send WhatsApp.")
        return False

    try:
        client = _get_client()
        msg = client.messages.create(
            body=message,
            from_=from_wa,
            to=to_wa,
        )
        logger.info("WhatsApp sent to %s | SID=%s", to_wa, msg.sid)
        return True
    except TwilioRestException as exc:
        logger.error("Twilio WhatsApp error to %s: %s", to_wa, exc)
        return False
    except Exception as exc:
        logger.error("Unexpected WhatsApp error to %s: %s", to_wa, exc)
        return False
