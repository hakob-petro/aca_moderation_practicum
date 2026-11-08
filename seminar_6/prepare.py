"""Seminar 6 setup: copy the console starter to ~/s6/console and connect it to your gateway.

It reads your Seminar 5 gateway's settings, finds the Docker network of its
running container, copies the labelled training comments (the console's
memory) and the dev comments (its inbox), and writes the console's private
settings. Running it again keeps your files and changes nothing.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from common import CONSOLE, REDTEAM, SETUP

HERE = Path(__file__).resolve().parent
S5 = Path(os.environ.get("S5_HOME", str(Path.home() / "s5")))
S3_DATA = Path.home() / "s3" / "data"
sys.path.insert(0, str(HERE.parent / "seminar_3"))
from scorer import SHORT_NAME  # noqa: E402  the two rules' full texts → advertising, legal


def private_write(path, content):
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as out:
        out.write(content)


def gateway_network():
    """The Docker network of the running Seminar 5 gateway."""
    if not (S5 / "serve.json").exists():
        sys.exit("No Seminar 5 setup in ~/s5. Finish Seminar 5's missions 1 and 2 first.")
    gateway = Path(json.loads((S5 / "serve.json").read_text())["gateway"])
    settings = dict(line.split("=", 1) for line in (gateway / ".env").read_text().splitlines() if line)
    cid = subprocess.run(["docker", "compose", "ps", "-q", "gateway"], cwd=gateway, text=True,
                         capture_output=True).stdout.strip()
    if not cid:
        sys.exit(f"Your gateway is not running. Start it, then run ./prepare again:\n"
                 f"  cd {gateway} && docker compose up -d")
    info = json.loads(subprocess.check_output(["docker", "inspect", cid]))[0]
    networks = sorted(info["NetworkSettings"]["Networks"])
    return settings, networks[0], int(settings["PORT"])


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    if (CONSOLE / ".env").exists():
        print(f"Already prepared: {CONSOLE}. Your edits and settings were kept.")
        return
    if CONSOLE.exists() and any(CONSOLE.iterdir()):
        sys.exit(f"{CONSOLE} already contains files but no .env; move it away, then run ./prepare again")
    settings, network, gateway_port = gateway_network()
    if not (S3_DATA / "dev.jsonl").exists():
        subprocess.run([sys.executable, str(HERE.parent / "seminar_3" / "prepare_data.py")], check=True)
    port = int(os.environ["MYPORT"]) + 4 if "MYPORT" in os.environ else gateway_port + 2

    SETUP.mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copytree(HERE / "console", CONSOLE, dirs_exist_ok=True)
    (CONSOLE / "data").mkdir(exist_ok=True)
    read = lambda name: [json.loads(line) for line in open(S3_DATA / name, encoding="utf-8")]
    # Memory: the labelled training comments. Inbox: the dev comments, labels kept for evaluate.py.
    write_jsonl(CONSOLE / "data" / "cases.jsonl", [
        {"rule": SHORT_NAME[r["rule"]], "comment": r["body"], "label": r["rule_violation"],
         "source": "the course data"} for r in read("train.jsonl")])
    write_jsonl(CONSOLE / "data" / "inbox.jsonl", [
        {"row_id": r["row_id"], "rule": SHORT_NAME[r["rule"]], "comment": r["body"],
         "label": r["rule_violation"]} for r in read("dev.jsonl")])
    private_write(CONSOLE / ".env", f"PORT={port}\nGATEWAY_URL=http://gateway:8000\n"
                  f"GATEWAY_KEY={settings['GATEWAY_KEY']}\nGATEWAY_NETWORK={network}\nPRECEDENT_AT=0.85\n")
    REDTEAM.mkdir(exist_ok=True)
    print(f"Prepared {CONSOLE}: memory of {len(read('train.jsonl'))} labelled comments, "
          f"an inbox of {len(read('dev.jsonl'))}.")
    print(f"Console port {port}; gateway network {network}; your gateway key was copied, not printed.")
    print("Next: mission 1, step 2.")


if __name__ == "__main__":
    main()
