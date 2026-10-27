"""Show rows of the training data, readably.

    python3 show.py 15            the row with row_id 15
    python3 show.py 15 102 7      several rows
    python3 show.py --random 3    three rows picked at random
"""

import csv
import random
import sys
import textwrap
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "data" / "train.csv"


def show(row: dict) -> None:
    label = "BREAKS the rule" if row["rule_violation"] == "1" else "follows the rule"
    print("=" * 78)
    print(f"row_id {row['row_id']}   r/{row['subreddit']}   label: {label}")
    print(f"rule: {row['rule']}")
    for key in ("body", "positive_example_1", "positive_example_2", "negative_example_1", "negative_example_2"):
        name = {"body": "body (the comment to judge)"}.get(key, key)
        text = " ".join(row[key].split())
        print(f"\n{name}:")
        print(textwrap.indent(textwrap.fill(text, 74), "    "))
    print()


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--random":
        n = int(args[1]) if len(args) > 1 else 1
        for row in random.sample(rows, n):
            show(row)
        return
    by_id = {row["row_id"]: row for row in rows}
    for row_id in args:
        if row_id in by_id:
            show(by_id[row_id])
        else:
            print(f"No row with row_id {row_id}: they go from 0 to {len(rows) - 1}.")


if __name__ == "__main__":
    main()
