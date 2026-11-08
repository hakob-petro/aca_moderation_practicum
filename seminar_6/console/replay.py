"""Mission 3: red-team comments through the console's pipeline, without logging them.

Reads a JSON list of {"author", "rule", "comment"} on standard input and
prints JSON. With --teach, it remembers the given comments instead: each goes
into the decision log as a removed case, decided by a human.
Run it with ./replay from ~/course/seminar_6.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import sys

import decisions
import memory
from gateway_client import GatewayError, moderate
from pipeline import routed, signals

items = json.load(sys.stdin)
con = decisions.connect()

if "--teach" in sys.argv:
    known = {(row["rule"], row["comment"]) for row in decisions.decided(con)}
    new = [item for item in items if (item["rule"], item["comment"]) not in known]
    for item in new:
        decisions.teach(con, item["rule"], item["comment"])
    print(json.dumps({"taught": len(new)}))
    sys.exit()

mem = memory.load(con)
found = [signals(mem, item["rule"], item["comment"]) for item in items]


def ask(item):
    try:
        return moderate(item["rule"], item["comment"], timeout=60)
    except GatewayError as error:
        return {"error": str(error)}


with ThreadPoolExecutor(max_workers=4) as pool:
    answers = list(pool.map(ask, items))
results = []
for item, memory_says, answer in zip(items, found, answers):
    if "error" in answer:
        results.append({**item, "error": answer["error"]})
        continue
    results.append({**item, "p_yes": round(answer["p_yes"], 3), "model": answer["decision"],
                    "vote": memory_says["vote"], "precedent": memory_says["precedent"],
                    "console": routed(answer["decision"], memory_says["precedent"])})
lessons = con.execute("SELECT COUNT(*) FROM decisions WHERE source = 'redteam'").fetchone()[0]
print(json.dumps({"lessons": lessons, "results": results}))
