"""The decision log: every comment the console handled, in SQLite on a Docker volume.

Mission 1: implement record() and set_final(). The rest is supplied.

A human decision goes in `final`. The model's decision is never overwritten,
so each row shows what the model said, what the console did, and who decided.
"""
import os
import sqlite3
from datetime import datetime, timezone

DB = os.environ.get("DECISIONS_DB", "/data/decisions.db")
DECISIONS = ("approve", "remove")

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id             INTEGER PRIMARY KEY,
    created_at     TEXT NOT NULL,
    source         TEXT NOT NULL,  -- inbox, typed or redteam
    rule           TEXT NOT NULL,  -- advertising or legal
    comment        TEXT NOT NULL,
    request_id     TEXT,           -- the gateway's ID: finds its log line
    p_yes          REAL,
    model_decision TEXT,           -- approve, review or remove, from the gateway
    approve_below  REAL,
    remove_at      REAL,
    vote           REAL,           -- mission 2: share of the 10 nearest cases that broke the rule
    precedent      REAL,           -- mission 2: similarity of the nearest removed case
    routed         TEXT,           -- what the console did: the model's decision, or review
    final          TEXT,           -- approve or remove; NULL while waiting for a human
    decided_by     TEXT,           -- model or human
    decided_at     TEXT
)
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str = DB) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute(SCHEMA)
    return con


def record(con, source, rule, comment, gateway, routed, vote=None, precedent=None) -> int:
    """Insert one handled comment and return its id.

    gateway is the gateway's /moderate response: request_id, p_yes, decision
    (stored as model_decision) and thresholds {approve_below, remove_at}.
    routed is approve, review or remove. approve and remove are final at once:
    final = routed, decided_by = "model", decided_at = now(). review waits
    for a human: final, decided_by and decided_at stay NULL.
    """
    # TODO: one INSERT with ? placeholders (never put values into the SQL text),
    # then commit and return the new row's id.
    raise NotImplementedError("Implement record() in decisions.py")


def set_final(con, decision_id, decision) -> None:
    """A human decides a comment: final = decision, decided_by = "human",
    decided_at = now(). model_decision and routed stay as they were.

    Raises ValueError unless decision is approve or remove, and KeyError if
    no row has this id.
    """
    # TODO: check the decision, one UPDATE with ? placeholders, then commit.
    raise NotImplementedError("Implement set_final() in decisions.py")


def teach(con, rule, comment) -> int:
    """Mission 3: remember a red-team comment as a removed case, decided by a human."""
    stamp = now()
    cursor = con.execute(
        "INSERT INTO decisions (created_at, source, rule, comment, final, decided_by, decided_at)"
        " VALUES (?, 'redteam', ?, ?, 'remove', 'human', ?)", (stamp, rule, comment, stamp))
    con.commit()
    return cursor.lastrowid


def pending(con):
    return con.execute("SELECT * FROM decisions WHERE final IS NULL ORDER BY id").fetchall()


def recent(con, limit=50):
    return con.execute("SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def decided(con):
    """Every comment with a final decision: the console's own past cases."""
    return con.execute(
        "SELECT rule, comment, final FROM decisions WHERE final IS NOT NULL ORDER BY id").fetchall()


def counts(con) -> dict:
    row = con.execute("""
        SELECT COUNT(*) AS logged,
               SUM(final IS NULL) AS waiting,
               SUM(decided_by = 'human') AS by_human,
               SUM(decided_by = 'human' AND model_decision IN ('approve', 'remove')
                   AND final != model_decision) AS overrides
        FROM decisions WHERE source != 'redteam'""").fetchone()
    return {key: row[key] or 0 for key in row.keys()}
