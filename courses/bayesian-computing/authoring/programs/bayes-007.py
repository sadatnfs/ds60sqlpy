"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def leapfrog(q, p, step, count):
    p = p - 0.5 * step * q
    for i in range(count):
        q = q + step * p
        if i < count - 1:
            p = p - step * q
    p = p - 0.5 * step * q
    return q, p


def run_cases():
    q0, p0 = 0.5, 0.7
    q, p = leapfrog(q0, p0, 0.2, 10)
    reverse_q, reverse_p = leapfrog(q, -p, 0.2, 10)
    assert np.allclose([reverse_q, reverse_p], [q0, -p0], atol=1e-12)
    energy = 0.5 * (q * q + p * p) - 0.5 * (q0 * q0 + p0 * p0)
    assert abs(energy) < 0.02
    bad_q, bad_p = leapfrog(q0, p0, 3.0, 10)
    bad_energy = 0.5 * (bad_q**2 + bad_p**2) - 0.5 * (q0**2 + p0**2)
    assert bad_energy > 1e6
    return dict(
        small_step_energy_error=energy,
        reversibility_error=float(abs(reverse_q - q0)),
        large_step_energy_error=bad_energy,
        large_step_acceptance=float(np.exp(-bad_energy)),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-007 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
