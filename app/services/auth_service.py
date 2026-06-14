from app.config import Config
import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow


CREDENTIALS_PATH = Config.CREDENTIALS_FILE
TOKEN_PATH = Config.TOKEN_FILE


class GoogleAuthRequiredException(Exception):
    """Exception raised when Google Calendar authentication is required."""
    def __init__(self, authorization_url):
        self.authorization_url = authorization_url
        super().__init__("Google Calendar authentication required.")


def get_google_flow(user_id="default"):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8501")

    if not client_id or not client_secret:
        raise ValueError(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env"
        )

    client_config = {
        "web": {
            "client_id": client_id,
            "project_id": "smart-timetable-ai",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [redirect_uri],
        }
    }

    return Flow.from_client_config(
        client_config,
        scopes=Config.GOOGLE_SCOPES,
        redirect_uri=redirect_uri
    )


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
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                
                # Save refreshed credentials
                os.makedirs(os.path.dirname(token_path), exist_ok=True)
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
                return creds
            except Exception as e:
                logging.error(f"[GOOGLE AUTH] Failed to refresh token: {e}")
                try:
                    if os.path.exists(token_path):
                        os.remove(token_path)
                except Exception:
                    pass

        logging.info(f"[GOOGLE AUTH] Initiating new OAuth flow for user {user_id}...")
        flow = get_google_flow(user_id)
        flow.code_verifier = "smart_timetable_ai_agent_secret_code_verifier_value_for_pkce_auth_flow_123456789"
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=str(user_id)
        )
        raise GoogleAuthRequiredException(authorization_url)

    return creds
