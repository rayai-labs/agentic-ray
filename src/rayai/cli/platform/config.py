"""Platform API configuration constants."""

import os
from importlib.metadata import version
from pathlib import Path

PLATFORM_API_URL = os.environ.get("RAYAI_API_URL", "https://api.rayai.com")
RAYAI_CONFIG_DIR = Path.home() / ".rayai"
CREDENTIALS_FILE = RAYAI_CONFIG_DIR / "credentials.json"
USER_AGENT = f"rayai-cli/{version('rayai')}"
DEFAULT_TIMEOUT = 30  # seconds
DEVICE_POLL_INTERVAL = 5  # seconds
