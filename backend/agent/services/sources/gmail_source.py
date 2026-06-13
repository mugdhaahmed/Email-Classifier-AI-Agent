import os
import base64
from pathlib import Path
from email.utils import parsedate_to_datetime

from decouple import config
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from agent.services.sources.base import EmailSource

# Read-only access only. If this scope changes, re-run
# `python manage.py gmail_auth` so the new scope is granted.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Standard Google OAuth token endpoint (used for headless refresh).
TOKEN_URI = 'https://oauth2.googleapis.com/token'

# backend/ root, used to resolve relative credential/token paths.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _resolve(path_value: str) -> Path:
    """Resolve a configured path relative to the backend root if not absolute."""
    p = Path(path_value)
    return p if p.is_absolute() else (BASE_DIR / p)


class GmailSource(EmailSource):
    """
    Fetches unread emails from a real Gmail account via the Gmail API.

    Credentials are resolved in this order (first match wins):
      1. Environment variables — GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET,
         GMAIL_REFRESH_TOKEN. Preferred for deployment (Render, Docker); no
         files on disk.
      2. token.json file — written by `python manage.py gmail_auth`. Convenient
         for local development.

    Either way, the one-time browser consent is performed by `gmail_auth`,
    which mints the refresh token. At runtime this class is fully headless.
    """

    def __init__(self):
        self.query = config('GMAIL_QUERY', default='is:unread')
        self.max_results = config('GMAIL_MAX_RESULTS', default=10, cast=int)
        self.token_path = _resolve(config('GMAIL_TOKEN_PATH', default='token.json'))
        self._service = None

    def _load_credentials(self) -> Credentials:
        """Build OAuth credentials from env vars if present, else token.json."""
        client_id = config('GMAIL_CLIENT_ID', default=None)
        client_secret = config('GMAIL_CLIENT_SECRET', default=None)
        refresh_token = config('GMAIL_REFRESH_TOKEN', default=None)

        if client_id and client_secret and refresh_token:
            # Pure env-var path — no files needed.
            return Credentials(
                token=None,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri=TOKEN_URI,
                scopes=SCOPES,
            )

        if os.path.exists(self.token_path):
            return Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        raise RuntimeError(
            "No Gmail credentials found. Either set GMAIL_CLIENT_ID, "
            "GMAIL_CLIENT_SECRET and GMAIL_REFRESH_TOKEN in your environment, "
            f"or run `python manage.py gmail_auth` to create {self.token_path}."
        )

    def _get_service(self):
        """Build (and cache) an authenticated Gmail API service client."""
        if self._service is not None:
            return self._service

        creds = self._load_credentials()

        # Refresh the access token transparently using the stored refresh token.
        if not creds.valid and creds.refresh_token:
            creds.refresh(Request())
            # Persist the refreshed token only when using the file-based path.
            if os.path.exists(self.token_path):
                with open(self.token_path, 'w', encoding='utf-8') as token_file:
                    token_file.write(creds.to_json())

        self._service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        return self._service

    def fetch(self) -> list[dict]:
        service = self._get_service()

        listing = service.users().messages().list(
            userId='me',
            q=self.query,
            maxResults=self.max_results,
        ).execute()

        messages = listing.get('messages', [])
        normalized = []

        for meta in messages:
            full = service.users().messages().get(
                userId='me',
                id=meta['id'],
                format='full',
            ).execute()
            normalized.append(self._normalize(full))

        return normalized

    def _normalize(self, message: dict) -> dict:
        """Convert a raw Gmail message into the shared normalized email shape."""
        payload = message.get('payload', {})
        headers = {h['name'].lower(): h['value'] for h in payload.get('headers', [])}

        received_at = ''
        date_header = headers.get('date')
        if date_header:
            try:
                received_at = parsedate_to_datetime(date_header).isoformat()
            except (TypeError, ValueError):
                received_at = ''

        return {
            'email_id': message.get('id', ''),
            'sender': headers.get('from', 'Unknown Sender'),
            'subject': headers.get('subject', '(No Subject)'),
            'body': self._extract_body(payload) or message.get('snippet', ''),
            'received_at': received_at,
        }

    def _extract_body(self, payload: dict) -> str:
        """
        Recursively walk the MIME tree and return the first text/plain body.
        Returns an empty string if none is found (caller falls back to snippet).
        """
        mime_type = payload.get('mimeType', '')
        body = payload.get('body', {})

        if mime_type == 'text/plain' and body.get('data'):
            return self._decode(body['data'])

        for part in payload.get('parts', []) or []:
            text = self._extract_body(part)
            if text:
                return text

        return ''

    @staticmethod
    def _decode(data: str) -> str:
        """Decode Gmail's URL-safe base64 body data into text."""
        return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8', errors='replace')
