"""A Python session on a Modal GPU, with PyTorch, transformers and the model ready.

    modal shell explore.py
    python3

The machine has a T4 GPU, the same packages as modal_score.py, the model's
weights in the hf-cache volume, and scorer.py, so `import scorer` gives you
the same prompts as ./score.

It is billed while it is open, idle or not. Leave with exit() and then exit;
it stops by itself after 45 minutes at the latest.
"""

from pathlib import Path

import modal

app = modal.App("aca-explore")
# The same image as modal_score.py, so Modal reuses it instead of building another.
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("torch==2.14.1", "transformers==5.20.2")
    .add_local_file(Path(__file__).with_name("scorer.py"), "/root/scorer.py")
)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


# A shell takes one GPU type, not a list: T4 is the one Modal most often has free.
@app.function(gpu="T4", image=image, volumes={"/root/.cache/huggingface": hf_cache}, timeout=45 * 60)
def explore():
    """`modal shell explore.py` opens a terminal on this function's machine."""
