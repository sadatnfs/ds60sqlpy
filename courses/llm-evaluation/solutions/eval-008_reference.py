import math


def retrieval_metrics(ranking, relevance, k):
    if type(k) is not int or k < 1 or len(set(ranking)) != len(ranking):
        raise ValueError("Distinct ranking and positive cutoff required")
    if any(d not in relevance for d in ranking):
        raise ValueError("Unjudged document")
    if any(type(v) is not int or v < 0 for v in relevance.values()):
        raise ValueError("Invalid grade")
    positives = {d for d, r in relevance.items() if r > 0}
    if not positives:
        return {"recall": None, "mrr": None, "ndcg": None}
    top = ranking[:k]
    dcg = sum((2 ** relevance[d] - 1) / math.log2(i + 2) for i, d in enumerate(top))
    ideal = sum(
        (2**r - 1) / math.log2(i + 2)
        for i, r in enumerate(sorted(relevance.values(), reverse=True)[:k])
    )
    first = next((i + 1 for i, d in enumerate(top) if relevance[d] > 0), None)
    return {
        "recall": len(positives.intersection(top)) / len(positives),
        "mrr": 0 if first is None else 1 / first,
        "ndcg": dcg / ideal,
    }


# === EXAMPLE A ===
def worked_a():
    gold = {"a": 3, "b": 2, "c": 0, "d": 1}
    result = retrieval_metrics(["a", "b", "c"], gold, 2)
    assert result == {"recall": 2 / 3, "mrr": 1.0, "ndcg": 1.0}
    print("Top-two metrics:", result)


# === EXAMPLE B ===
def worked_b():
    import numpy as np

    gold = {"a": 3, "b": 2, "c": 0, "d": 1}
    result = retrieval_metrics(["c", "d", "b"], gold, 2)
    expected = (1 / math.log2(3)) / (7 + 3 / math.log2(3))
    assert (
        result["recall"] == 1 / 3 and result["mrr"] == 0.5 and np.isclose(result["ndcg"], expected)
    )
    print("Weak ranking:", result)


# === EXERCISES ===
def exercise_checks():
    gold = {"a": 1, "b": 0}
    assert retrieval_metrics(["b"], gold, 1) == {"recall": 0.0, "mrr": 0, "ndcg": 0.0}
    assert retrieval_metrics(["a"], gold, 10)["ndcg"] == 1
    assert retrieval_metrics([], {"b": 0}, 1)["recall"] is None
    for ranking, k in [(["a", "a"], 2), (["x"], 1), (["a"], 0)]:
        try:
            retrieval_metrics(ranking, gold, k)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid ranking accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-008: all reference checks passed")


if __name__ == "__main__":
    main()
