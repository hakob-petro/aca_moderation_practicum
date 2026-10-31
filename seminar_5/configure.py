"""Save the deployed model URL without displaying either private API key."""
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from common import config, env

url = sys.argv[1].rstrip("/") if len(sys.argv) == 2 else ""
parts = urlsplit(url)
if parts.scheme != "https" or not parts.hostname or parts.username or parts.query or parts.fragment:
    sys.exit("Usage: python3 configure.py https://THE-PRINTED-MODAL-URL")
if not url.endswith("/v1"):
    url += "/v1"
path = Path(config()["gateway"]) / ".env"
settings = env(path)
settings["MODEL_URL"] = url
os.chmod(path, 0o600)
path.write_text("".join(f"{key}={value}\n" for key, value in settings.items()))
print(f"Saved MODEL_URL in {path}; keys unchanged.")
