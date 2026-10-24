import numpy as np


def exact_retrieval():
    query = np.array([1.0, 0.0])
    items = np.array([[1.0, 0.0], [0.8, 0.6], [0.0, 1.0]])
    scores = items @ query
    order = np.argsort(-scores, kind="stable")
    assert order.tolist() == [0, 1, 2] and np.allclose(scores, [1.0, 0.8, 0.0])
    approximate = np.array([1, 2])
    true_top2 = set(order[:2])
    recall = len(true_top2 & set(approximate)) / 2
    assert recall == 0.5
    print("Exact order:", order, "example approximate recall@2:", recall)


def ranking_metrics():
    relevance = np.array([3.0, 2.0, 0.0])
    order = np.array([2, 0, 1])
    discount = np.log2(np.arange(2, 5))
    dcg = np.sum((2 ** relevance[order] - 1) / discount)
    ideal = np.sum((2 ** np.sort(relevance)[::-1] - 1) / discount)
    ndcg = dcg / ideal
    binary = np.array([0, 1, 1])
    hits = np.flatnonzero(binary) + 1
    reciprocal = 1 / hits[0]
    ap = np.mean(np.arange(1, len(hits) + 1) / hits)
    assert 0 < ndcg < 1 and reciprocal == 0.5 and np.isclose(ap, 7 / 12)
    print("Exponential-gain NDCG:", ndcg, "reciprocal rank:", reciprocal, "AP:", ap)


def exposure_adjustment():
    # Same underlying relevance .4, examination probabilities 1 and .25.
    expected_click = np.array([0.4, 0.1])
    examination = np.array([1.0, 0.25])
    recovered = expected_click / examination
    assert np.allclose(recovered, [0.4, 0.4])
    print("Expected clicks:", expected_click, "propensity-adjusted relevance:", recovered)


def main():
    exact_retrieval()
    ranking_metrics()
    exposure_adjustment()


if __name__ == "__main__":
    main()
