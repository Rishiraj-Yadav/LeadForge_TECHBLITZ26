"""SendGrid email service."""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME

    async def send_email(self, to_email: str, subject: str, html_content: str) -> int:
        message = Mail(
            from_email=(self.from_email, self.from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        response = self.client.send(message)
        logger.info(f"Email sent to {to_email} with status {response.status_code}")
        return response.status_code


def get_email_service() -> EmailService:
    return EmailService()
