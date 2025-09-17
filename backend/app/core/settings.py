import os
from dotenv import load_dotenv

# Load environment variables from .env.dev, overriding existing ones
# The .env.dev file is in the project root, which is 3 levels up from this file
env_path = os.path.join(os.path.dirname(__file__), '../../../.env.dev')
load_dotenv(dotenv_path=env_path, override=True)

# Also try loading from project root as fallback
root_env_path = os.path.join(os.path.dirname(__file__), '../../.env.dev')
load_dotenv(dotenv_path=root_env_path, override=True)


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL", "mssql+pyodbc://localhost/master?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )
        self.jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret")
        self.allowed_origins: list[str] = (
            os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        )
        # Ensure localhost:3000 is always included for development
        if "http://localhost:3000" not in self.allowed_origins:
            self.allowed_origins.append("http://localhost:3000")

        # Email/SMTP config
        self.smtp_host: str = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "1025"))
        self.smtp_user: str = os.getenv("SMTP_USER", "")
        self.smtp_password: str = os.getenv("SMTP_PASSWORD", "")
        self.email_from: str = os.getenv("EMAIL_FROM", "dev@example.com")


settings = Settings()
