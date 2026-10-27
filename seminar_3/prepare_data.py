"""Split the Jigsaw training data into train and dev.

    python3 prepare_data.py

Reads ~/course/data/train.csv and writes ~/s3/data/train.jsonl and
~/s3/data/dev.jsonl, one comment per line. Everyone gets the same split, so
everyone's AUC is measured on the same comments.

The split is by comment text: a text that appears several times goes entirely
into train or entirely into dev, so the model is never tested on a comment it
was trained on.
"""

import csv
import json
import random
from collections import defaultdict
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "data" / "train.csv"
OUT = Path.home() / "s3" / "data"
DEV_SHARE = 0.2
SEED = 42


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["row_id"] = int(row["row_id"])
        row["rule_violation"] = int(row["rule_violation"])

    # Group rows by comment text, separately for each rule.
    groups = defaultdict(list)
    for row in rows:
        groups[(row["rule"], row["body"])].append(row)

    # Within each rule, send a random fifth of the texts to dev. A text that
    # appears under both rules goes to the side it lands on first.
    rng = random.Random(SEED)
    side_of_text = {}
    for rule in sorted({row["rule"] for row in rows}):
        texts = sorted(body for (r, body) in groups if r == rule)
        rng.shuffle(texts)
        n_dev = round(len(texts) * DEV_SHARE)
        for i, body in enumerate(texts):
            side_of_text.setdefault(body, "dev" if i < n_dev else "train")

    split = {"train": [], "dev": []}
    for row in rows:
        split[side_of_text[row["body"]]].append(row)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, part in split.items():
        part.sort(key=lambda r: r["row_id"])
        with (OUT / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for row in part:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Read {len(rows)} comments from {SOURCE}")
    for name, part in split.items():
        print(f"\n{name}: {len(part)} comments -> {OUT / (name + '.jsonl')}")
        for rule in sorted({r['rule'] for r in part}):
            labels = [r["rule_violation"] for r in part if r["rule"] == rule]
            print(f"  {rule[:40]:<40}  {len(labels):>4} comments, "
                  f"{sum(labels) / len(labels):.0%} break the rule")


if __name__ == "__main__":
    main()
