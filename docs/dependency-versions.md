# Dependency Versions (Recommended Pinning)

Pin dependencies to stable minor series and review quarterly. Suggested baselines:

- Python: 3.11
- FastAPI: ~=0.111
- SQLAlchemy: ~=2.0
- Alembic: ~=1.13
- Pydantic: ~=2.7
- Uvicorn: ~=0.30
- Stripe: ~=10.0 (Python SDK)
- Email: `postmarker` or `sendgrid` latest stable; or SMTP via `smtplib`

Record exact pins in `requirements.txt` or `pyproject.toml` per your stack.

