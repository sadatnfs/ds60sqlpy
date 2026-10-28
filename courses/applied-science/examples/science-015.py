"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def ips_value(reward, logged_probability, target_probability):
    r, p, q = map(lambda v: np.asarray(v, float), (reward, logged_probability, target_probability))
    if r.shape != p.shape or r.shape != q.shape or r.ndim != 1 or not len(r):
        raise ValueError("Use matching nonempty vectors")
    if not all(np.all(np.isfinite(v)) for v in (r, p, q)) or np.any((p > 1) | (q < 0) | (q > 1)):
        raise ValueError("Use finite rewards and valid probabilities")
    if np.any(p <= 0):
        raise ValueError("Target action lacks logging-policy support")
    return float(np.mean(r * q / p))


def run_cases():
    # Exact repeated logging population: A occurs80%, B20%; reward(.2,.8).
    p = np.r_[np.full(80, 0.8), np.full(20, 0.2)]
    reward = np.r_[np.full(80, 0.2), np.full(20, 0.8)]
    q = np.full(100, 0.5)
    value = ips_value(reward, p, q)
    observed = float(reward.mean())
    assert np.isclose(value, 0.5) and np.isclose(observed, 0.32)
    clipped = float(np.mean(reward * np.minimum(q / p, 1.5)))
    assert clipped < value
    model = np.r_[np.full(80, 0.3), np.full(20, 0.7)]
    dr = 0.5 * 0.3 + 0.5 * 0.7 + float(np.mean(q / p * (reward - model)))
    assert np.isclose(dr, 0.5)
    return dict(ips=value, logging_average=observed, clipped_estimate=clipped, doubly_robust=dr)


if __name__ == "__main__":
    evidence = run_cases()
    print("science-015 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
