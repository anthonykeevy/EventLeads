# Email Configuration

## Providers

- SMTP (default for dev): works with MailHog/Mailpit locally
- Postmark or SendGrid (recommended for prod): reliable delivery and templates

## Templates

- Verification Email: subject, body with verify link and expiry notice
- Password Reset: subject, body with reset link and support hint

## Rate Limits

- Resend Cooldown: 60 seconds
- Max Resends/Day: 5 per user

## Bounces & Undeliverables

- Track bounce events (via provider webhooks if available)
- Flag accounts with repeated bounces; show banner to update email

## Security

- Do not include secrets in links; all tokens are one-time and expire in 30–60 min
- Log issuance/consumption; store IP and user agent for auditing

