"""Fine-tune Qwen3-0.6B with LoRA on your train split, then score your dev split.

    modal run train.py                                 your setting (printed at the start)
    modal run train.py --lr 2e-4 --epochs 2 --data half  any setting you like

Everything heavy runs on a Modal GPU:
  1. `swift sft` (ms-swift) trains a LoRA adapter on ~/s3/data/train.jsonl:
     each comment's prompt, with "Yes" or "No" as the answer to learn;
  2. the adapter goes into your Modal volume aca-models, under runs/RUN_NAME;
  3. the model with the adapter scores ~/s3/data/dev.jsonl, exactly like
     ./score --dev in Seminar 3.
Results: ~/s4/results/RUN_NAME.json and RUN_NAME_predictions.csv.

--data half trains on a random half of your training comments (the same half
for everyone), to see how much the amount of data matters.

--only legal (or advertising) trains on that rule's comments alone. The dev
AUC of the other rule then shows how the model does on a rule it never saw.
"""

import getpass
import hashlib
import os
import json
import random
import sys
import time
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "seminar_3"))
import scorer  # noqa: E402  the prompts, exactly as in Seminar 3

# Every student gets one of these settings, picked from their username, so
# that the class tries all of them: learning rate, epochs, how much data.
SETTINGS = [(lr, epochs, data) for data in ("all", "half") for epochs in (1, 2) for lr in (5e-5, 1e-4, 2e-4, 4e-4)]

