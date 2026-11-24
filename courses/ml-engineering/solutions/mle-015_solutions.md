# mle-015: explained reference

Monitor operations, data contracts and mature outcomes as distinct signals.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Move the monitoring cutoff

Record the cutoff and cohort identities. Comparing different maturity stages without adjustment can create a misleading trend.

At cutoff 5 only predictions 1 and 3 have labels (available at 3 and 5), giving coverage 0.5 and Brier 0.085 from (0.1-0)^2 and (0.6-1)^2. Move the cutoff to 8 and all four labels arrive; prediction 2 (score 0.9, label 1) and prediction 4 (score 0.2, label 0) join. Plotting Brier at cutoff 5 next to Brier at cutoff 8 as if they were two weeks of the same population would be wrong, because the evaluated rows differ.

**Expected:** Newly available labels change the evaluated population.

## 2. Test outcome-dependent delay

Investigate delay by outcome and cohort, and use an appropriate evaluation design. Do not assume missing-at-random labels without evidence.

In the fixture the label for prediction 2, the one positive scored 0.9, arrives at time 7, later than both mature rows. If positives systematically arrive late, the early mature set is enriched for negatives and the early Brier describes an easier population. Group label delay by label value and compare.

**Expected:** Early observed quality can be biased.

## 3. Interpret drift

Inspect data contracts and evaluate mature outcomes when available. A changed distribution can be harmless, harmful or even beneficial depending on the model and task.

Example_two shifts every baseline value by 10, so the KS statistic is 1.0 with a two-sample p-value near 0.008. That says the distributions differ; it says nothing about Brier, because no label enters the calculation. Treating the alarm as proof of degraded quality would skip the mature-label check.

**Expected:** It establishes a difference under the tested sample/comparison, not performance loss.

## 4. Record metric scope

Aggregate with suitable identities and windows when designing a real service. Preserve reset/restart behavior in the interpretation.

np.quantile on the five latencies with method="higher" returns 15.0 ms, while the default linear method returns 13.6 ms. State the method, the five-sample window and that the array belongs to one process, otherwise two dashboards can disagree about the same requests.

**Expected:** The scope is explicit.

## 5. Choose an action

Use a reviewed reject, fallback, investigation or rollback policy. Avoid silently continuing with invalid inputs while reporting healthy service status.

Name the input, the threshold and the response, for example "reject requests whose region is outside the schema and page the owner". An alert that only increments a counter while /health stays 200 lets invalid inputs keep flowing.

**Expected:** The response is specific and bounded.

## 6. Keep uncertainty visible

Retain counts and distributional context, then collect representative observations for a meaningful service objective or comparison.

With five latencies the 0.95 quantile is essentially the maximum: one slow request moves it from 8 to 15 ms. Report n=5 beside the value so readers see how little evidence stands behind it.

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

Keep their denominators and scopes explicit, and connect each to a reviewed response. The real local service demonstrates actual process metrics and stale-feature rejection without claiming production-scale observability.
