import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email_alert(username, ip, recipient_email):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Email credentials not set. Skipping email alert.")
        return

    subject = "🚨 Brute Force Attack Detected"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = f"""
    ALERT: Brute Force Attack Detected!

    Username: {username}
    IP Address: {ip}
    Time: {time_now}

    Immediate action required.
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(os.getenv("EMAIL_HOST", "smtp.gmail.com"), int(os.getenv("EMAIL_PORT", 587)))
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Email alert sent successfully.")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication failed. Please check your EMAIL_USER and EMAIL_PASSWORD environment variables. For Gmail, use an app password instead of your regular password.")
    except Exception as e:
        print(f"Failed to send email alert: {e}")
