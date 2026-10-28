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


# === EXAMPLE A ===
def worked_a():
    biased = identity_wins([1, 1], [True, False])
    quality = identity_wins([1, 0], [True, False])
    assert biased.tolist() == [1.0, 0.0] and biased.mean() == 0.5
    assert quality.tolist() == [1.0, 1.0]
    print(
        "Always-left identity scores:", biased.tolist(), "consistent preference:", quality.tolist()
    )


# === EXAMPLE B ===
def worked_b():
    brier, ece = calibration([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
    assert np.isclose(brier, 0.025) and np.isclose(ece, 0.15)
    constant = calibration([0.5] * 4, [1, 1, 0, 0])
    assert constant == (0.25, 0.0)
    print("Informative scores:", brier, ece, "constant calibration:", constant)


# === EXERCISES ===
def exercise_checks():
    assert calibration([1, 0], [1, 0]) == (0.0, 0.0)
    assert calibration([0, 1], [1, 0]) == (1.0, 1.0)
    assert identity_wins([0, 1], [True, False]).tolist() == [0.0, 0.0]
    assert calibration([1], [1])[0] == 0
    for p, y in [([], []), ([float("nan")], [1]), ([1.1], [1])]:
        try:
            calibration(p, y)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid confidence accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-011: all reference checks passed")


if __name__ == "__main__":
    main()
