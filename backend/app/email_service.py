import logging
import smtplib
from email.message import EmailMessage
from fastapi import BackgroundTasks
from .config import settings


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.smtp_host or not settings.smtp_sender:
        # Graceful no-op when SMTP is not configured
        logging.info("SMTP not configured; skipping email to %s with subject '%s'", to_email, subject)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port or 25) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password or "")
        server.send_message(message)


def send_registration_email(background_tasks: BackgroundTasks, to_email: str, subject: str, body: str) -> None:
    # Run email sending outside the request/response flow
    background_tasks.add_task(_send_email, to_email, subject, body)
