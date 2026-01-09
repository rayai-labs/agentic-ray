"""Platform API configuration constants."""

import os
from importlib.metadata import version
from pathlib import Path

# Production: uncomment before deploying
# PLATFORM_API_URL = os.environ.get("RAYAI_API_URL", "https://api.rayai.com")
# Local development:
PLATFORM_API_URL = os.environ.get("RAYAI_API_URL", "http://localhost:8000")
RAYAI_CONFIG_DIR = Path.home() / ".rayai"
CREDENTIALS_FILE = RAYAI_CONFIG_DIR / "credentials.json"
USER_AGENT = f"rayai-cli/{version('rayai')}"
DEFAULT_TIMEOUT = 30  # seconds
DEVICE_POLL_INTERVAL = 5  # seconds
