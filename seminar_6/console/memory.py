"""What the console remembers: labelled past cases, and a search for the most similar.

Cases are the labelled training comments of Seminar 3's split
(data/cases.jsonl) plus every comment finally decided in your decision log.
A small embedding model (model2vec, on the CPU) turns each comment into a
vector; comments that use similar words get vectors pointing the same way.

Mission 2: implement nearest(). The rest is supplied.
"""
import json
from pathlib import Path

import numpy as np
from model2vec import StaticModel

HERE = Path(__file__).resolve().parent
EMBEDDER = StaticModel.from_pretrained(str(HERE / "embedder"))
K = 10  # the vote looks at this many neighbours


def embed(texts):
    """One unit-length vector per text, so a dot product is the cosine similarity."""
    vectors = EMBEDDER.encode(list(texts))
    return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)


def nearest(vectors, query, k):
    """The k rows of vectors most similar to query, most similar first.

    vectors: an (n, d) array of unit-length rows. query: one unit-length
    vector of length d. Returns a list of (row index, similarity) pairs, where
    similarity is their dot product as a Python float; fewer pairs if n < k.
    """
    # TODO: the similarities are vectors @ query; return the k best, best first.
    raise NotImplementedError("Implement nearest() in memory.py")


class Memory:
    def __init__(self, cases):
        self.cases = cases  # dicts: rule, comment, label (1 broke the rule), source
        self.vectors = embed(case["comment"] for case in cases)
        self.rows = {}
        for i, case in enumerate(cases):
            self.rows.setdefault(case["rule"], []).append(i)

    def similar(self, rule, comment, k=K):
        """The k past cases under the same rule most similar to comment."""
        rows = self.rows.get(rule, [])
        if not rows:
            return []
        hits = nearest(self.vectors[rows], embed([comment])[0], k)
        return [{**self.cases[rows[i]], "similarity": round(s, 3)} for i, s in hits]


def vote(similar):
    """The share of the similar cases that broke the rule; None without cases."""
    return sum(case["label"] for case in similar) / len(similar) if similar else None


def precedent(similar):
    """The similarity of the most similar case that was removed; 0 if none was."""
    return max((case["similarity"] for case in similar if case["label"] == 1), default=0.0)


def course_cases(path=HERE / "data" / "cases.jsonl"):
    with open(path, encoding="utf-8") as lines:
        return [json.loads(line) for line in lines]


def load(con=None):
    """Course cases plus the comments decided in your log; your decision wins for a repeat."""
    cases = {(case["rule"], case["comment"]): case for case in course_cases()}
    if con is not None:
        from decisions import decided
        for row in decided(con):
            cases[(row["rule"], row["comment"])] = {
                "rule": row["rule"], "comment": row["comment"],
                "label": int(row["final"] == "remove"), "source": "your log"}
    return Memory(list(cases.values()))
