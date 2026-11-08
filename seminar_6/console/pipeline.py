"""One comment through the console: the gateway's decision, similar past cases, the route.

Until mission 2, nearest() and route() are not written yet: the console then
shows no similar cases and does whatever the gateway decided.
"""
import os

import memory
from gateway_client import moderate
from routing import route

PRECEDENT_AT = float(os.environ.get("PRECEDENT_AT", "0.85"))


def signals(mem, rule, comment):
    """What memory says: the most similar past cases, their vote, the nearest removed one."""
    try:
        similar = mem.similar(rule, comment)
    except NotImplementedError:
        similar = []
    return {"similar": similar, "vote": memory.vote(similar),
            "precedent": memory.precedent(similar) if similar else None}


def routed(model_decision, precedent):
    try:
        return route(model_decision, precedent or 0.0, PRECEDENT_AT)
    except NotImplementedError:
        return model_decision


def handle(mem, rule, comment):
    found = signals(mem, rule, comment)
    gateway = moderate(rule, comment)
    return {"gateway": gateway, **found, "routed": routed(gateway["decision"], found["precedent"])}
