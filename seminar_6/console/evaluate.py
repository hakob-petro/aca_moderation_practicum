"""Mission 2: how well does memory alone rank the dev comments, next to your model?

Memory here is only the course's labelled training comments, so no dev comment
can find itself. For every inbox (dev) comment: the vote of its 10 nearest
cases, and your model's p_yes through the gateway. Prints JSON; run it with
./evaluate from ~/course/seminar_6.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import memory
from gateway_client import moderate
from pipeline import PRECEDENT_AT, routed

HERE = Path(__file__).resolve().parent
with open(HERE / "data" / "inbox.jsonl", encoding="utf-8") as lines:
    items = [json.loads(line) for line in lines]
mem = memory.load()  # course cases only: no decisions from your log
found = [mem.similar(item["rule"], item["comment"]) for item in items]
votes = [memory.vote(similar) for similar in found]
precedents = [memory.precedent(similar) for similar in found]
with ThreadPoolExecutor(max_workers=4) as pool:
    answers = list(pool.map(lambda item: moderate(item["rule"], item["comment"], timeout=60), items))
p_yes = [answer["p_yes"] for answer in answers]


def auc(scores, labels):
    """The chance that a random rule-breaking comment scores above a random clean one."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def per_rule(scores):
    """AUC for each rule, and their average: the same metric as Seminars 3 and 4."""
    result = {}
    for rule in sorted({item["rule"] for item in items}):
        rows = [i for i, item in enumerate(items) if item["rule"] == rule]
        result[rule] = round(auc([scores[i] for i in rows], [items[i]["label"] for i in rows]), 3)
    result["mean"] = round(sum(result.values()) / len(result), 3)
    return result


approved = [i for i, answer in enumerate(answers) if answer["decision"] == "approve"]
escalated = [i for i in approved if routed("approve", precedents[i]) == "review"]
print(json.dumps({
    "comments": len(items),
    "model_auc": per_rule(p_yes),
    "vote_auc": per_rule(votes),
    "model_approved": len(approved),
    "approved_but_broke_the_rule": sum(items[i]["label"] for i in approved),
    "precedent_at": PRECEDENT_AT,
    "sent_to_review_by_precedent": len(escalated),
    "of_which_broke_the_rule": sum(items[i]["label"] for i in escalated),
}, indent=2))
