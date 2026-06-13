from app.config import Config
import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


CREDENTIALS_PATH = Config.CREDENTIALS_FILE
TOKEN_PATH = Config.TOKEN_FILE


def authenticate_google(user_id="default"):
    creds = None
    token_path = f"credentials/token_{user_id}.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, Config.GOOGLE_SCOPES)

    if not creds or not creds.valid:
        logging.info(
            f"\n[GOOGLE AUTH] Credentials invalid or missing for user {user_id}. Attempting to refresh or re-authenticate..."
        )
        if creds and creds.expired and creds.refresh_token:
            logging.info(f"[GOOGLE AUTH] Refreshing expired token for user {user_id}...")
            from google.auth.transport.requests import Request

            creds.refresh(Request())
        else:
            logging.info(f"[GOOGLE AUTH] Initiating new OAuth flow for user {user_id}...")
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise ValueError(
                    "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env"
                )

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "project_id": "smart-timetable-ai",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": ["http://localhost"],
                }
            }

            flow = InstalledAppFlow.from_client_config(
                client_config, Config.GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Ensure credentials directory exists
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds
