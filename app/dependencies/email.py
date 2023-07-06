from email.message import EmailMessage
from ..config import EMAIL_SENDER, EMAIL_PASSWORD
import ssl
import smtplib

def send_email(email_receiver: str, email_subject: str, body: str):
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = email_receiver
    em["Subject"] = email_subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, email_receiver, em.as_string())