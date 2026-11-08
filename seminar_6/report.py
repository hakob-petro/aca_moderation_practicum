"""The class red-team table: everyone's replays, and the attacks that fooled the most services.

    python3 report.py
"""
import json
from collections import Counter

from common import POOL

rows = []
fooled = Counter()
for path in sorted((POOL / "results").glob("*.json")):
    result = json.loads(path.read_text())
    cell = lambda name: (f"{result[name]['slipped']}/{result[name]['comments']}" if name in result else "–")
    rows.append((path.stem, cell("before"), cell("after"), cell("paraphrases")))
    for author, comment in result.get("before", {}).get("slipped_comments", []):
        fooled[(author, comment)] += 1

if not rows:
    raise SystemExit("Nobody has replayed the pool yet.")
print(f"{'student':20} {'before':>8} {'after':>8} {'paraphrases':>12}   (slipped through / replayed)")
for row in rows:
    print(f"{row[0]:20} {row[1]:>8} {row[2]:>8} {row[3]:>12}")
print(f"\nAttacks that slipped past the most services ({len(rows)} replayed the pool):")
for (author, comment), n in fooled.most_common(5):
    print(f"  {n:3}  [{author}] {comment[:100]}")
