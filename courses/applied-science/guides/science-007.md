# science-007: Forecast vintages, revision histories and overlapping origins

Tutorial mode. Stage: intermediate. Direct prerequisites: `statistics-022`, `statistics-026`.

## A backtest is a reconstruction of historical information

A forecast predicts an outcome that is not yet known at a particular origin. A credible historical evaluation must reconstruct the records that were available at that origin. Event time says when a measurement belongs in the world; availability time says when an analyst could have used it. Revisions add another dimension because the latest value today may differ from the value first reported.

Represent a record as \((t,a,v)\), with event time \(t\), availability time \(a\), and value \(v\). At cutoff \(c\), first retain records with \(a\le c\). Then select the latest eligible record for each event. Reversing those operations can discard a valid older record or introduce a later revision. A single current-value table cannot reproduce this history after earlier versions are overwritten.

The tiny fixture follows an exact linear series: 10,12,14,16,18. An event-two value of 14 is later revised to 50. This extreme revision makes leakage visible. It is a teaching contrast, not a realistic claim about the frequency or magnitude of revisions in an operational dataset.

## Key terms

- **Vintage:** The version of a series exactly as it was available at a specific information cutoff.
- **Availability time:** When an analyst could first use a record, as distinct from the event time at which the measurement belongs in the world.
- **Revision:** A later value for the same event time that replaces the first report and must not leak into an earlier forecast origin.
- **Overlapping horizons:** Forecasts from different origins that share target times, which makes their errors dependent.

## Worked case 1: a vintage-aware forecast

At cutoff four, the available series through event three is 10,12,14,16. Least squares fits its trend and extrapolates event four to 18. The `as_of` function filters by availability and sorts by event/availability to construct the valid snapshot. Its explicit assertions verify both the older and current values of the revised event.

If the revised event-two value is leaked into the historical training table, the same extrapolation changes to 36. A revision to another time point can have different leverage, so the program tests the actual numerical contrast rather than assuming every corrupted input must change every prediction. This matters in test design: a fixture that accidentally leaves the result unchanged does not demonstrate protection against the intended defect.

The model is deliberately simple. The purpose is to establish an information contract that applies equally to a sophisticated forecasting system. A model with excellent backtest loss can still be unusable if the features, labels or revisions used during fitting were unavailable at forecast time. Model selection should compare procedures that obey the same cutoff rules.

## Worked case 2: overlapping horizons create dependence

Forecasts issued at origins two and three for horizons one and two include a shared target time. The program lists the origin/horizon/target triples and proves that the number of unique targets is smaller than the number of forecast errors. Treating those errors as independent observations would overstate how much distinct evidence was collected.

There are several distinct questions. Accuracy for a particular horizon should usually be summarized by horizon. Accuracy for a repeated operational schedule may weight origins and horizons according to their use. A deployment decision may instead depend on a cost function, capacity limit or service level. Specify that aggregation before examining model rankings.

For uncertainty about performance, preserve the relevant dependence with a time-aware or cluster-aware method. Resampling individual errors arbitrarily can break shared-target and serial structure. A block length is also a modeling choice: a very short block may ignore dependence, while a long block leaves few effectively independent pieces of evidence. Report sensitivity rather than treating one resampling configuration as a universal answer.

## Separate fitting, selection and final assessment

A rolling-origin backtest emulates repeated refitting, but it does not automatically supply a pristine final test. If its results are repeatedly used to choose features, model families or thresholds, it becomes part of model selection. A final untouched period or a deliberately nested temporal procedure provides a different layer of evidence.

Record the origin schedule, training window, revision policy, label delay, covariate availability, refitting cadence and losses. A future calendar indicator can be known in advance; a future realized price or weather observation usually cannot be substituted without an explicit forecast or scenario. Exogenous regressors require the same information audit as the target.

Numerical accuracy is not the only operational criterion. Forecasts must arrive before the decision deadline, handle missing updates and preserve versioned inputs. An immutable prediction record should link its origin, source snapshot, model version and decision. Otherwise a later revised warehouse can make an incorrect historical forecast appear correct or prevent a good one from being reproduced.

