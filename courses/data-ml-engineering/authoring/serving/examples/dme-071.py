"""Latency denominators and arrival-cohort effects from explicit synthetic timestamps."""

import numpy as np


def summarize(arrived, admitted, first, completed, output_tokens):
    if not arrived <= admitted <= first <= completed or output_tokens < 2:
        raise ValueError("Need ordered timestamps and at least two output tokens")
    return {
        "queue": admitted - arrived,
        "ttft": first - arrived,
        "after_admission_first_token": first - admitted,
        "tpot": (completed - first) / (output_tokens - 1),
        "e2e": completed - arrived,
    }


def example_one():
    values = summarize(0.0, 0.2, 0.5, 1.7, 5)
    np.testing.assert_allclose(list(values.values()), [0.2, 0.5, 0.3, 0.3, 1.7])
    print(values)
    compute, transport, pacing = 0.4, 0.8, 0.5
    assert abs(compute + transport + pacing - values["e2e"]) < 1e-12
    print(
        "Wall time",
        values["e2e"],
        "compute",
        compute,
        "transport/storage model",
        transport,
        "pacing",
        pacing,
    )


def example_two():
    fast = np.array([0.1] * 90)
    slow = np.array([3.0] * 10)
    pooled = np.concatenate([fast, slow])
    assert float(np.median(pooled)) == 0.1
    assert float(np.quantile(pooled, 0.95)) == 3.0
    weighted_scenario_mean = (fast.mean() + slow.mean()) / 2
    request_mean = pooled.mean()
    assert abs(request_mean - 0.39) < 1e-12
    assert abs(weighted_scenario_mean - 1.55) < 1e-12
    print(
        "Request mean",
        request_mean,
        "equal-scenario mean",
        weighted_scenario_mean,
        "p50",
        np.median(pooled),
        "p95",
        np.quantile(pooled, 0.95),
    )
    print("Different denominators answer different capacity and user-experience questions.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
