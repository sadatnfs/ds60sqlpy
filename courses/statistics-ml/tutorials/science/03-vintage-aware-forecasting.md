# Forecast from the information that existed at the cutoff

Tutorial ID: `statistics-science-003`. Prerequisites: `statistics-025`, `statistics-026`, `statistics-027`, `statistics-learning-007`. Complete program: [science_03.py](examples/science_03.py).

## Key terms

- **Forecast origin:** The cutoff time from which forecasts are made; training may use only labels already available at that time.
- **Label delay:** The gap between an event and the availability of its outcome, two months in the example, which limits the usable training history.
- **Rolling-origin evaluation:** Repeating the fit-and-forecast procedure at several origins to evaluate the operational procedure rather than one split.
- **As-of value:** The latest version of a record available at a given cutoff, found by filtering on availability before choosing the latest version.
- **Last-value baseline:** A naive forecast that repeats the most recent available observation, used as a reference for the fitted model.

## Define the forecasting job

There are three related series, each with 60 monthly observations, a linear trend, annual seasonality and noise. At each chosen origin, forecast the next three months. The toy outcome becomes available two months after its event time. This delay determines which observations a deployed model can actually use, even when a historical file contains all values today.

For an origin o, require \(t+2\le o\) for training labels. The code asserts that condition before fitting. Future timestamps are known, so their trend and seasonal basis functions can be constructed without reading future outcomes. A predictor that depends on a future realized price or revised target would need its own availability check.

## Fit and compare two complete procedures

The model uses an intercept, time, sine and cosine with period twelve. Each series gets its own least-squares coefficients using only available history. A last-value forecast uses the most recent available observation. Both predict the same horizons at the same six origins; neither is tuned on the final forecast errors.

The model's RMSE is about .372 across 54 forecasted outcomes, while the last-value baseline's RMSE is about 4.245. This strong result reflects a synthetic process that matches the seasonal linear model. It does not establish the model is best for real series with changing seasonality, intermittent demand or structural breaks.

Rolling origins evaluate a repeated operational procedure. Forecast errors for overlapping horizons can be dependent. These particular origins are six months apart with a three-month horizon, avoiding target overlap, but series may still share shocks. An uncertainty interval should preserve the relevant time and cross-series dependence rather than treating all printed errors as independent rows.

## Revisions create a second clock

A value for event 10 arrives at time 12 with value one, then is revised at time 20 to value 99. At cutoff 15, only the first version existed. Filter records by availability before selecting the latest version per event. Reversing that order can choose the revision first and then drop it, losing the valid original, or can leak it into the past.

The example uses an event/availability/value table and verifies the as-of value is one. A current warehouse table containing only the latest values cannot reconstruct a historical information boundary without additional version history. Perfect event timestamps are insufficient when the data became available later.

## Extend the scientific question

For staffing, use a decision loss that reflects shortage and surplus rather than only squared error. For aggregate demand, reconcile forecasts to a known hierarchy and evaluate both the aggregate and components. For prediction intervals, estimate uncertainty from an appropriate residual/parameter or probabilistic model and assess empirical coverage by horizon; a point forecast plus a constant arbitrary band is not calibrated uncertainty.

A backtest should record origins, label delay, revision policy, horizon, refitting schedule, baseline and loss definition. Those choices define the procedure being evaluated. A final live period is separate evidence about the actual delivery system and current environment.

**Answered discussion: Is retraining on every origin leakage?** No, when each fit uses only information available at that origin and matches the deployment schedule. Selecting the model family repeatedly from the same backtest can still overfit evaluation decisions and should be reported.

## Worked example: error by forecast horizon

The guide reports one pooled RMSE. Splitting the same rolling-origin errors from `examples/science_03.py` by horizon shows which forecasts carry most of the advantage.

```python
import numpy as np


def design(t):
    return np.column_stack(
        [np.ones(len(t)), t, np.sin(2 * np.pi * t / 12), np.cos(2 * np.pi * t / 12)]
    )


rng = np.random.default_rng(2703)
t = np.arange(60)
series = [
    10 + lv + tr * t + 3 * np.sin(2 * np.pi * t / 12) + rng.normal(scale=0.4, size=60)
    for lv, tr in ((0, 0.1), (4, 0.2), (-2, 0.05))
]
for horizon in (1, 2, 3):
    model, last = [], []
    for origin in range(24, 55, 6):
        train, target = np.arange(origin - 1), origin + horizon - 1
        for v in series:
            beta = np.linalg.lstsq(design(train), v[train], rcond=None)[0]
            model.append((design(np.array([target])) @ beta)[0] - v[target])
            last.append(v[train[-1]] - v[target])
    print(
        f"horizon {horizon}: model RMSE {np.sqrt(np.mean(np.square(model))):.3f} "
        f"last-value RMSE {np.sqrt(np.mean(np.square(last))):.3f}"
    )
```

```text
horizon 1: model RMSE 0.400 last-value RMSE 2.815
horizon 2: model RMSE 0.347 last-value RMSE 4.266
horizon 3: model RMSE 0.367 last-value RMSE 5.287
```

The seasonal model stays near the noise level at every horizon, 0.400, 0.347 and 0.367, because its trend and cycle are correct and the extra months do not add parameter error of note. The last-value baseline degrades steadily, from 2.815 one month ahead to 5.287 three months ahead, because the seasonal swing of amplitude three accumulates with distance from the last observation. With the two-month label delay, even the first horizon is two steps beyond the most recent label, which is why the naive baseline is already poor at horizon one.

## Worked example: the order of the as-of operations

The guide warns that deduplicating before filtering by availability loses valid history. Running both orders on the three-row revision table makes the loss concrete.

```python
import pandas as pd

rev = pd.DataFrame({"event": [10, 10, 11], "available": [12, 20, 13], "value": [1, 99, 2]})
right = rev[rev.available <= 15].sort_values("available").drop_duplicates("event", keep="last")
wrong = rev.sort_values("available").drop_duplicates("event", keep="last")
wrong = wrong[wrong.available <= 15]
print("filter then dedupe:", right[["event", "value"]].values.tolist())
print("dedupe then filter:", wrong[["event", "value"]].values.tolist())
```

```text
filter then dedupe: [[10, 1], [11, 2]]
dedupe then filter: [[11, 2]]
```

Filtering to rows available by time 15 and then keeping the latest version gives event 10 the value 1 and event 11 the value 2, the information a forecaster actually had. Deduplicating first keeps the time-20 revision of event 10, which the cutoff then removes, so event 10 disappears from the snapshot entirely. A backtest built that way silently trains on fewer events than production had, and in a join it can turn into missing features that the model never saw historically.

## Failure modes in forecast backtests

Using the final revised value for past periods leaks future information even if every timestamp looks right. Forgetting the label delay overstates short-horizon skill. Pooling all horizons into one RMSE hides where the model fails. Comparing against a weak baseline only, such as last value on strongly seasonal data, makes any seasonal model look excellent; add a seasonal naive baseline when the cycle is known.

Reference: [Forecasting: Principles and Practice](https://otexts.com/fpp3/). Related book: [forecast evaluation](../../chapters/27-advanced-forecasting-and-forecast-evaluation.md).