## Answered scientific discussion

**Should all revised data be excluded forever?** No. At a later origin, a revision that is already available can legitimately enter training. The requirement is to reproduce what was known at each origin, not to prohibit useful information.

**Does the example prove that linear regression is a good forecaster?** It proves that a linear procedure recovers a deliberately linear fixture under a valid information snapshot. Its larger lesson is procedural: changing the information boundary can dominate the apparent choice of forecasting algorithm.

## Worked example: As-of reconstruction from a revision log

```python
import pandas as pd

log = pd.DataFrame(
    {
        "period": [1, 2, 2, 3, 3, 3, 4],
        "released": [2, 3, 5, 4, 5, 7, 5],
        "value": [100, 104, 110, 103, 108, 109, 112],
    }
)


def as_of(origin):
    known = log[log.released <= origin]
    return known.sort_values("released").groupby("period").value.last()


for origin in (4, 5, 7):
    print(f"vintage at origin {origin}:", as_of(origin).to_dict())

latest = as_of(99)
truth_period_4 = 112
naive_from_vintage = as_of(4).iloc[-1]  # last known level at origin 4
naive_from_latest = latest.loc[3]  # what a revised backtest would use
print(
    "forecast for period 4 from vintage 4:",
    naive_from_vintage,
    "error",
    truth_period_4 - naive_from_vintage,
)
print(
    "forecast for period 4 from latest data:",
    naive_from_latest,
    "error",
    truth_period_4 - naive_from_latest,
)
```

Observed output:

```text
vintage at origin 4: {1: 100, 2: 104, 3: 103}
vintage at origin 5: {1: 100, 2: 110, 3: 108, 4: 112}
vintage at origin 7: {1: 100, 2: 110, 3: 109, 4: 112}
forecast for period 4 from vintage 4: 103 error 9
forecast for period 4 from latest data: 109 error 3
```

The log has seven rows but only four periods, because periods 2 and 3 were revised after their first release. At origin 4 the analyst knew period 2 as 104 and period 3 as 103; period 4 had not been released at all. By origin 5 both earlier periods had been revised upward, to 110 and 108, and period 4 appeared at 112. Origin 7 adds one more revision, period 3 to 109. A naive last-value forecast of period 4 made at origin 4 had only 103 available and missed by 9. A backtest that rebuilds that same forecast from the latest table uses 109 and appears to miss by only 3. The two-thirds reduction in error is pure leakage: the revised value of period 3 was not known until origin 7, three periods after the forecast was due. Any backtest that reads the final table rather than calling an as-of function inherits this optimism, and its size depends on how large and how directional the revisions are.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def as_of(records, cutoff):
    eligible = [r for r in records if r[1] <= cutoff]
    latest = {}
    for event, available, value in sorted(eligible, key=lambda r: (r[0], r[1])):
        latest[event] = value
    return latest


def run_cases():
    records = [(0, 1, 10.0), (1, 2, 12.0), (2, 8, 50.0), (2, 3, 14.0), (3, 4, 16.0), (4, 5, 18.0)]
    old = as_of(records, 4)
    current = as_of(records, 9)
    assert old[2] == 14 and current[2] == 50

    def extrapolate(values):
        t = np.array(sorted(values))
        y = np.array([values[k] for k in t])
        return float(np.polyval(np.polyfit(t, y, 1), 4))

    vintage = extrapolate(old)
    leaked = extrapolate({k: v for k, v in current.items() if k <= 3})
    assert np.isclose(vintage, 18) and not np.isclose(leaked, 18)
    # Overlapping two-step forecasts reuse a target and must not be iid resampled.
    targets = [(origin, horizon, origin + horizon) for origin in (2, 3) for horizon in (1, 2)]
    assert len({r[2] for r in targets}) < len(targets)
    return dict(
        vintage_forecast=vintage,
        revised_backtest=leaked,
        unique_targets=len({r[2] for r in targets}),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-007 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Forecasting: Principles and Practice, reconciliation](https://otexts.com/fpp3/reconciliation.html)
- [Forecasting principles, accuracy](https://otexts.com/fpp3/accuracy.html)
