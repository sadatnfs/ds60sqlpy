"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json


def recall_at_k(relevant, candidates, k):
    if not relevant or k <= 0:
        raise ValueError("Recall needs a nonempty relevance set and positive candidate budget")
    return len(set(relevant) & set(candidates[:k])) / len(relevant)


def run_cases():
    # Retrieval is trained from interactions available before the evaluation time.
    history = {"a": {"i1", "i2"}, "b": {"i1", "i3"}, "c": {"i2", "i4"}}
    target = history["a"]
    scores = {i: 0.0 for i in ("i3", "i4", "i5")}
    for user, items in history.items():
        if user == "a":
            continue
        similarity = len(items & target) / len(items | target)
        for item in items - target:
            scores[item] += similarity
    ranked = sorted(scores, key=lambda i: (-scores[i], i))
    assert ranked[:2] == ["i3", "i4"] and recall_at_k({"i4"}, ranked, 2) == 1
    popularity = {"i3": 3, "i4": 2, "i5": 1}
    cold = sorted(popularity, key=lambda i: (-popularity[i], i))
    assert cold[0] == "i3"
    # Reranking cannot recover a relevant item omitted by retrieval.
    assert recall_at_k({"i5"}, ranked, 2) == 0
    return dict(
        candidates=ranked,
        scores=scores,
        cold_start=cold,
        retrieval_recall=recall_at_k({"i4"}, ranked, 2),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-013 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
