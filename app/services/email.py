from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

from app.core.config import settings

def get_email_service() -> EmailService:
    return EmailService()

class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        self.fm = FastMail(self.config)

    async def send_message(self, subject: str, text: str, recipient: str):
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=text,
            subtype="plain"
            )
        
        await self.fm.send_message(message)