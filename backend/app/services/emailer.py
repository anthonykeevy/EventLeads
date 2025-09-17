import os
import smtplib
from email.message import EmailMessage


def _try_smtp_send(to: str, subject: str, body: str) -> tuple[bool, str]:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0") or 0)
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_SENDER") or os.getenv("EMAIL_FROM", user or "no-reply@example.com")
    
    if not host or not port:
        return False, f"SMTP configuration missing: host={host}, port={port}"
    
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(host, port) as s:
            if user and pwd:
                s.starttls()
                s.login(user, pwd)
            s.send_message(msg)
        return True, "Email sent successfully via SMTP"
    except Exception as e:
        return False, f"SMTP send failed: {str(e)}"


def send_email(to: str, subject: str, body: str) -> None:
    # Try SMTP; else print to stdout (dev)
    success, message = _try_smtp_send(to, subject, body)
    if success:
        print(f"[EMAIL][SUCCESS] {message}")
        return
    
    # SMTP failed - log the error and fallback to console
    print(f"[EMAIL][ERROR] {message}")
    print(f"[EMAIL][FALLBACK] To: {to}")
    print(f"[EMAIL][FALLBACK] Subject: {subject}")
    print(f"[EMAIL][FALLBACK] Body: {body}")

