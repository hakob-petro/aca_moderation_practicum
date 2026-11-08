"""Calls your Seminar 5 gateway, over the Docker network the two projects share."""
import os

import httpx

URL = os.environ.get("GATEWAY_URL", "http://gateway:8000")
KEY = os.environ["GATEWAY_KEY"]


class GatewayError(Exception):
    """The gateway gave no decision: nothing may be decided for this comment."""


def moderate(rule, comment, timeout=20.0):
    try:
        response = httpx.post(URL + "/moderate", json={"rule": rule, "comment": comment},
                              headers={"Authorization": f"Bearer {KEY}"}, timeout=timeout)
    except httpx.HTTPError as error:
        raise GatewayError(f"cannot reach the gateway at {URL} ({type(error).__name__})") from None
    if response.status_code != 200:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text[:200]
        raise GatewayError(f"HTTP {response.status_code}: {detail}")
    return response.json()
