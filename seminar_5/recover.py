"""Clone committed source into a fresh folder, start a second Compose project,
call it, remove it. This is a redeployment drill on the SAME host, not a new VM.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from common import SETUP, config, compose, env, http, SAMPLE

work = Path(config()["gateway"]).resolve()
settings = env()


def git(*args, cwd=work):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


root = Path(git("rev-parse", "--show-toplevel")).resolve()
relative = work.relative_to(root)
if git("status", "--porcelain", "--", "."):
    raise SystemExit("Commit the deployment folder first (mission 4). No files were changed.")
tracked = git("ls-files", "-z").split("\0")
if ".env" in tracked or not {"app.py", "compose.yml"} <= set(tracked):
    raise SystemExit("Track the code, and leave .env ignored, before this drill.")
for filename in filter(None, tracked):
    content = (work / filename).read_bytes()
    if any(settings[key].encode() in content for key in ("MODEL_KEY", "GATEWAY_KEY")):
        raise SystemExit("A private key is in tracked code. Remove it and rotate it before continuing.")
commit = git("rev-parse", "HEAD")
project = "s5-recovery-" + str(os.getuid())
report = {"commit": commit, "answered": False, "removed": False, "same_host": True}
target_port = int(settings["PORT"]) + 1
with tempfile.TemporaryDirectory(prefix="recovery-", dir=SETUP) as folder:
    clone = Path(folder) / "repo"
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(root), str(clone)], check=True)
    assert git("rev-parse", "HEAD", cwd=clone) == commit
    target = clone / relative
    shutil.copy(work / ".env", target / ".env")
    os.chmod(target / ".env", 0o600)
    settings["PORT"] = str(target_port)
    (target / ".env").write_text("".join(f"{k}={v}\n" for k, v in settings.items()))
    print(f"Fresh clone: {clone}; commit {commit[:12]}; port {target_port}", flush=True)
    try:
        compose("-p", project, "up", "--build", "-d", "--wait", "--wait-timeout", "60", work=target)
        status, body = http(f"http://127.0.0.1:{target_port}/moderate", settings["GATEWAY_KEY"], SAMPLE)
        assert status == 200 and body.get("decision") in {"approve", "review", "remove"}, body
        report["answered"] = True
        report["decision"] = body["decision"]
        print("PASS  fresh deployment returned a real model decision")
    finally:
        compose("-p", project, "down", work=target)
        remaining = subprocess.check_output(["docker", "ps", "-aq", "--filter",
            f"label=com.docker.compose.project={project}"], text=True).strip()
        report["removed"] = not bool(remaining)
        (SETUP / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
print("Recovery containers, copied key file and temporary clone removed. Original deployment is still running.")
