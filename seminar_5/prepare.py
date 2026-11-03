"""Local setup only: snapshot an adapter, create private keys, copy the starter."""
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil

import modal

app = modal.App("aca-s5-prepare")
HERE = Path(__file__).resolve().parent
SETUP = Path(os.environ.get("S5_HOME", str(Path.home() / "s5")))


def private_write(path, content):
    # Create with restrictive permissions before writing a single byte.
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as out:
        out.write(content)


@app.local_entrypoint()
def main(run: str = "", student: str = "", workdir: str = "", port: int = 0):
    SETUP.mkdir(parents=True, exist_ok=True, mode=0o700)
    existing = SETUP / "serve.json"
    if existing.exists():
        print(f"Already prepared: {existing}. Your edits and keys were kept.")
        print(f"Gateway: {json.loads(existing.read_text())['gateway']}")
        print("Continue with modal deploy serve.py. Use a separate S5_HOME for a different snapshot.")
        return
    runs = {p.stem: json.loads(p.read_text()) for p in (Path.home() / "s4/results").glob("*.json")}
    if not run:
        if not runs:
            raise SystemExit("No Seminar 4 run found. Train first, or ask the instructor for a RUN and use --run RUN.")
        run = max(runs, key=lambda name: runs[name].get("auc", 0))
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", run):
        raise SystemExit("RUN must be a directory name, without slashes")
    work = (Path(workdir).expanduser() if workdir else SETUP / "gateway").resolve()
    if work.exists() and any(work.iterdir()):
        raise SystemExit(f"{work} already contains files; choose an empty --workdir PATH")
    port = port or (int(os.environ["MYPORT"]) + 2 if "MYPORT" in os.environ else 18082)
    if not 1024 <= port <= 65534:
        raise SystemExit("Use an unprivileged port between 1024 and 65534")
    identity = student or getpass.getuser()
    slug = re.sub(r"[^a-z0-9-]", "-", identity.lower())[:22].strip("-") or "student"
    suffix = hashlib.sha256(identity.encode()).hexdigest()[:8]
    name = f"aca-s5-{slug}-{suffix}"
    adapter = SETUP / "adapter"
    adapter.mkdir(exist_ok=True)
    source = modal.Volume.from_name("aca-models")
    hashes = {}
    for filename in ("adapter_config.json", "adapter_model.safetensors"):
        destination = adapter / filename
        with destination.open("wb") as out:
            for chunk in source.read_file(f"runs/{run}/{filename}"):
                out.write(chunk)
        hashes[filename] = hashlib.sha256(destination.read_bytes()).hexdigest()
    snapshot_name = name + "-" + hashes["adapter_model.safetensors"][:8]
    snapshot = modal.Volume.from_name(snapshot_name, create_if_missing=True)
    with snapshot.batch_upload(force=True) as upload:
        upload.put_directory(adapter, "/adapter")
    work.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HERE / "gateway", work, dirs_exist_ok=True)
    shutil.copy(HERE.parent / "seminar_3/scorer.py", work / "scorer.py")
    model_key, gateway_key = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    private_write(SETUP / "model.env", f"VLLM_API_KEY={model_key}\n")
    private_write(work / ".env", f"PORT={port}\nMODEL_URL=https://REPLACE-ME/v1\n"
        f"MODEL_KEY={model_key}\nGATEWAY_KEY={gateway_key}\nMODEL_NAME=moderator\n"
        "MODEL_TIMEOUT=15\nAPPROVE_BELOW=0.30\nREMOVE_AT=0.80\n")
    config = {"app": name, "volume": snapshot_name, "run": run, "sha256": hashes,
              "gateway": str(work), "student": identity, "port": port}
    existing.write_text(json.dumps(config, indent=2) + "\n")
    print(f"Prepared {run}; adapter SHA-256 {hashes['adapter_model.safetensors']}")
    print(f"App: {name}; hash-checked snapshot: {snapshot_name}")
    print(f"Gateway starter: {work}; keys saved privately, not printed.")
    print("Next: modal deploy serve.py, then python3 configure.py https://THE-PRINTED-URL")
