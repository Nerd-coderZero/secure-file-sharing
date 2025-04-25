# app/email/utils.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

async def send_verification_email(email_to: str, verification_url: str):
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_FROM
    message["To"] = email_to
    message["Subject"] = "Verify your email"
    
    html = f"""
    <html>
    <body>
        <p>Hi,</p>
        <p>Please click the link below to verify your email address:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not register for an account, please ignore this email.</p>
    </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email_to, message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")