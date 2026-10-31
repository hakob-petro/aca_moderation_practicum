"""A small closed-loop load test. Run on the server or through a laptop tunnel."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import time

from common import SETUP, env, http, SAMPLE

parser = argparse.ArgumentParser()
parser.add_argument("--url", help="Gateway URL, e.g. http://127.0.0.1:8000 through the SSH tunnel")
parser.add_argument("--env", help="Private .env file (default: the prepared gateway's .env)")
parser.add_argument("--requests", type=int, default=200)
parser.add_argument("--concurrency", type=int, default=4)
parser.add_argument("--output", type=Path, default=SETUP / "load.json")
args = parser.parse_args()
if not 1 <= args.requests <= 2000 or not 1 <= args.concurrency <= 16:
    parser.error("Use 1..2000 requests and 1..16 concurrent callers")
settings = env(args.env)
url = (args.url or f"http://127.0.0.1:{settings['PORT']}").rstrip("/") + "/moderate"
key = settings["GATEWAY_KEY"]


def one(i):
    start = time.perf_counter()
    try:
        # Vary the suffix. Common prompt prefixes can still be cached: this is a
        # warm, repetitive classroom workload, not a general capacity estimate.
        status, body = http(url, key, {**SAMPLE, "comment": SAMPLE["comment"] + f" Offer {i}."}, timeout=45)
        if status == 200 and body.get("decision") not in {"approve", "review", "remove"}:
            status = "invalid-response"
    except Exception:
        status = "connection-error"
    return status, (time.perf_counter() - start) * 1000


started = time.perf_counter()
with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
    results = list(pool.map(one, range(args.requests)))
elapsed = time.perf_counter() - started
successes = sorted(ms for status, ms in results if status == 200)
errors = Counter(str(status) for status, _ in results if status != 200)
report = {"requests": args.requests, "concurrency": args.concurrency, "successes": len(successes),
          "errors": dict(errors), "seconds": round(elapsed, 3),
          "successful_requests_per_second": round(len(successes) / elapsed, 2),
          "p50_ms": round(successes[math.ceil(.50 * len(successes)) - 1], 1) if successes else None,
          "p95_ms": round(successes[math.ceil(.95 * len(successes)) - 1], 1) if successes else None,
          "workload": "warm repeated advertising prompt with varied suffix; prefix caching may apply"}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(bool(errors))
