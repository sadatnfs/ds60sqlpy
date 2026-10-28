"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special


def bpr_loss_gradient(weights, differences, penalty=0.01):
    w = np.asarray(weights, float)
    d = np.asarray(differences, float)
    margin = d @ w
    loss = float(np.logaddexp(0, -margin).mean() + penalty * (w @ w) / 2)
    grad = -(d * special.expit(-margin)[:, None]).mean(axis=0) + penalty * w
    return loss, grad


def negative_candidates(exposures, positives, cutoff, window, max_reporting_lag):
    if window < 0 or max_reporting_lag < 0:
        raise ValueError("Attribution and reporting bounds must be nonnegative")
    result = []
    for item, exposed in exposures:
        if exposed + window + max_reporting_lag > cutoff:
            continue
        positive = any(
            observed_item == item
            and exposed <= event_time <= exposed + window
            and available <= cutoff
            for observed_item, event_time, available in positives
        )
        if not positive:
            result.append(item)
    return result


def run_cases():
    d = np.array([[1.0, 0.0], [2.0, 1.0], [1.0, -1.0]])
    w = np.zeros(2)
    initial = bpr_loss_gradient(w, d)[0]
    for _ in range(200):
        w -= 0.1 * bpr_loss_gradient(w, d)[1]
    loss, gradient = bpr_loss_gradient(w, d)
    assert loss < initial and np.all(d @ w > 0)
    h = 1e-5
    numeric = []
    for j in range(2):
        shift = np.eye(2)[j] * h
        numeric.append(
            (bpr_loss_gradient(w + shift, d)[0] - bpr_loss_gradient(w - shift, d)[0]) / (2 * h)
        )
    assert np.allclose(gradient, numeric, atol=1e-8)
    # A future click is not a verified negative at the earlier ranking time.
    exposures = [("i1", 0), ("i2", 4), ("i3", 0), ("i4", 1)]
    positives = [("i1", 1, 2), ("i2", 6, 8)]
    known_positive = {item for item, event_time, available in positives if available <= 5}
    negatives = negative_candidates(exposures, positives, 5, 3, 2)
    assert "i2" not in known_positive and negatives == ["i3"]
    assert negative_candidates(exposures, positives, 9, 3, 2) == ["i3", "i4"]
    return dict(
        initial_loss=initial, trained_loss=loss, weights=w.tolist(), margins=(d @ w).tolist()
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-014 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
