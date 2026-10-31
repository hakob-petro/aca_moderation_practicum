"""Open Missions 3 and 4 in JupyterLab on a Modal GPU.

    modal run notebook.py
    modal run notebook.py --download

Work is stored in a volume named for your local username. See NOTEBOOK.md.
"""

import getpass
import hashlib
import os
import re
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
NOTEBOOK = "missions_3_4.ipynb"
app = modal.App("aca-s3-notebook")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "torch==2.14.1", "transformers==5.20.2", "jupyterlab==4.4.10",
        "matplotlib==3.10.7", "scikit-learn==1.7.2", "ipywidgets==8.1.7",
    )
    .add_local_file(HERE / NOTEBOOK, f"/opt/course/seminar_3/{NOTEBOOK}")
    .add_local_file(HERE.parent / "data/train.csv", "/opt/course/data/train.csv")
)
for filename in ("scorer.py", "auc.py", "prepare_data.py", "check"):
    image = image.add_local_file(HERE / filename, f"/opt/course/seminar_3/{filename}")
image = image.add_local_dir(HERE / "templates", "/opt/course/seminar_3/templates")


def workspace_name(student: str = "") -> str:
    identity = student or getpass.getuser()
    slug = re.sub(r"[^a-z0-9-]", "-", identity.lower()).strip("-")[:32] or "student"
    suffix = hashlib.sha256(identity.encode()).hexdigest()[:8]
    return f"aca-s3-notebook-{slug}-{suffix}"


@app.function(image=image, gpu="T4", timeout=125 * 60, scaledown_window=2)
def serve(minutes: int):
    import secrets
    import shutil
    import subprocess
    import sys
    import time
    import urllib.request

    work = Path("/root/work")
    s3 = work / "s3"
    s3.mkdir(parents=True, exist_ok=True)
    home_s3 = Path.home() / "s3"
    if not home_s3.exists():
        home_s3.symlink_to(s3, target_is_directory=True)
    if home_s3.resolve() != s3.resolve():
        raise RuntimeError("Expected ~/s3 to point at the notebook workspace")
    notebook = work / NOTEBOOK
    if not notebook.exists():
        shutil.copy2(f"/opt/course/seminar_3/{NOTEBOOK}", notebook)

    token = secrets.token_urlsafe(32)
    volume = modal.Volume.from_name(os.environ["ACA_NOTEBOOK_VOLUME"])
    with modal.forward(8888) as tunnel:
        process = subprocess.Popen(
            [sys.executable, "-m", "jupyterlab", "--no-browser", "--allow-root",
             "--ip=0.0.0.0", "--port=8888", "--ServerApp.port_retries=0",
             "--ServerApp.allow_remote_access=True", "--ServerApp.root_dir=/root/work"],
            cwd=work, env={**os.environ, "JUPYTER_TOKEN": token},
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"Jupyter exited with code {process.returncode}")
                try:
                    request = urllib.request.Request("http://127.0.0.1:8888/api/status",
                                                     headers={"Authorization": f"token {token}"})
                    with urllib.request.urlopen(request, timeout=2) as response:
                        if response.status == 200:
                            break
                except (OSError, TimeoutError):
                    time.sleep(1)
            else:
                raise RuntimeError("Jupyter did not become ready within 90 seconds")
            print(f"\nOpen on your laptop: {tunnel.url}/lab/tree/{NOTEBOOK}?token={token}", flush=True)
            print(f"Workspace: {os.environ['ACA_NOTEBOOK_VOLUME']}", flush=True)
            print(f"GPU is billed while this is running. Save, export, then press Ctrl+C here. Stops after {minutes} minutes.", flush=True)
            try:
                process.wait(timeout=minutes * 60)
            except subprocess.TimeoutExpired:
                print("Session time limit reached. Stopping Jupyter.", flush=True)
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            volume.commit()


@app.local_entrypoint()
def main(student: str = "", minutes: int = 90, gpu: str = "T4", download: bool = False, output_dir: str = ""):
    if download:
        restore_export(student, output_dir)
        return
    if not 1 <= minutes <= 120:
        raise ValueError("Use --minutes between 1 and 120")
    name = workspace_name(student)
    volume = modal.Volume.from_name(name, create_if_missing=True)
    cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
    print(f"Using notebook volume {name}. Restart with the same --student to resume.")
    serve.with_options(gpu=gpu, env={"ACA_NOTEBOOK_VOLUME": name},
                       volumes={"/root/work": volume, "/root/.cache/huggingface": cache}).remote(minutes)


def restore_export(student: str = "", output_dir: str = ""):
    """Restore exported mission files locally, backing up any files they replace."""
    import datetime
    import io
    import shutil
    import zipfile

    name = workspace_name(student)
    volume = modal.Volume.from_name(name)
    out = Path(output_dir).expanduser() if output_dir else Path.home() / "s3"
    allowed = {"m3.txt", "m4.txt", "my_comments.txt", "my_scores.tsv", "baseline.json",
               "baseline_predictions.csv", "data/train.jsonl", "data/dev.jsonl"}
    try:
        payload = b"".join(volume.read_file("notebook-results.zip"))
    except modal.exception.NotFoundError as exc:
        raise RuntimeError("No export yet. Run the notebook's final export cell, save, and stop the session first.") from exc
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if set(archive.namelist()) != allowed or len(archive.namelist()) != len(allowed):
            raise ValueError("Export must contain exactly the eight mission files")
        if sum(info.file_size for info in archive.infolist()) > 30_000_000:
            raise ValueError("Export is unexpectedly large")
        if archive.testzip() is not None:
            raise ValueError("Export ZIP failed its checksum check")
        backup = out / "notebook-backups" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        for member in archive.infolist():
            dest = out / member.filename
            content = archive.read(member)
            if dest.exists() and dest.read_bytes() != content:
                old = backup / member.filename
                old.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, old)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            timestamp = datetime.datetime(*member.date_time).timestamp()
            os.utime(dest, (timestamp, timestamp))
    print(f"Restored eight mission files to {out}")
    if backup.exists():
        print(f"Previous versions saved in {backup}")
    print("From ~/course/seminar_3 run: ./check 3 && ./check 4")
