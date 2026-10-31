"""One-token scoring, using the same conversation as Seminar 3's scorer.py."""
import math

from scorer import chat_for


def score_request(rule: str, comment: str, model: str = "moderator") -> dict:
    return {
        "model": model,
        "messages": chat_for(rule, comment),
        "max_tokens": 1,
        "temperature": 1.0,
        "top_p": 1.0,
        "logprobs": True,
        "top_logprobs": 2,
        "extra_body": {
            "allowed_token_ids": [9454, 2753],  # exact Yes and No, no leading space
            "chat_template_kwargs": {"enable_thinking": False},
        },
    }


def read_score(response) -> tuple[float, float]:
    entries = response.choices[0].logprobs.content[0].top_logprobs
    values = {item.token: item.logprob for item in entries}
    if not {"Yes", "No"} <= values.keys():
        raise ValueError("The server must return both Yes and No log probabilities")
    score = values["Yes"] - values["No"]
    if not math.isfinite(score):
        raise ValueError("Non-finite model score")
    # Stable sigmoid, even for very confident scores.
    p_yes = 1 / (1 + math.exp(-score)) if score >= 0 else math.exp(score) / (1 + math.exp(score))
    return score, p_yes
