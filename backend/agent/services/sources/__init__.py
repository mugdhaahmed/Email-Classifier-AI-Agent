from decouple import config

from agent.services.sources.base import EmailSource
from agent.services.sources.mock_source import MockJSONSource


def get_email_source() -> EmailSource:
    """
    Factory that selects the active email ingestion source.

    MOCK_MODE=True  -> MockJSONSource (reads mock_emails.json, no credentials)
    MOCK_MODE=False -> GmailSource    (reads real unread Gmail)

    GmailSource is imported lazily so mock mode never requires the Google
    client libraries or a token to be present.
    """
    mock_mode = config('MOCK_MODE', default=True, cast=bool)

    if mock_mode:
        return MockJSONSource()

    from agent.services.sources.gmail_source import GmailSource
    return GmailSource()
