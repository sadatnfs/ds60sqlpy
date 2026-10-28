import numpy as np


def identity_wins(left_wins, a_on_left):
    if len(left_wins) != len(a_on_left) or not left_wins:
        raise ValueError("Paired orientations required")
    if any(type(side) is not bool for side in a_on_left) or any(
        win not in (0, 0.5, 1) for win in left_wins
    ):
        raise ValueError("Known comparison labels and Boolean orientation required")
    return np.array(
        [float(win if left else 1 - win) for win, left in zip(left_wins, a_on_left, strict=True)]
    )


def calibration(probabilities, labels, edges=(0.0, 0.5, 1.0)):
    p = np.asarray(probabilities, float)
    y = np.asarray(labels, float)
    if (
        p.shape != y.shape
        or not p.size
        or np.any((p < 0) | (p > 1))
        or not np.isfinite(p).all()
        or np.any((y != 0) & (y != 1))
    ):
        raise ValueError("Invalid calibration records")
    edges = np.asarray(edges, float)
    if (
        edges.ndim != 1
        or len(edges) < 2
        or not np.isfinite(edges).all()
        or edges[0] != 0
        or edges[-1] != 1
        or np.any(np.diff(edges) <= 0)
    ):
        raise ValueError("Increasing probability bin edges required")
    bin_id = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    ece = 0.0
    for index in range(len(edges) - 1):
        take = bin_id == index
        if take.any():
            ece += take.mean() * abs(p[take].mean() - y[take].mean())
    return float(np.mean((p - y) ** 2)), float(ece)


def worked_a():
    biased = identity_wins([1, 1], [True, False])
    quality = identity_wins([1, 0], [True, False])
    assert biased.tolist() == [1.0, 0.0] and biased.mean() == 0.5
    assert quality.tolist() == [1.0, 1.0]
    print(
        "Always-left identity scores:", biased.tolist(), "consistent preference:", quality.tolist()
    )


worked_a()

# Task 1: Candidate A is on the right and the left answer wins.
# Task 2: Score probabilities 1,0 against labels 1,0.
# Task 3: Score 0,1 against 1,0.
# Task 4: Give probability 0.5 to balanced labels.
# Task 5: Duplicate an answer paragraph without adding a claim.
# Task 6: Fit a mapping on development labels, then evaluate it on new families.

# Implement your six changes below.
