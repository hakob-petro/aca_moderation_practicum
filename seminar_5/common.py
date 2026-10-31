"""Small standard-library helpers shared by the classroom commands."""
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

SETUP = Path(os.environ.get("S5_HOME", str(Path.home() / "s5")))


def config():
    return json.loads((SETUP / "serve.json").read_text())


def env(path=None):
    path = Path(path) if path else Path(config()["gateway"]) / ".env"
    return dict(line.split("=", 1) for line in path.read_text().splitlines()
                if line and not line.startswith("#"))


def http(url, key="", body=None, timeout=30):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                     headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        try:
            data = json.load(error)
        except (ValueError, UnicodeError):
            data = {"detail": f"HTTP {error.code}"}
        return error.code, data


def compose(*args, work=None):
    return subprocess.check_output(["docker", "compose", *args],
        cwd=work or config()["gateway"], text=True).strip()


SAMPLE = {"rule": "advertising", "comment": "Get 1000 Instagram followers for $5 at example.com"}
