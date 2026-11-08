# /// script
# requires-python = ">=3.12"
# dependencies = ["openai==3.42.0", "model2vec==0.10.0", "numpy==2.5.4"]
# ///
"""Does retrieval help the model? Dev AUC with four kinds of example comments in the prompt.

    uv run prompt_examples.py [--model moderator|base]

Your deployed model scores the 401 dev comments four times: with each row's
own examples (as in Seminar 4), the gateway's fixed examples, the most similar
labelled training comments (retrieved), and no examples. About 1,600 requests,
a minute or two once the model is warm. Saves ~/s6/prompt_examples.json.
"""
import argparse
import asyncio
import json
from pathlib import Path
import sys

from huggingface_hub import snapshot_download
from model2vec import StaticModel
import numpy as np
from openai import AsyncOpenAI

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "seminar_3"))
sys.path.insert(0, str(HERE.parents[1] / "seminar_5"))
from scorer import SHORT_NAME, build_chat, chat_for  # noqa: E402
from common import config, env  # noqa: E402  Seminar 5's settings: your model's URL and key

sys.path.insert(0, config()["gateway"])
from model_client import read_score, score_request  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--model", choices=["moderator", "base"], default="moderator")
args = parser.parse_args()
data = Path.home() / "s3" / "data"
train = [json.loads(line) for line in open(data / "train.jsonl", encoding="utf-8")]
dev = [json.loads(line) for line in open(data / "dev.jsonl", encoding="utf-8")]

# Retrieval: the labelled training comments, never a dev comment.
dev_texts = {row["body"] for row in dev}
cases = {(row["rule"], row["body"]): row["rule_violation"] for row in train if row["body"] not in dev_texts}
keys = list(cases)
# The console's embedding model, at the same fixed revision.
embedder = StaticModel.from_pretrained(snapshot_download(
    "minishlab/potion-base-8M", revision="bf8b056651a2c21b8d2565580b8569da283cab23",
    allow_patterns=["config.json", "model.safetensors", "tokenizer.json"]))


def unit(vectors):
    return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)


case_vectors = unit(embedder.encode([text for _, text in keys]))
dev_vectors = unit(embedder.encode([row["body"] for row in dev]))
rules = np.array([rule for rule, _ in keys])
labels = np.array([cases[key] for key in keys])


def retrieved(i, rule):
    """The two most similar rule-breaking and the two most similar clean training comments."""
    similarity = case_vectors @ dev_vectors[i]
    examples = {}
    for label, slots in ((1, ("positive_example_1", "positive_example_2")),
                         (0, ("negative_example_1", "negative_example_2"))):
        rows = np.where((rules == rule) & (labels == label))[0]
        best = rows[np.argsort(-similarity[rows])[:2]]
        examples.update({slot: keys[j][1] for slot, j in zip(slots, best)})
    return examples


VARIANTS = {
    "own (Seminar 4)": lambda i, row: build_chat(row["rule"], row["body"], row),
    "fixed (gateway)": lambda i, row: chat_for(SHORT_NAME[row["rule"]], row["body"]),
    "retrieved": lambda i, row: build_chat(row["rule"], row["body"], retrieved(i, row["rule"])),
    "none": lambda i, row: build_chat(row["rule"], row["body"]),
}


def auc(scores, truth):
    pos = [s for s, y in zip(scores, truth) if y]
    neg = [s for s, y in zip(scores, truth) if not y]
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


async def main():
    settings = env()
    limit = asyncio.Semaphore(8)
    async with AsyncOpenAI(base_url=settings["MODEL_URL"], api_key=settings["MODEL_KEY"],
                           timeout=600, max_retries=0) as client:
        async def score(chat):
            # The same one-token request as the gateway, with our own conversation.
            request = {**score_request("advertising", "", args.model), "messages": chat}
            async with limit:
                return read_score(await client.chat.completions.create(**request))[0]

        print("Warming the model (a cold start takes a minute or more)...", flush=True)
        await score(chat_for("advertising", "warm up"))
        results = {}
        for name, make in VARIANTS.items():
            scores = await asyncio.gather(*(score(make(i, row)) for i, row in enumerate(dev)))
            per_rule = {}
            for rule in sorted({row["rule"] for row in dev}):
                rows = [i for i, row in enumerate(dev) if row["rule"] == rule]
                per_rule[SHORT_NAME[rule]] = round(auc([scores[i] for i in rows],
                                                       [dev[i]["rule_violation"] for i in rows]), 3)
            results[name] = {"auc": round(sum(per_rule.values()) / len(per_rule), 3), **per_rule}
            print(f"{name:16} AUC {results[name]['auc']:.3f}  {per_rule}", flush=True)
    out = Path.home() / "s6" / "prompt_examples.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"model": args.model, "results": results}, indent=2) + "\n")
    print(f"Saved {out}")


asyncio.run(main())
