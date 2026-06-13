import os

from django.core.management.base import BaseCommand, CommandError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agent.services.sources.gmail_source import SCOPES, TOKEN_URI, _resolve


class Command(BaseCommand):
    help = "Run the one-time Gmail OAuth flow and print/save the refresh token."

    def handle(self, *args, **options):
        from decouple import config

        client_id = config('GMAIL_CLIENT_ID', default=None)
        client_secret = config('GMAIL_CLIENT_SECRET', default=None)
        credentials_path = _resolve(config('GMAIL_CREDENTIALS_PATH', default='credentials.json'))
        token_path = _resolve(config('GMAIL_TOKEN_PATH', default='token.json'))

        # Prefer env-var client config; fall back to a credentials.json file.
        if client_id and client_secret:
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": TOKEN_URI,
                    "redirect_uris": ["http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            self.stdout.write("Using GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET from environment.")
        elif os.path.exists(credentials_path):
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            self.stdout.write(f"Using OAuth client file at {credentials_path}.")
        else:
            raise CommandError(
                "No OAuth client config found. Either set GMAIL_CLIENT_ID and "
                "GMAIL_CLIENT_SECRET in your .env, or download the OAuth client "
                f"JSON to {credentials_path}."
            )

        self.stdout.write("Opening browser for Google authentication...")
        creds = flow.run_local_server(port=0)

        # Save token.json for the local file-based path.
        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())

        # Confirm which account was authorized.
        try:
            service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'unknown')
        except Exception:
            email = 'unknown'

        self.stdout.write(self.style.SUCCESS(f"\nAuthentication successful for {email}."))
        self.stdout.write(f"Token also saved to {token_path}.\n")
        self.stdout.write(self.style.WARNING(
            "For env-var / deployment use, add this to your .env (no files needed):"
        ))
        self.stdout.write("-" * 60)
        self.stdout.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        self.stdout.write("-" * 60)
        self.stdout.write(
            "\nThen set MOCK_MODE=False and restart the server to ingest real Gmail."
        )
