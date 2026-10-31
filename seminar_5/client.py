# /// script
# requires-python = ">=3.12"
# dependencies = ["openai==3.42.0"]
# ///
"""uv run client.py [--model base|moderator] [--comment TEXT] [--rule legal]."""
import argparse
import json
import sys
import time
from pathlib import Path

from openai import OpenAI

from common import SETUP, config, env, SAMPLE

sys.path.insert(0, config()["gateway"])
from model_client import read_score, score_request

parser = argparse.ArgumentParser()
parser.add_argument("--model", choices=["base", "moderator"], default="moderator")
parser.add_argument("--comment", default=SAMPLE["comment"])
parser.add_argument("--rule", choices=["advertising", "legal"], default="advertising")
args = parser.parse_args()
settings = env()
start = time.perf_counter()
with OpenAI(base_url=settings["MODEL_URL"], api_key=settings["MODEL_KEY"],
            timeout=600, max_retries=0) as client:
    response = client.chat.completions.create(**score_request(args.rule, args.comment, args.model))
score, p_yes = read_score(response)
result = {"model": args.model, "rule": args.rule, "score": score, "p_yes": p_yes,
          "seconds": round(time.perf_counter() - start, 3)}
print(json.dumps(result, indent=2))
with (SETUP / "calls.jsonl").open("a") as out:
    out.write(json.dumps(result) + "\n")
