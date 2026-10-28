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


# === EXAMPLE A ===
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


# === EXAMPLE B ===
def worked_b():
    value = js_divergence([0.8, 0.2], [0.2, 0.8])
    assert np.isclose(value, 0.8 * np.log(1.6) + 0.2 * np.log(0.4))
    assert 0 < value < np.log(2)
    assert np.isclose(js_divergence([1, 0], [0, 1]), np.log(2))
    print("Traffic JS divergence:", value)


# === EXERCISES ===
def exercise_checks():
    assert observed_cohort([], 5)["accuracy"] is None
    assert (
        observed_cohort([{"event": 1, "label_available": 10, "correct": 0}], 5)["label_coverage"]
        == 0
    )
    assert js_divergence([0.3, 0.7], [0.3, 0.7]) == 0
    assert np.isclose(js_divergence([0.2, 0.8], [0.8, 0.2]), js_divergence([0.8, 0.2], [0.2, 0.8]))
    try:
        js_divergence([2, 0], [0.5, 0.5])
    except ValueError:
        pass
    else:
        raise AssertionError("Nonprobability accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-015: all reference checks passed")


if __name__ == "__main__":
    main()
