import numpy as np


def observed_cohort(rows, as_of):
    eligible = [r for r in rows if r["event"] <= as_of]
    observed = [r for r in eligible if r["label_available"] <= as_of]
    return {
        "eligible": len(eligible),
        "labeled": len(observed),
        "label_coverage": len(observed) / len(eligible) if eligible else None,
        "accuracy": float(np.mean([r["correct"] for r in observed])) if observed else None,
    }


def js_divergence(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p < 0)
        or np.any(q < 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Probability vectors required")
    m = (p + q) / 2

    def term(x):
        positive = x > 0
        return float(np.sum(x[positive] * np.log(x[positive] / m[positive])))

    return (term(p) + term(q)) / 2


def worked_a():
    rows = [
        {"event": 1, "label_available": 2, "correct": 1},
        {"event": 1, "label_available": 10, "correct": 0},
    ]
    early = observed_cohort(rows, 2)
    mature = observed_cohort(rows, 10)
    assert early["accuracy"] == 1 and early["label_coverage"] == 0.5
    assert mature["accuracy"] == 0.5 and mature["label_coverage"] == 1
    print("Early:", early, "mature:", mature)


worked_a()

# Task 1: Evaluate the two requests at day 2.
# Task 2: Evaluate the same requests at day 10.
# Task 3: Compare a histogram to itself.
# Task 4: Compare[1,0] with[0,1] using natural logarithms.
# Task 5: Requests from one user share conversational history.
# Task 6: A drift score rises while mature-cohort quality is stable.

# Implement your six changes below.
