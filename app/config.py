import os

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


class Config:
    # Database
    DB_PATH = os.getenv("DB_PATH", "data/database.db")

    # Time and Locale
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

    # Google Calendar API
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    TOKEN_FILE = "credentials/token.json"
    CREDENTIALS_FILE = "credentials/credentials.json"

    # Defaults
    DEFAULT_STUDY_HOURS = 5.0

    # Groq API
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
