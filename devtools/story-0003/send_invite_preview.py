import sys
from pathlib import Path
from sqlalchemy import text

# Ensure backend app is importable
repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.db import engine  # type: ignore
from app.services.settings_service import settings_service  # type: ignore
from app.services.emailer import send_email  # type: ignore


def main() -> None:
    # Pick inviter display name if possible
    inviter_name = "Admin"
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT TOP 1 COALESCE(FirstName+' '+LastName, Username, Email) FROM [User] ORDER BY UserID DESC"
                )
            ).first()
            inviter_name = (row or ["Admin"])[0] or "Admin"
    except Exception:
        pass

    ttl_hours = settings_service.get_invite_token_ttl_hours()
    accept_url = "http://localhost:3000/invite/accept?token=PREVIEW_TOKEN"

    plain = (
        f"{inviter_name} invited you to join Event Leads.\n\n"
        f"Click the invitation link below to set your password and join: \n{accept_url}\n\n"
        f"This invitation is valid for {ttl_hours} hours. If it expires, please ask {inviter_name} to resend it."
    )
    html = f"""
    <html>
      <body style=\"font-family:Segoe UI, Arial, sans-serif; color:#1f2937;\">
        <h2 style=\"color:#111827;\">You're invited to Event Leads</h2>
        <p>
          <strong>{inviter_name}</strong> has invited you to join
          <strong>Event Leads</strong> for their organisation.
        </p>
        <p>
          When you click the button below, you'll be prompted to set your password before entering the site.
        </p>
        <p>
          <a href=\"{accept_url}\" style=\"background:#2563eb;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;display:inline-block;\">Accept Invitation</a>
        </p>
        <p style=\"margin-top:16px;\">
          This invitation is valid for <strong>{ttl_hours} hours</strong>. If the link has expired, please reach out to {inviter_name} to send a new invitation.
        </p>
        <hr style=\"margin:20px 0;border:none;border-top:1px solid #e5e7eb;\" />
        <p style=\"font-size:12px;color:#6b7280;\">
          If the button doesn't work, paste this link in your browser:<br/>
          <span style=\"word-break:break-all;\">{accept_url}</span>
        </p>
      </body>
    </html>
    """
    send_email(to="mailhog@example.com", subject="You're invited to Event Leads (Preview)", body=plain, html_body=html)
    print({"sent": True, "to": "mailhog@example.com", "ttl_hours": ttl_hours, "inviter": inviter_name})


if __name__ == "__main__":
    main()
