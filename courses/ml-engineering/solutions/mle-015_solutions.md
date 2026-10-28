# mle-015: explained reference

Monitor operations, data contracts and mature outcomes as distinct signals.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Move the monitoring cutoff

Record the cutoff and cohort identities. Comparing different maturity stages without adjustment can create a misleading trend.

**Expected:** Newly available labels change the evaluated population.

## 2. Test outcome-dependent delay

Investigate delay by outcome and cohort, and use an appropriate evaluation design. Do not assume missing-at-random labels without evidence.

**Expected:** Early observed quality can be biased.

## 3. Interpret drift

Inspect data contracts and evaluate mature outcomes when available. A changed distribution can be harmless, harmful or even beneficial depending on the model and task.

**Expected:** It establishes a difference under the tested sample/comparison, not performance loss.

## 4. Record metric scope

Aggregate with suitable identities and windows when designing a real service. Preserve reset/restart behavior in the interpretation.

**Expected:** The scope is explicit.

## 5. Choose an action

Use a reviewed reject, fallback, investigation or rollback policy. Avoid silently continuing with invalid inputs while reporting healthy service status.

**Expected:** The response is specific and bounded.

## 6. Keep uncertainty visible

Retain counts and distributional context, then collect representative observations for a meaningful service objective or comparison.

**Expected:** The estimate is visibly weak.

## Complete reference

```python
"""mle-015: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


def example_one():
    labels = pd.DataFrame(
        {
            "prediction_id": [1, 2, 3, 4],
            "prediction_time": [1, 2, 3, 4],
            "label_available": [3, 7, 5, 8],
            "label": [0, 1, 1, 0],
            "score": [0.1, 0.9, 0.6, 0.2],
        }
    )
    cutoff = 5
    mature = labels[labels.label_available <= cutoff]
    brier = float(np.mean((mature.score - mature.label) ** 2))
    assert mature.prediction_id.tolist() == [1, 3] and abs(brier - 0.085) < 1e-12
    assert len(mature) / len(labels) == 0.5
    return {"mature_prediction_ids": [1, 3], "brier": brier, "label_coverage": 0.5}


def example_two():
    from scipy.stats import ks_2samp

    baseline = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    shifted = baseline + 10
    statistic = float(ks_2samp(baseline, shifted).statistic)
    latencies = np.array([2.0, 3.0, 4.0, 8.0, 15.0])
    assert statistic == 1.0 and float(np.quantile(latencies, 0.95, method="higher")) == 15.0
    return {
        "covariate_shift_statistic": statistic,
        "observed_p95_ms": 15.0,
        "quality_requires_labels": True,
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-015 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Monitor operations, data contracts and mature outcomes as distinct signals. Keep their denominators and scopes explicit, and connect each to a reviewed response. The real local service demonstrates actual process metrics and stale-feature rejection without claiming production-scale observability.
