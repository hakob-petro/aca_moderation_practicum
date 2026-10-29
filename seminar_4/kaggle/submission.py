"""Scores the competition's test comments with Qwen3-0.6B and your LoRA adapter.

This runs on Kaggle, with the GPU on and the internet off: Kaggle runs it
again on its hidden test set when you submit, and scores submission.csv.
kaggle_prepare copies it into ~/s4/kaggle/notebook. The prompt is the one
your model was trained with (Seminar 3's scorer.py).
"""

import glob
import json
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import torch
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer

SYSTEM = "You are a moderator of an online community. You decide whether a comment breaks the community's rule."


def build_chat(rule: str, comment: str, examples: dict | None = None, subreddit: str = "") -> list[dict]:
    """Exactly as in Seminar 3's scorer.py: the prompt the model was trained on."""
    lines = []
    if subreddit:
        lines.append(f"Community: r/{subreddit}")
    lines.append(f"Rule: {rule}")
    if examples:
        lines += [
            "",
            "Comments that break the rule:",
            f"- {examples['positive_example_1']}",
            f"- {examples['positive_example_2']}",
            "",
            "Comments that follow the rule:",
            f"- {examples['negative_example_1']}",
            f"- {examples['negative_example_2']}",
        ]
    lines += [
        "",
        "Comment to judge:",
        comment,
        "",
        "Does the comment to judge break the rule? Answer Yes or No.",
    ]
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(lines)}]


def add_lora(model, adapter_dir: str) -> None:
    """Folds the adapter into the model: each layer's weights W become W + B·A·(alpha/r).

    That is all a LoRA adapter is: for each layer, two thin matrices A and B,
    whose product is a small change to the layer's weights. (peft does the
    same; Kaggle's copy of peft clashes with another package there.)
    """
    config = json.load(open(os.path.join(adapter_dir, "adapter_config.json")))
    scale = config["lora_alpha"] / config["r"]
    weights = load_file(os.path.join(adapter_dir, "adapter_model.safetensors"))
    params = dict(model.named_parameters())
    changed = 0
    for name, A in weights.items():
        if ".lora_A." not in name:
            continue
        B = weights[name.replace(".lora_A.", ".lora_B.")]
        # base_model.model.model.layers.0.mlp.down_proj.lora_A.weight -> model.layers.0.mlp.down_proj.weight
        W = params[name.replace("base_model.model.", "", 1).replace(".lora_A.weight", ".weight")]
        with torch.no_grad():
            W += (B.to(W.device).float() @ A.to(W.device).float() * scale).to(W.dtype)
        changed += 1
    print(f"Adapter folded into {changed} weight matrices")


def find_folder(file_name: str, path_contains: str = "") -> str:
    """Kaggle mounts inputs under /kaggle/input: find the folder that holds a file."""
    for path in glob.glob(f"/kaggle/input/**/{file_name}", recursive=True):
        if path_contains.lower() in path.lower():
            return os.path.dirname(path)
    raise SystemExit(f"Cannot find {file_name} under /kaggle/input: is it added to the notebook?")


def load(model_dir: str, adapter_dir: str, device: str):
    """The model on one GPU, with the adapter folded in."""
    # bfloat16 on GPUs built for it; Kaggle's T4s use float16.
    dtype = torch.bfloat16 if torch.cuda.get_device_capability(device)[0] >= 8 else torch.float16
    model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=dtype).to(device).eval()
    add_lora(model, adapter_dir)
    return model


def score(model, tokenizer, texts: list[str], device: str, yes: int, no: int) -> list[float]:
    """logit(Yes) - logit(No) for every prompt, in batches of similar length."""
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    scores = [0.0] * len(texts)
    for begin in range(0, len(order), 32):
        idx = order[begin : begin + 32]
        batch = tokenizer([texts[i] for i in idx], return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            logits = model(**batch, logits_to_keep=1).logits[:, -1, :].float()
        for i, s in zip(idx, (logits[:, yes] - logits[:, no]).tolist()):
            scores[i] = s
    return scores


def main() -> None:
    start = time.time()
    data_dir = find_folder("test.csv", "jigsaw")
    model_dir = find_folder("config.json", "qwen")
    adapter_dir = find_folder("adapter_config.json")
    print("test:", data_dir, "| model:", model_dir, "| adapter:", adapter_dir)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    tokenizer.padding_side = "left"
    [yes] = tokenizer.encode("Yes", add_special_tokens=False)
    [no] = tokenizer.encode("No", add_special_tokens=False)

    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    texts = [
        tokenizer.apply_chat_template(
            build_chat(row["rule"], row["body"], row, row["subreddit"]),
            tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )
        for row in test.to_dict("records")
    ]

    # Kaggle gives two GPUs: a copy of the model on each scores half the comments,
    # both at once. A GPU works while Python waits, so two threads are enough.
    # On the hidden test this took Kaggle 20 minutes instead of 42.
    devices = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
    models = [load(model_dir, adapter_dir, d) for d in devices]
    # A tokenizer each: one tokenizer used by two threads at once can fail.
    tokenizers = [AutoTokenizer.from_pretrained(model_dir) for _ in devices]
    for t in tokenizers:
        t.padding_side = "left"
    print(f"{len(texts)} comments to score on {len(devices)} GPU(s)")
    halves = [list(range(len(texts)))[k :: len(devices)] for k in range(len(devices))]
    with ThreadPoolExecutor(len(devices)) as pool:
        results = list(pool.map(
            lambda k: score(models[k], tokenizers[k], [texts[i] for i in halves[k]], devices[k], yes, no),
            range(len(devices)),
        ))
    scores = [0.0] * len(texts)
    for half, result in zip(halves, results):
        for i, s in zip(half, result):
            scores[i] = s

    pd.DataFrame({
        "row_id": test["row_id"],
        "rule_violation": [1 / (1 + math.exp(-s)) for s in scores],  # P(Yes)
    }).to_csv("/kaggle/working/submission.csv", index=False)
    print(f"Wrote submission.csv: {len(scores)} rows in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
