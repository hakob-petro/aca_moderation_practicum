"""Score comments on a Modal GPU.

    modal run modal_score.py --comment "Buy followers cheap at example.com"
    modal run modal_score.py --comment "Can my landlord keep my deposit?" --rule legal
    modal run modal_score.py --file ~/s3/my_comments.txt
    modal run modal_score.py --dev

The same as score.py, which runs on this machine instead. ./score picks the
right one for you. How the model judges a comment: scorer.py.

The prompts are built here, on your server. Only the model runs on Modal: it
receives the prompts, and sends back one score per prompt.
"""

import os
from pathlib import Path

import modal

import scorer

# The first GPU type in this list that Modal has free right now. ACA_GPU=T4 (say)
# asks for one type only; ACA_GPU=none runs on Modal's CPUs, for testing, slowly.
GPU = os.environ.get("ACA_GPU", "L4,A10,T4")
GPUS = None if GPU == "none" else GPU.split(",") if "," in GPU else GPU

app = modal.App("aca-score")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("torch==2.14.1", "transformers==5.20.2")
    .add_local_file(Path(__file__).with_name("scorer.py"), "/root/scorer.py")
)
# The model's weights are downloaded once and kept here, so later runs start faster.
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.cls(
    gpu=GPUS,
    image=image,
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=900,
    scaledown_window=60,  # the GPU machine shuts down after a minute without work
)
class RemoteScorer:
    @modal.enter()
    def load(self):
        """Runs once when the GPU machine starts: load the model onto the GPU."""
        self.model = scorer.Scorer()
        hf_cache.commit()

    @modal.method()
    def score(self, chats: list[list[dict]]) -> list[float]:
        return self.model.score(chats)

    @modal.method()
    def prompt(self, chat: list[dict]) -> str:
        return self.model.prompt(chat)

    @modal.method()
    def device(self) -> str:
        return self.model.device_name()


@app.local_entrypoint()
def main(comment: str = "", rule: str = "advertising", file: str = "", dev: bool = False, show_prompt: bool = False):
    remote = RemoteScorer()
    scorer.run(
        remote.score.remote,
        remote.prompt.remote,
        ran_on=f"Modal ({remote.device.remote()})",
        comment=comment,
        rule=rule,
        file=file,
        dev=dev,
        want_prompt=show_prompt,
    )
