"""Email delivery via SMTP (stdlib `smtplib`, offloaded to a thread since
it's a blocking API)."""

import asyncio
import smtplib
from email.message import EmailMessage

import structlog

from config import get_settings
from notifications.channels.base import NotificationChannel
from notifications.events import NotificationMessage

logger = structlog.get_logger(__name__)


class EmailChannel(NotificationChannel):
    name = "email"

    async def send(self, message: NotificationMessage) -> bool:
        settings = get_settings()
        if not (settings.smtp_host and settings.notify_email_from and settings.notify_email_to):
            return False

        email_message = EmailMessage()
        email_message["Subject"] = message.title
        email_message["From"] = settings.notify_email_from
        email_message["To"] = settings.notify_email_to
        email_message.set_content(message.body)

        try:
            await asyncio.to_thread(self._send_sync, email_message, settings)
            return True
        except (OSError, smtplib.SMTPException):
            logger.warning(
                "email_notification_failed", notification_event=message.event.value, exc_info=True
            )
            return False

    @staticmethod
    def _send_sync(email_message: EmailMessage, settings) -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(email_message)
