"""llm-applied-007: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def unit(value):
    value = np.asarray(value, dtype=np.float64)
    if value.ndim != 1 or not len(value) or not np.isfinite(value).all():
        raise ValueError("finite vector required")
    norm = np.linalg.norm(value)
    if norm == 0 or not np.isfinite(norm):
        raise ValueError("nonzero finite norm required")
    return value / norm


def cosine_rank(query, documents):
    q = unit(query)
    scores = []
    for key, value in documents.items():
        v = unit(value)
        if v.shape != q.shape:
            raise ValueError("embedding dimensions differ")
        scores.append((key, float(q @ v)))
    return sorted(scores, key=lambda row: (-row[1], row[0]))


def verify():
    # Exercise 1: Rank fixed topic vectors
    table = {
        "purchase": np.array([1.0, 0.1, 0.0]),
        "geometry": np.array([0.0, 1.0, 0.0]),
        "mixed": np.array([0.5, 0.5, 0.0]),
    }
    ranked = cosine_rank(np.array([1.0, 0.0, 0.0]), table)
    assert [key for key, score in ranked] == ["purchase", "mixed", "geometry"]

    # Exercise 2: Separate cosine from magnitude
    query = np.array([1.0, 0.0, 0.0])
    original = table["purchase"]
    scaled = 10 * original
    np.testing.assert_allclose(
        unit(original) @ unit(query), unit(scaled) @ unit(query), atol=1e-12, rtol=0
    )
    assert scaled @ query == 10 * (original @ query)

    # Exercise 3: Expose hand-authored synonym knowledge
    word_vectors = {"buy": np.array([1.0, 0.0, 0.0]), "purchase": np.array([1.0, 0.0, 0.0])}
    assert set("buy".split()) & set("purchase".split()) == set()
    np.testing.assert_array_equal(word_vectors["buy"], word_vectors["purchase"])

    # Exercise 4: Reject zero and nonfinite vectors
    for bad in [np.array([0.0, 0.0]), np.array([1.0, np.nan])]:
        try:
            unit(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid vector accepted")

    # Exercise 5: Reject incompatible spaces
    query_meta = {"model": "A", "width": 3, "normalization": "unit"}
    index_meta = {"model": "B", "width": 3, "normalization": "unit"}
    assert query_meta != index_meta

    # Exercise 6: Measure a domain failure
    misleading = {"wrong": np.array([1.0, 0.0, 0.0]), "relevant": np.array([0.5, 0.5, 0.0])}
    relevant = {"relevant"}
    top = cosine_rank(query, misleading)[0][0]
    assert top == "wrong" and top not in relevant
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
