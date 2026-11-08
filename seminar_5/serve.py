"""Deploy with: modal deploy serve.py. First run ./prepare.

The public URL exposes vLLM's OpenAI-compatible API. VLLM_API_KEY is supplied
as a Modal Secret, never as a command-line argument or part of the image.
"""
import json
import os
from pathlib import Path

import modal

SETUP = Path(os.environ.get("S5_HOME", str(Path.home() / "s5")))
config = json.loads((SETUP / "serve.json").read_text() if modal.is_local() else os.environ["S5_CONFIG"])
if modal.is_local():
    # Seconds without requests before the GPU is released. Seminar 6's console
    # is used with pauses, so it deploys with ACA_SCALEDOWN=1200 for the class.
    config["scaledown"] = int(os.environ.get("ACA_SCALEDOWN", "60"))
    if not 60 <= config["scaledown"] <= 1200:
        raise SystemExit("ACA_SCALEDOWN must be between 60 and 1200 seconds")
app = modal.App(config["app"])
image = (modal.Image.debian_slim(python_version="3.12").pip_install("vllm==0.32.0")
         .env({"S5_CONFIG": json.dumps(config)}))
weights = modal.Volume.from_name(config["volume"])
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
secret_values = (dict(line.split("=", 1) for line in (SETUP / "model.env").read_text().splitlines() if line)
                 if modal.is_local() else {"VLLM_API_KEY": os.environ["VLLM_API_KEY"]})
# The same Secret dependency must exist when Modal imports this module remotely;
# Modal injects its values into the container before importing this module.
secrets = [modal.Secret.from_dict(secret_values)]


@app.function(
    image=image,
    gpu=os.environ.get("ACA_GPU", "L4,A10").split(","),
    volumes={"/weights": weights, "/root/.cache/huggingface": cache},
    secrets=secrets,
    timeout=600,
    scaledown_window=config.get("scaledown", 60),
    max_containers=1,
)
@modal.concurrent(max_inputs=16)
@modal.web_server(8000, startup_timeout=600)
def model():
    import hashlib
    import socket
    import subprocess
    import time

    for name, expected in config["sha256"].items():
        actual = hashlib.sha256((Path("/weights/adapter") / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError("Adapter changed; rerun ./prepare with a new snapshot name")
    process = subprocess.Popen([
        "vllm", "serve", "Qwen/Qwen3-0.6B",
        "--revision", "c1899de289a04d12100db370d81485cdf75e47ca",
        "--host", "0.0.0.0", "--port", "8000",
        "--served-model-name", "base",
        "--enable-lora", "--lora-modules", "moderator=/weights/adapter",
        "--max-lora-rank", "8",
        "--dtype", "half", "--max-model-len", "4096",
        "--gpu-memory-utilization", "0.50", "--max-num-seqs", "16",
        "--enforce-eager", "--attention-backend", "FLASH_ATTN", "--generation-config", "vllm",
        "--logprobs-mode", "processed_logprobs", "--max-logprobs", "2",
    ])
    # Detect a bad CLI flag or crashed engine immediately instead of making the
    # caller wait for the entire web-server startup timeout. Request-body logging
    # is disabled by default in this pinned vLLM release.
    deadline = time.monotonic() + 540
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"vLLM exited during startup (code {process.returncode}); see its logs")
        try:
            with socket.create_connection(("127.0.0.1", 8000), timeout=1):
                return
        except OSError:
            time.sleep(1)
    process.terminate()
    raise TimeoutError("vLLM did not become ready within nine minutes")
