"""
api_client.py — HTTP client for the existing FastAPI backend.

Wraps GET /children, GET /schedule/{child_id}, POST /update-vaccine.
All functions raise on HTTP errors and return parsed JSON dicts.
"""
import logging
from typing import Any, Dict, List, Optional

import requests

from config import API_BASE_URL

logger = logging.getLogger(__name__)

_SESSION = requests.Session()
_SESSION.headers.update({"Content-Type": "application/json"})
_TIMEOUT = 15  # seconds


class APIError(RuntimeError):
    """Raised when a backend API call fails."""
    pass


def _get(path: str, **params) -> Any:
    url = f"{API_BASE_URL}{path}"
    try:
        resp = _SESSION.get(url, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("GET %s failed: %s", url, exc)
        raise APIError(f"GET {url} failed: {exc}") from exc


def _post(path: str, payload: Dict) -> Any:
    url = f"{API_BASE_URL}{path}"
    try:
        resp = _SESSION.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("POST %s failed: %s", url, exc)
        raise APIError(f"POST {url} failed: {exc}") from exc


# ─── Public API ───────────────────────────────────────────────

def get_children() -> List[Dict]:
    """
    GET /children
    Returns a list of child dicts with keys:
      id, name, dob, phone_number, email, device_token
    """
    data = _get("/children")
    if isinstance(data, dict) and "children" in data:
        return data["children"]
    if isinstance(data, list):
        return data
    logger.warning("Unexpected /children response shape: %s", data)
    return []


def get_schedule(child_id: int) -> List[Dict]:
    """
    GET /schedule/{child_id}
    Returns a list of vaccine schedule entries:
      { vaccine, due_date, status, taken, taken_date (optional) }
    """
    data = _get(f"/schedule/{child_id}")
    if isinstance(data, dict) and "schedule" in data:
        return data["schedule"]
    if isinstance(data, list):
        return data
    logger.warning("Unexpected /schedule/%s response shape: %s", child_id, data)
    return []


def update_vaccine(child_id: int, vaccine_name: str, taken_date: Optional[str] = None) -> Dict:
    """
    POST /update-vaccine
    Marks a vaccine as done for the given child.
    """
    payload: Dict[str, Any] = {
        "child_id": child_id,
        "vaccine": vaccine_name,
    }
    if taken_date:
        payload["taken_date"] = taken_date
    return _post("/update-vaccine", payload)
