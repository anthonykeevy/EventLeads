import os
import smtplib
from email.message import EmailMessage

# Set the same environment variables the backend uses
os.environ["SMTP_HOST"] = "localhost"
os.environ["SMTP_PORT"] = "1025"
os.environ["EMAIL_FROM"] = "dev@example.com"

def test_smtp():
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0") or 0)
    sender = os.getenv("EMAIL_FROM", "dev@example.com")
    
    print(f"Testing SMTP: {host}:{port}")
    print(f"Sender: {sender}")
    
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = "test@example.com"
        msg["Subject"] = "Test Email"
        msg.set_content("This is a test email.")
        
        with smtplib.SMTP(host, port) as s:
            s.send_message(msg)
        print("SUCCESS: Email sent to MailHog!")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    test_smtp()


