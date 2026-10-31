"""Meaningful failure/authentication contracts; run against a completed policy.

GATEWAY_DIR=/path/to/completed/gateway uv run --with-requirements gateway/requirements.txt \
    python -m unittest discover -s tests -v
"""
import asyncio
import importlib
import json
import os
from pathlib import Path
import sys
import unittest

import httpx
from fastapi.testclient import TestClient
from openai import AsyncOpenAI

sys.path.insert(0, os.environ["GATEWAY_DIR"])
os.environ.update(GATEWAY_KEY="gateway-test-key-" * 3, MODEL_KEY="model-test-key-" * 3,
                  MODEL_URL="http://model/v1", MODEL_TIMEOUT="0.05")
module = importlib.import_module("app")


def response(yes=-.1, no=-2.35):
    return {"id": "test", "object": "chat.completion", "created": 0, "model": "moderator",
            "choices": [{"index": 0, "finish_reason": "length", "message": {"role": "assistant", "content": "Yes"},
              "logprobs": {"content": [{"token": "Yes", "logprob": yes, "bytes": [89, 101, 115],
                "top_logprobs": [{"token": "Yes", "logprob": yes, "bytes": None},
                                 {"token": "No", "logprob": no, "bytes": None}]}]}}]}


class GatewayTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(module.app)
        self.client.__enter__()
        self.calls = 0
        self.headers = {"Authorization": "Bearer " + os.environ["GATEWAY_KEY"]}
        self.body = {"rule": "legal", "comment": "The heating is working again."}

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def upstream(self, status=200, content=None, delay=0, disconnect=False):
        async def handle(request):
            self.calls += 1
            payload = json.loads(request.content)
            self.assertEqual(payload["allowed_token_ids"], [9454, 2753])
            self.assertEqual(payload["temperature"], 1)
            self.assertEqual(payload["chat_template_kwargs"], {"enable_thinking": False})
            await asyncio.sleep(delay)
            if disconnect:
                raise httpx.ConnectError("upstream-secret-must-not-leak", request=request)
            return httpx.Response(status, json=content if content is not None else response())
        module.app.state.client = AsyncOpenAI(base_url="http://model/v1", api_key="private-model-key",
            max_retries=0, http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)))

    def test_unauthorized_and_invalid_do_not_call_model(self):
        self.upstream()
        for headers in ({}, {"Authorization": "Bearer wrong"}):
            self.assertEqual(self.client.post("/moderate", json=self.body, headers=headers).status_code, 401)
        for body in ({**self.body, "comment": " "}, {**self.body, "rule": "other"}, {**self.body, "comment": "x" * 2001}):
            self.assertEqual(self.client.post("/moderate", json=body, headers=self.headers).status_code, 422)
        self.assertEqual(self.calls, 0)

    def test_scores_and_decision(self):
        self.upstream()
        result = self.client.post("/moderate", json=self.body, headers=self.headers)
        self.assertEqual(result.status_code, 200)
        self.assertAlmostEqual(result.json()["score"], 2.25)
        self.assertAlmostEqual(result.json()["p_yes"], .9046505351)
        self.assertEqual(result.json()["decision"], "remove")
        self.assertEqual(result.headers["x-request-id"], result.json()["request_id"])

    def test_failures_never_become_decisions_and_do_not_retry(self):
        for kwargs, expected in [({"status": 401}, 503), ({"status": 500}, 503),
                                 ({"disconnect": True}, 503), ({"delay": .2}, 504),
                                 ({"content": {"choices": []}}, 502)]:
            with self.subTest(kwargs=kwargs):
                self.calls = 0
                self.upstream(**kwargs)
                result = self.client.post("/moderate", json=self.body, headers=self.headers)
                self.assertEqual(result.status_code, expected)
                self.assertNotIn("decision", result.json())
                self.assertNotIn("secret", result.text)
                self.assertEqual(self.calls, 1)

    def test_health_does_not_wake_model(self):
        self.upstream()
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.calls, 0)

    def test_missing_candidate_is_not_a_decision(self):
        bad = response()
        bad["choices"][0]["logprobs"]["content"][0]["top_logprobs"].pop()
        self.upstream(content=bad)
        result = self.client.post("/moderate", json=self.body, headers=self.headers)
        self.assertEqual(result.status_code, 502)
        self.assertNotIn("decision", result.json())

    def test_policy_boundaries(self):
        for p, expected in [(0, "approve"), (.3, "review"), (.799, "review"), (.8, "remove"), (1, "remove")]:
            self.assertEqual(module.decide(p, .3, .8), expected)


if __name__ == "__main__":
    unittest.main()
