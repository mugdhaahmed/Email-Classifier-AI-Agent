import os
import json
from pathlib import Path

from agent.services.sources.base import EmailSource


class MockJSONSource(EmailSource):
    """
    Reads emails from the static mock_emails.json file.

    Mandatory for credential-free testing: lets the full pipeline run without
    connecting to a real inbox. Records already match the normalized shape.
    """

    def __init__(self):
        # backend/agent/services/sources/mock_source.py -> backend/
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.mock_data_path = base_dir / 'agent' / 'data' / 'mock_emails.json'

    def fetch(self) -> list[dict]:
        if not os.path.exists(self.mock_data_path):
            print(f"[MOCK SOURCE] Data file missing at {self.mock_data_path}.")
            return []

        with open(self.mock_data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
