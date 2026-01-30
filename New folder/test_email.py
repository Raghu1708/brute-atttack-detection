from email_alert import send_email_alert

# Test the email alert function with dummy data
# This should trigger the SMTPAuthenticationError if credentials are invalid
send_email_alert("testuser", "192.168.1.1", "test@example.com")
