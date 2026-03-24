"""
email_sender.py — Send email notifications via Gmail SMTP (TLS).

Usage:
    from notifications.email_sender import send_email
    send_email(
        to_email="parent@example.com",
        subject="Vaccination Reminder",
        body="Reminder: Your child's Penta-1 is due in 2 days."
    )
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SMTP_FROM_EMAIL, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send a plain-text email via SMTP.

    Args:
        to_email: Recipient email address.
        subject:  Email subject.
        body:     Plain-text email body.

    Returns:
        True on success, False on failure.
    """
    if not to_email:
        logger.warning("send_email called with empty to_email — skipping.")
        return False

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP credentials not configured — cannot send email.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"]    = SMTP_FROM_EMAIL or SMTP_USER
    msg["To"]      = to_email
    msg["Subject"] = subject

    # Plain-text part
    msg.attach(MIMEText(body, "plain"))

    # HTML part — add a minimal styled wrapper
    html_body = f"""
    <html>
      <body style="font-family:Arial,sans-serif;color:#333;padding:20px;">
        <div style="max-width:520px;margin:auto;border:1px solid #e0e0e0;
                    border-radius:8px;padding:24px;">
          <h2 style="color:#1565c0;">💉 Immunization Reminder</h2>
          <p style="font-size:15px;line-height:1.6;">{body}</p>
          <hr style="border:none;border-top:1px solid #eee;margin:16px 0;" />
          <p style="font-size:12px;color:#888;">
            This is an automated reminder from ImmuniTrack.
            Please visit your nearest healthcare provider.
          </p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(msg["From"], to_email, msg.as_string())
        logger.info("Email sent to %s | Subject: %s", to_email, subject)
        return True
    except smtplib.SMTPAuthenticationError as exc:
        logger.error("SMTP authentication failed: %s", exc)
        return False
    except smtplib.SMTPException as exc:
        logger.error("SMTP error sending to %s: %s", to_email, exc)
        return False
    except Exception as exc:
        logger.error("Unexpected email error to %s: %s", to_email, exc)
        return False
