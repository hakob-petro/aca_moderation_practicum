"""The dev comments your fine-tuned model got most wrong.

    python3 wrong.py             your latest run
    python3 wrong.py RUN         a particular run

It lists the comments that follow the rule but scored highest, and the ones
that break it but scored lowest. Read any of them in full with
    python3 ~/course/seminar_3/show.py ROW_ID
"""

import csv
import sys
from pathlib import Path

RESULTS = Path.home() / "s4" / "results"


def main() -> None:
    if len(sys.argv) > 1:
        file = RESULTS / f"{sys.argv[1]}_predictions.csv"
    else:
        found = sorted(RESULTS.glob("*_predictions.csv"), key=lambda p: p.stat().st_mtime)
        if not found:
            sys.exit("No results yet: run modal run train.py first (mission 1).")
        file = found[-1]
    if not file.exists():
        sys.exit(f"No such run: {file.name}")

    rows = list(csv.DictReader(file.open(encoding="utf-8")))
    texts = {}
    with (Path(__file__).resolve().parent.parent / "data" / "train.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            texts[r["row_id"]] = " ".join(r["body"].split())

    clean = sorted((r for r in rows if r["label"] == "0"), key=lambda r: -float(r["score"]))[:5]
    breaking = sorted((r for r in rows if r["label"] == "1"), key=lambda r: float(r["score"]))[:5]
    print(f"From {file.name}. A score above 0 means the model leans to Yes.\n")
    print("Labelled 'follows the rule', but the model said it breaks it:")
    for r in clean:
        print(f"  row {r['row_id']:>5}  {r['rule']:<12} score {float(r['score']):+6.2f}  {texts.get(r['row_id'], '')[:70]}")
    print("\nLabelled 'breaks the rule', but the model said it follows it:")
    for r in breaking:
        print(f"  row {r['row_id']:>5}  {r['rule']:<12} score {float(r['score']):+6.2f}  {texts.get(r['row_id'], '')[:70]}")


if __name__ == "__main__":
    main()
