"""Score 100 dev comments with a big model through an API: the frontier baseline.

    export AI_KEY=your-google-ai-studio-key
    python3 frontier.py --list-models
    python3 frontier.py --model MODEL_NAME

Works with any API that speaks OpenAI's format: Google AI Studio by default,
or OpenRouter with --base-url https://openrouter.ai/api/v1 and an OpenRouter
key. The model is asked for a number from 0 to 100; AUC needs only the order.
Results: ~/s3/frontier.json and ~/s3/frontier_predictions.csv.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from auc import column_averaged_auc  # noqa: E402

S3 = Path.home() / "s3"
AI_STUDIO = "https://generativelanguage.googleapis.com/v1beta/openai"
PER_RULE = 50

QUESTION = (
    "You are a moderator of an online community.\n\n"
    "Rule: {rule}\n\n"
    "Comments that break the rule:\n- {positive_example_1}\n- {positive_example_2}\n\n"
    "Comments that follow the rule:\n- {negative_example_1}\n- {negative_example_2}\n\n"
    "Comment to judge:\n{body}\n\n"
    "How likely is it that the comment to judge breaks the rule? "
    "Answer with one whole number from 0 (certainly not) to 100 (certainly), and nothing else."
)


def call(base_url: str, key: str, path: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def ask(base_url: str, key: str, model: str, prompt: str) -> tuple[float | None, str]:
    """Returns (the number the model gave, its raw answer). Waits and retries when the free tier says "too many requests"."""
    for attempt in range(6):
        try:
            reply = call(base_url, key, "/chat/completions", {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            })
            text = (reply["choices"][0]["message"].get("content") or "").strip()
            match = re.search(r"\d+(\.\d+)?", text)
            return (float(match.group()) if match else None), text
        except urllib.error.HTTPError as e:
            if e.code == 429:  # too many requests: wait, then try again
                time.sleep(15 * (attempt + 1))
                continue
            sys.exit(f"The API said {e.code}: {e.read().decode(errors='replace')[:300]}")
    sys.exit("Still rate-limited after several tries. Wait a while and run it again: finished comments are kept.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", help="the model's name, as --list-models prints it")
    p.add_argument("--base-url", default=AI_STUDIO, help="the API's address (default: Google AI Studio)")
    p.add_argument("--list-models", action="store_true", help="print the models this key can use")
    p.add_argument("--wait", type=float, default=6.0, help="seconds between requests, for the free tier's limits")
    args = p.parse_args()

    key = os.environ.get("AI_KEY")
    if not key:
        sys.exit("No key. First:  export AI_KEY=your-key   (it stays in this terminal only)")

    if args.list_models:
        for m in call(args.base_url, key, "/models").get("data", []):
            print(m["id"])
        return
    if not args.model:
        sys.exit("Which model? Add --model NAME. See the names with --list-models.")

    dev_file = S3 / "data" / "dev.jsonl"
    if not dev_file.exists():
        sys.exit("No dev split yet. Run:  python3 prepare_data.py")
    rows = [json.loads(line) for line in dev_file.open(encoding="utf-8")]
    chosen = []
    for rule in sorted({r["rule"] for r in rows}):
        chosen += [r for r in rows if r["rule"] == rule][:PER_RULE]

    # Keep answers as they come, so an interrupted run can continue where it stopped.
    cache_file = S3 / "frontier_answers.jsonl"
    cache = {}
    if cache_file.exists():
        for line in cache_file.open(encoding="utf-8"):
            item = json.loads(line)
            if item["model"] == args.model:
                cache[item["row_id"]] = item
    with cache_file.open("a", encoding="utf-8") as out:
        for i, r in enumerate(chosen, 1):
            if r["row_id"] in cache:
                continue
            number, text = ask(args.base_url, key, args.model, QUESTION.format(**r))
            item = {"model": args.model, "row_id": r["row_id"], "number": number, "answer": text[:200]}
            cache[r["row_id"]] = item
            out.write(json.dumps(item) + "\n")
            out.flush()
            print(f"{i:3}/{len(chosen)}  row {r['row_id']:<5} answered {text[:30]!r}")
            time.sleep(args.wait)

    short = {"No Advertising": "advertising", "No legal advice": "legal"}
    results, unreadable = [], 0
    for r in chosen:
        number = cache[r["row_id"]]["number"]
        if number is None:
            unreadable += 1
            number = 50.0  # no number in the answer: count it as 50/50
        results.append({"row_id": r["row_id"], "rule": short.get(r["rule"].split(":")[0], r["rule"]),
                        "label": r["rule_violation"], "score": number})
    mean, per_rule = column_averaged_auc(results)

    with (S3 / "frontier_predictions.csv").open("w", encoding="utf-8") as f:
        f.write("row_id,rule,label,score\n")
        for r in results:
            f.write(f"{r['row_id']},{r['rule']},{r['label']},{r['score']}\n")
    summary = {"model": args.model, "comments": len(results), "unreadable_answers": unreadable,
               "auc": round(mean, 4), "auc_per_rule": {k: round(v, 4) for k, v in per_rule.items()}}
    (S3 / "frontier.json").write_text(json.dumps(summary, indent=2) + "\n")

    for name, v in per_rule.items():
        print(f"  AUC {name:<12} {v:.3f}")
    print(f"  AUC averaged over the two rules: {mean:.3f}   ({unreadable} answers without a number)")
    print(f"Saved to {S3 / 'frontier.json'}")


if __name__ == "__main__":
    main()
