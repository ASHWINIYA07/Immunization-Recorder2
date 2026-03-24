"""
push_sender.py — Send push notifications via an HTTP POST API.

This is a production-ready integration point. Set PUSH_API_URL in .env
to point at your push notification service (e.g., Firebase FCM, OneSignal).

Usage:
    from notifications.push_sender import send_push
    send_push("device_token_xyz", "Vaccination Reminder", "Due today!")
"""
import logging
import requests
from requests.exceptions import RequestException

from config import PUSH_API_URL

logger = logging.getLogger(__name__)

_TIMEOUT = 10  # seconds


def send_push(device_token: str, title: str, body: str) -> bool:
    """
    Send a push notification to a device.

    Args:
        device_token: FCM / APNS device token string.
        title:        Notification title.
        body:         Notification body text.

    Returns:
        True on success, False on failure.
    """
    if not device_token:
        logger.warning("send_push called with empty device_token — skipping.")
        return False

    if not PUSH_API_URL:
        logger.error("PUSH_API_URL not configured — cannot send push notification.")
        return False

    payload = {
        "device_token": device_token,
        "title":        title,
        "body":         body,
        "sound":        "default",
        "priority":     "high",
    }

    try:
        resp = requests.post(PUSH_API_URL, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        logger.info(
            "Push sent to token …%s | Response: %s",
            device_token[-6:], resp.status_code
        )
        return True
    except RequestException as exc:
        logger.error("Push notification failed for token …%s: %s",
                     device_token[-6:], exc)
        return False
    except Exception as exc:
        logger.error("Unexpected push error: %s", exc)
        return False
