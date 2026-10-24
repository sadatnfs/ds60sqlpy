"""llm-014: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Fit a tiny baseline
    docs = [[0, 1, 0, 1], [0, 2]]
    counts = np.zeros((3, 3), dtype=int)
    for doc in docs:
        for a, b in zip(doc[:-1], doc[1:]):
            counts[a, b] += 1
    assert counts[0, 1] == 2 and counts[1, 0] == 1 and counts[0, 2] == 1 and counts.sum() == 4

    # Exercise 2: Normalize smoothed rows
    prob = (counts + 1) / (counts.sum(1, keepdims=True) + 3)
    np.testing.assert_allclose(prob.sum(1), 1, atol=1e-12, rtol=0)
    np.testing.assert_allclose(prob[2], [1 / 3] * 3, atol=1e-12, rtol=0)

    # Exercise 3: Score held-out transitions
    saved = counts.copy()
    held = [0, 2, 1]
    nll = -sum(np.log(prob[a, b]) for a, b in zip(held[:-1], held[1:]))
    np.testing.assert_allclose(nll, 2 * np.log(3), atol=1e-12, rtol=0)
    assert len(held) - 1 == 2

    # Exercise 4: Prove no assessment update
    np.testing.assert_array_equal(counts, saved)

    # Exercise 5: Verify a causal prefix oracle
    values = np.array([2.0, 4.0, 8.0])
    out = np.array([values[: i + 1].mean() for i in range(3)])
    np.testing.assert_allclose(out, [2, 3, 14 / 3], atol=1e-12, rtol=0)
    for cut in range(1, 4):
        np.testing.assert_allclose(
            out[:cut], [values[: i + 1].mean() for i in range(cut)], atol=1e-12, rtol=0
        )

    # Exercise 6: Write the bounded comparison
    report = {
        "vocabulary": 3,
        "targets": 2,
        "mean_nll": float(nll / 2),
        "limitation": "Tiny authored corpus; unseen tasks remain untested.",
    }
    assert (
        np.isfinite(report["mean_nll"])
        and report["targets"] == 2
        and "untested" in report["limitation"]
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
