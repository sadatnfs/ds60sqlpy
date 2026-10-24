import numpy as np
from scipy.special import logsumexp

VECTORS = {
    "car": np.array([1.0, 0.0, 0.0]),
    "automobile": np.array([0.9, 0.1, 0.0]),
    "repair": np.array([0.8, 0.2, 0.0]),
    "dog": np.array([0.0, 0.0, 1.0]),
    "pet": np.array([0.0, 0.1, 0.9]),
    "bites": np.array([0.2, 0.2, 0.2]),
    "person": np.array([0.4, 0.4, 0.4]),
}


def pooled(tokens):
    if not tokens:
        raise ValueError("empty token sequence")
    if any(token not in VECTORS for token in tokens):
        raise ValueError("unknown token")
    value = np.mean([VECTORS[token] for token in tokens], axis=0)
    norm = np.linalg.norm(value)
    if norm == 0:
        raise ValueError("zero representation")
    return value / norm


def masked_mean(values, mask):
    values = np.asarray(values, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    if values.ndim != 2 or mask.shape != (len(values),) or not mask.any():
        raise ValueError("nonempty valid-token mask required")
    return values[mask].mean(axis=0)


def contrastive_loss(scores, temperature=1.0):
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or scores.shape[0] != scores.shape[1] or temperature <= 0:
        raise ValueError("square scores and positive temperature required")
    scaled = scores / temperature
    return float(np.mean(logsumexp(scaled, axis=1) - np.diag(scaled)))


def main():
    docs = [pooled(["car", "repair"]), pooled(["dog", "pet"])]
    query = pooled(["automobile", "repair"])
    scores = np.array(docs) @ query
    assert scores[0] > scores[1] and np.isclose(np.linalg.norm(query), 1.0)
    assert np.allclose(pooled(["dog", "bites", "person"]), pooled(["person", "bites", "dog"]))
    values = np.array([[1.0, 2.0], [3.0, 4.0], [100.0, 100.0]])
    assert np.allclose(masked_mean(values, [1, 1, 0]), [2.0, 3.0])
    score_matrix = np.array([[3.0, 1.0], [1.0, 3.0]])
    assert np.isclose(contrastive_loss(score_matrix), np.log1p(np.exp(-2)))
    assert contrastive_loss(score_matrix, 0.5) < contrastive_loss(score_matrix, 1.0)
    try:
        pooled(["unknown"])
    except ValueError:
        pass
    else:
        raise AssertionError("unknown word silently encoded")
    try:
        masked_mean(values, [0, 0, 0])
    except ValueError:
        pass
    else:
        raise AssertionError("all-padding mean accepted")
    print(
        "nlp-014: explicit pooled geometry, masked mean, contrastive loss and order-loss counterexample passed"
    )


if __name__ == "__main__":
    main()
