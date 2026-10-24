"""llm-applied-008: bounded local reference checks. No network or persistent data writes."""

from collections import defaultdict


def rrf(rankings, constant=60):
    if constant <= 0:
        raise ValueError("positive fusion constant required")
    scores = defaultdict(float)
    for ranking in rankings:
        unique = []
        seen = set()
        for key in ranking:
            if not isinstance(key, str):
                raise TypeError("string document ID required")
            if key not in seen:
                unique.append(key)
                seen.add(key)
        for position, key in enumerate(unique, 1):
            scores[key] += 1 / (constant + position)
    return sorted(scores.items(), key=lambda row: (-row[1], row[0]))


def verify():
    # Exercise 1: Fuse two rankings
    ranked = rrf([["a", "b", "c"], ["b", "d", "a"]], 60)
    assert [key for key, score in ranked][:2] == ["b", "a"]

    # Exercise 2: Inspect one exact contribution
    scores = dict(ranked)
    assert abs(scores["b"] - (1 / 62 + 1 / 61)) < 1e-12

    # Exercise 3: Prevent duplicate votes
    assert rrf([["a", "b", "b", "c"]], 60) == rrf([["a", "b", "c"]], 60)

    # Exercise 4: Rerank a bounded candidate set
    features = {"a": 0, "b": 2, "c": 1}
    candidates = ["a", "b", "c"]
    reranked = sorted(candidates, key=lambda key: (-features[key], key))
    assert reranked == ["b", "c", "a"]

    # Exercise 5: Expose a candidate-recall ceiling
    relevant = {"d"}
    assert not set(candidates) & relevant
    assert "d" not in reranked

    # Exercise 6: Reject invalid fusion policy
    for rankings, k, kind in [([["a"]], 0, ValueError), ([[1]], 60, TypeError)]:
        try:
            rrf(rankings, k)
        except kind:
            pass
        else:
            raise AssertionError("invalid fusion input")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
