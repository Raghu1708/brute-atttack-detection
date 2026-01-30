from twilio.rest import Client
from datetime import datetime
import os

def send_whatsapp_alert(username, ip, recipient_phone):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')

    if not account_sid or not auth_token or not twilio_phone:
        print("Twilio credentials not set. Skipping WhatsApp alert.")
        return

    twilio_whatsapp_number = f"whatsapp:{twilio_phone}"

    client = Client(account_sid, auth_token)

    message_body = f"🚨 Brute Force Attack Detected!\nUsername: {username}\nIP Address: {ip}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nImmediate action required."

    try:
        message = client.messages.create(
            body=message_body,
            from_=twilio_whatsapp_number,
            to=f'whatsapp:{recipient_phone}'
        )
        print(f"WhatsApp message sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp alert: {e}")