app = modal.App("aca-train")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "torch==2.14.1",
        # ms-swift 4.6 needs transformers below 5.20, peft below 0.21 and trl below 1.0.
        "transformers==5.19.0",
        "peft==0.20.0",
        "trl==0.29.1",
        "accelerate==1.15.0",
        "ms-swift==4.6.0",
    )
    .env({"USE_HF": "1"})  # download models from Hugging Face, not ModelScope
    .add_local_file(HERE.parent / "seminar_3" / "scorer.py", "/root/scorer.py")
)
models = modal.Volume.from_name("aca-models", create_if_missing=True)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.function(
    # The first one Modal has free. No T4: it would take about 15 minutes.
    gpu=os.environ.get("ACA_GPU", "L4,A10,L40S").split(","),
    image=image,
    volumes={"/models": models, "/root/.cache/huggingface": hf_cache},
    timeout=40 * 60,
)
def train(run: str, rows: list[dict], dev_chats: list[list[dict]], lr: float, epochs: int) -> dict:
    import shutil
    import subprocess

    import torch

    gpu = torch.cuda.get_device_name(0)
    bf16 = torch.cuda.get_device_capability(0)[0] >= 8  # L4, A10, L40S: yes
    with open("/tmp/train.jsonl", "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    command = [
        "swift", "sft",
        "--model", scorer.MODEL, "--model_revision", scorer.REVISION,
        "--tuner_type", "lora", "--lora_rank", "8", "--lora_alpha", "32", "--target_modules", "all-linear",
        "--dataset", "/tmp/train.jsonl",
        "--num_train_epochs", str(epochs), "--learning_rate", str(lr),
        "--per_device_train_batch_size", "8", "--gradient_accumulation_steps", "2",
        "--max_length", "1024", "--torch_dtype", "bfloat16" if bf16 else "float16",
        "--output_dir", "/tmp/out", "--add_version", "false",
        "--save_strategy", "epoch", "--save_only_model", "true",
        "--logging_steps", "10", "--report_to", "none", "--seed", "42",
    ]
    print("$ " + " ".join(command), flush=True)
    start = time.time()
    subprocess.run(command, check=True)
    train_seconds = time.time() - start
    hf_cache.commit()

    # The last checkpoint holds the finished adapter: keep it in the volume.
    last = max(Path("/tmp/out").glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    target = Path("/models/runs") / run
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    for name in ("adapter_config.json", "adapter_model.safetensors"):
        shutil.copy(last / name, target / name)
    models.commit()

    model = scorer.Scorer(adapter=str(target))
    start = time.time()
    scores = model.score(dev_chats)
    return {"gpu": gpu, "train_seconds": round(train_seconds), "score_seconds": round(time.time() - start), "scores": scores}


def training_rows(train: list[dict], data: str, only: str = "") -> list[dict]:
    """One training conversation per comment: the Seminar 3 prompt, and the answer to learn."""
    if only:
        train = [r for r in train if scorer.SHORT_NAME.get(r["rule"]) == only]
    rows = [
        {"messages": scorer.build_chat(r["rule"], r["body"], r, r["subreddit"])
                     + [{"role": "assistant", "content": "Yes" if r["rule_violation"] else "No"}]}
        for r in train
    ]
    random.Random(42).shuffle(rows)
    return rows[: len(rows) // 2] if data == "half" else rows


@app.local_entrypoint()
def main(lr: float = 0.0, epochs: int = 0, data: str = "", only: str = ""):
    sys.path.insert(0, str(HERE.parent / "seminar_3"))
    from auc import column_averaged_auc

    folder_in = Path.home() / "s3" / "data"
    if not (folder_in / "dev.jsonl").exists():
        sys.exit("No train/dev split yet. Run:  python3 ~/course/seminar_3/prepare_data.py")
    train_rows = [json.loads(line) for line in (folder_in / "train.jsonl").open(encoding="utf-8")]
    dev_rows = [json.loads(line) for line in (folder_in / "dev.jsonl").open(encoding="utf-8")]

    user = getpass.getuser()
    my_lr, my_epochs, my_data = SETTINGS[int(hashlib.sha256(user.encode()).hexdigest(), 16) % len(SETTINGS)]
    lr = lr or my_lr
    epochs = epochs or my_epochs
    data = data or my_data
    if data not in ("all", "half"):
        sys.exit("--data is all or half")
    if only not in ("", "advertising", "legal"):
        sys.exit("--only is advertising or legal")
    run = f"lr{lr:g}-ep{epochs}-{data}" + (f"-only-{only}" if only else "")

    rows = training_rows(train_rows, data, only)
    dev_chats = [scorer.build_chat(r["rule"], r["body"], r, r["subreddit"]) for r in dev_rows]
    print(f"Setting: learning rate {lr:g}, {epochs} epoch(s), {data} of the training comments"
          + (f", {only} comments only" if only else ""))
    print(f"Training on {len(rows)} comments; then scoring {len(dev_rows)} dev comments. Run name: {run}")

    out = train.remote(run, rows, dev_chats, lr, epochs)

    results = [
        {"row_id": r["row_id"], "rule": scorer.SHORT_NAME.get(r["rule"], r["rule"]), "label": r["rule_violation"], "score": s}
        for r, s in zip(dev_rows, out["scores"])
    ]
    mean, per_rule = column_averaged_auc(results)
    folder = Path.home() / "s4" / "results"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f"{run}_predictions.csv").open("w", encoding="utf-8") as f:
        f.write("row_id,rule,label,score\n")
        for r in results:
            f.write(f"{r['row_id']},{r['rule']},{r['label']},{r['score']:.6f}\n")
    summary = {
        "student": user,
        "run": run,
        "learning_rate": lr,
        "epochs": epochs,
        "data": data,
        "only": only or None,
        "training_comments": len(rows),
        "gpu": out["gpu"],
        "train_seconds": out["train_seconds"],
        "auc": round(mean, 4),
        "auc_per_rule": {k: round(v, 4) for k, v in per_rule.items()},
        "adapter": f"aca-models volume: runs/{run}",
    }
    (folder / f"{run}.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"\nTrained in {out['train_seconds'] // 60} min {out['train_seconds'] % 60} s on {out['gpu']}.")
    for name, v in per_rule.items():
        print(f"  AUC {name:<12} {v:.3f}")
    print(f"  AUC averaged over the two rules: {mean:.3f}   (the untrained model: 0.487)")
    print(f"Saved to {folder / (run + '.json')}; the adapter is in your Modal volume aca-models, runs/{run}")
