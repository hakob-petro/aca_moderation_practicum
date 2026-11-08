"""Small standard-library helpers shared by Seminar 6's commands."""
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

SETUP = Path(os.environ.get("S6_HOME", str(Path.home() / "s6")))
CONSOLE = SETUP / "console"
REDTEAM = SETUP / "redteam"
POOL = Path(os.environ.get("ACA_REDTEAM", "/srv/aca/redteam"))
RULES = ("advertising", "legal")


def env(path=CONSOLE / ".env"):
    return dict(line.split("=", 1) for line in Path(path).read_text().splitlines()
                if line and not line.startswith("#"))


def compose(*args):
    return subprocess.run(["docker", "compose", *args], cwd=CONSOLE, text=True,
                          capture_output=True, check=True).stdout.strip()


def in_console(*args, stdin=None):
    """Run a Python script inside the console container. It prints JSON."""
    done = subprocess.run(["docker", "compose", "exec", "-T", "console", "python", *args],
                          cwd=CONSOLE, input=stdin, text=True, capture_output=True)
    if done.returncode:
        raise SystemExit((done.stderr.strip() or "The console container failed.")[-3000:]
                         + "\nIs it running? cd ~/s6/console && docker compose ps")
    return json.loads(done.stdout)


def status(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except OSError:
        return None


def read_comments(path):
    """Lines like `advertising: text` or `legal: text`. Blank lines and # lines are skipped."""
    items, problems = [], []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rule, colon, comment = line.partition(":")
        rule, comment = rule.strip().lower(), comment.strip()
        if not colon or rule not in RULES:
            problems.append(f"line {number}: start it with 'advertising:' or 'legal:'")
        elif not 10 <= len(comment) <= 500:
            problems.append(f"line {number}: the comment needs 10 to 500 characters")
        else:
            items.append({"rule": rule, "comment": comment})
    return items, problems
