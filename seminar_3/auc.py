"""AUC, computed the way the Kaggle competition does it.

AUC is the chance that a randomly chosen comment that breaks the rule gets a
higher score than a randomly chosen comment that does not. 1.0 is perfect,
0.5 is guessing. Only the order of the scores matters, not their size.

Kaggle computes it for each rule separately, then averages the rules:
"column-averaged AUC".
"""


def auc(labels: list[int], scores: list[float]) -> float:
    """The share of (breaking, clean) pairs where the breaking one scores higher. Ties count half."""
    pairs = sorted(zip(scores, labels))
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("AUC needs both breaking and clean comments")

    # Walk up from the lowest score. Each breaking comment beats every clean
    # comment below it. Equal scores are handled as one block.
    wins = 0.0
    clean_below = 0
    i = 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        block = [label for _, label in pairs[i:j]]
        pos, neg = sum(block), len(block) - sum(block)
        wins += pos * clean_below + pos * neg / 2
        clean_below += neg
        i = j
    return wins / (n_pos * n_neg)


def column_averaged_auc(rows: list[dict]) -> tuple[float, dict[str, float]]:
    """rows: dicts with "rule", "label" and "score". Returns (mean over rules, AUC of each rule)."""
    by_rule = {}
    for row in rows:
        labels, scores = by_rule.setdefault(row["rule"], ([], []))
        labels.append(int(row["label"]))
        scores.append(float(row["score"]))
    per_rule = {rule: auc(labels, scores) for rule, (labels, scores) in sorted(by_rule.items())}
    return sum(per_rule.values()) / len(per_rule), per_rule
