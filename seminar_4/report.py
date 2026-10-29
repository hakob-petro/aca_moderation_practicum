"""The class table: everyone's shared result, best first.

    python3 report.py

Each student shares one run with ./share. The table shows each run's setting
and its dev AUC, then what each setting did on average across the class.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

SHARED = Path("/srv/aca/results")
BASELINE = 0.487


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else SHARED
    runs = []
    for p in sorted(folder.glob("*.json")):
        try:
            runs.append(json.loads(p.read_text()))
        except (OSError, ValueError):
            continue
    if not runs:
        sys.exit(f"Nobody has shared a result yet ({folder}). Share yours with: ./share")

    runs.sort(key=lambda r: r.get("auc", 0), reverse=True)
    print(f"{'student':<22}{'lr':>8}{'epochs':>8}{'data':>6}{'AUC':>8}{'advert.':>9}{'legal':>8}  gpu")
    for r in runs:
        per = r.get("auc_per_rule", {})
        print(f"{r.get('student', '?'):<22}{r.get('learning_rate', 0):>8g}{r.get('epochs', '?'):>8}{r.get('data', '?'):>6}"
              f"{r.get('auc', 0):>8.3f}{per.get('advertising', 0):>9.3f}{per.get('legal', 0):>8.3f}  {r.get('gpu', '')}")
    print(f"{'untrained model (Seminar 3)':<44}{BASELINE:>8.3f}")

    print("\nOn average, across the class:")
    for key, name in (("learning_rate", "learning rate"), ("epochs", "epochs"), ("data", "data")):
        groups = defaultdict(list)
        for r in runs:
            groups[r.get(key)].append(r.get("auc", 0))
        parts = [f"{value:g} -> {sum(v) / len(v):.3f} ({len(v)})" if isinstance(value, float)
                 else f"{value} -> {sum(v) / len(v):.3f} ({len(v)})" for value, v in sorted(groups.items(), key=lambda kv: str(kv[0]))]
        print(f"  {name:<14} " + "   ".join(parts))
    print("  (in brackets: how many runs. One run per setting is a small sample: the next run may differ.)")


if __name__ == "__main__":
    main()
