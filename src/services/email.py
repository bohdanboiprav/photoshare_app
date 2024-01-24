from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Contact System",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(
    email: EmailStr, username: str, host: str, type: str | None = None
):
    """
    The send_email function sends an email to the user with a link to verify their account.
        Args:
            - email (str): The user's email address.
            - username (str): The username of the user who is registering for an account.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Pass the hostname of the server
    :param type: str | None: Determine the type of email to be sent
    :return: A coroutine object
    """
    temp_name = "verify_email.html"
    subj = "Confirm your email "
    if type == "reset_password":
        subj = "Reset password"
        temp_name = "reset_password.html"
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject=subj,
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)

        await fm.send_message(message, template_name=temp_name)
    except ConnectionErrors as err:
        print(err, "=============================")
