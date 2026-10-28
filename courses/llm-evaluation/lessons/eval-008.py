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


def worked_a():
    gold = {"a": 3, "b": 2, "c": 0, "d": 1}
    result = retrieval_metrics(["a", "b", "c"], gold, 2)
    assert result == {"recall": 2 / 3, "mrr": 1.0, "ndcg": 1.0}
    print("Top-two metrics:", result)


worked_a()

# Task 1: Explain why case A has nDCG 1 but recall 2/3.
# Task 2: Rank only the irrelevant document at depth 1.
# Task 3: Put the same relevant ID in two result positions.
# Task 4: Return a document absent from the relevance map.
# Task 5: Evaluate a query for which every judged document has grade 0.
# Task 6: Compare equal-query and traffic-weighted averages.

# Implement your six changes below.
