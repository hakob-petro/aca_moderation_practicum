"""Console contracts and the Streamlit app against a fake gateway; run against a completed console.

Inside the running console container, from ~/s6/console:
    docker compose exec -T console python - < ~/course/seminar_6/tests/test_console.py
It uses a temporary database, never your decision log, and never calls the model.
"""
import os
import tempfile
import unittest

os.environ["DECISIONS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

import numpy as np  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

import decisions  # noqa: E402
import memory  # noqa: E402
import pipeline  # noqa: E402
from gateway_client import GatewayError  # noqa: E402
from routing import route  # noqa: E402


def fake_gateway(rule, comment, timeout=20.0):
    """approve, review or remove from the comment's length: deterministic, no model."""
    p_yes = [0.1, 0.5, 0.9][len(comment) % 3]
    decision = "approve" if p_yes < 0.3 else "remove" if p_yes >= 0.8 else "review"
    return {"request_id": f"fake-{len(comment)}", "rule": rule, "model": "moderator", "score": 0.0,
            "p_yes": p_yes, "decision": decision, "thresholds": {"approve_below": 0.3, "remove_at": 0.8}}


def down(rule, comment, timeout=20.0):
    raise GatewayError("HTTP 503: Model unavailable; no moderation decision was made")


class Contracts(unittest.TestCase):
    def test_log_keeps_model_decision(self):
        con = decisions.connect(os.path.join(tempfile.mkdtemp(), "c.db"))
        gateway = fake_gateway("legal", "abc")
        row_id = decisions.record(con, "inbox", "legal", "x'); DROP TABLE decisions;--", gateway, "approve")
        decisions.set_final(con, row_id, "remove")
        row = con.execute("SELECT * FROM decisions WHERE id = ?", (row_id,)).fetchone()
        self.assertEqual((row["model_decision"], row["routed"], row["final"], row["decided_by"]),
                         ("approve", "approve", "remove", "human"))
        with self.assertRaises(ValueError):
            decisions.set_final(con, row_id, "review")
        with self.assertRaises(KeyError):
            decisions.set_final(con, 999, "remove")

    def test_nearest_and_memory(self):
        vectors = np.array([[1, 0], [0.6, 0.8], [0, 1]])
        self.assertEqual([i for i, _ in memory.nearest(vectors, np.array([0.0, 1.0]), 2)], [2, 1])
        mem = memory.load()
        case = mem.cases[0]
        found = mem.similar(case["rule"], case["comment"])
        self.assertEqual(len(found), memory.K)
        self.assertGreater(found[0]["similarity"], 0.99)
        self.assertTrue(all(c["rule"] == case["rule"] for c in found))

    def test_route(self):
        self.assertEqual(route("approve", 0.85, 0.85), "review")
        self.assertEqual(route("approve", 0.84, 0.85), "approve")
        self.assertEqual(route("remove", 1.0, 0.85), "remove")


class App(unittest.TestCase):
    def setUp(self):
        con = decisions.connect()
        con.execute("DELETE FROM decisions")
        con.commit()

    def run_app(self, gateway):
        pipeline.moderate = gateway
        app = AppTest.from_file("app.py", default_timeout=120).run()
        self.assertFalse(app.exception)
        return app

    def test_inbox_review_and_override(self):
        app = self.run_app(fake_gateway)
        next(b for b in app.button if b.label == "Moderate the next 5").click().run()
        con = decisions.connect()
        self.assertEqual(decisions.counts(con)["logged"], 5)
        for _ in range(5):
            buttons = [b for b in app.button if b.label == "Remove"]
            if not buttons:
                break
            buttons[0].click().run()
        self.assertEqual(decisions.counts(con)["waiting"], 0)
        automatic = con.execute("SELECT id, final FROM decisions WHERE decided_by = 'model'").fetchone()
        app.number_input[0].set_value(automatic["id"]).run()
        app.radio[0].set_value("approve" if automatic["final"] == "remove" else "remove").run()
        next(b for b in app.button if b.label == "Override").click().run()
        self.assertEqual(decisions.counts(con)["overrides"], 1)

    def test_gateway_failure_decides_nothing(self):
        app = self.run_app(down)
        next(b for b in app.button if b.label == "Moderate the next 5").click().run()
        self.assertTrue(any("No decision" in e.value for e in app.error))
        self.assertEqual(decisions.counts(decisions.connect())["logged"], 0)


unittest.main(argv=["test_console"], verbosity=2, exit=True)
