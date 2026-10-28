# Day 50: Solutions: Time Series Modeling

We compare a seasonal-naive baseline and recursive lag models on the same
fixed 14-step forecast horizon. Four development origins select a candidate
before one final holdout evaluation. All values are course-authored synthetic data.

Contents
- Exercise 1: Seasonal naive baseline and beat it
- Exercise 2: Use TimeSeriesSplit and compare models
- Exercise 3: Evaluate with MAPE and visualize errors

---

Setup
```python
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error as MAPE
import matplotlib.pyplot as plt

# Course-authored synthetic daily values, not observed business data.
dates = pd.date_range("2020-01-01", periods=400, freq="D")
rng = np.random.default_rng(50)
values = 10 + 2 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
values = values + rng.normal(0, 0.8, len(dates))
df = pd.DataFrame({"y": values}, index=dates)
H = 14
# Reserve the final window before feature fitting, CV, or model selection.
development = df["y"].iloc[:-H].copy()
test = df["y"].iloc[-H:].copy()
assert development.index.max() < test.index.min()
assert (df["y"] > 0).all()  # MAPE is suitable for this positive fixture only.
```

Worked reference for Exercise 1; Seasonal naive baseline
```python
def seasonal_naive_forecast(history, future_index, season=7):
    """Repeat the final observed season from one fixed forecast origin."""
    if len(history) < season or season < 1:
        raise ValueError("a complete positive-length season is required")
    if len(future_index) and history.index[-1] >= future_index[0]:
        raise ValueError("forecast timestamps must follow the observed history")
    repeated = np.resize(history.iloc[-season:].to_numpy(), len(future_index))
    return pd.Series(repeated, index=future_index, name="seasonal_naive")


baseline_fc = seasonal_naive_forecast(development, test.index)
assert baseline_fc.index.equals(test.index)
# Days 8-14 repeat the same observed week, never actual values from days 1-7.
np.testing.assert_array_equal(baseline_fc.iloc[:7], baseline_fc.iloc[7:])
```
Explanation
- Repeat only the final observed week for the entire 14-step horizon.
- The baseline and candidate use the same origin and target timestamps.
- Actual test targets are read only when scoring or plotting the final forecasts.

---

Worked reference for Exercise 2; TimeSeriesSplit and models
```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

FEATURES = ["lag1", "lag7", "roll7"]


def make_lag_table(history):
    return pd.DataFrame(
        {
            "lag1": history.shift(1),
            "lag7": history.shift(7),
            "roll7": history.shift(1).rolling(7).mean(),
            "target": history,
        }
    ).dropna()


def recursive_forecast(model, history, future_index):
    """Feed prior predictions back as lags; future actuals are not an input."""
    if len(history) < 7:
        raise ValueError("at least seven observed values are required")
    if len(future_index) and history.index[-1] >= future_index[0]:
        raise ValueError("forecast timestamps must follow the observed history")
    known = history.to_numpy(dtype=float).tolist()
    predictions = []
    for timestamp in future_index:
        features = pd.DataFrame(
            [{"lag1": known[-1], "lag7": known[-7], "roll7": np.mean(known[-7:])}],
            index=[timestamp],
        )
        prediction = float(model.predict(features[FEATURES])[0])
        if not np.isfinite(prediction):
            raise ValueError("model produced a nonfinite prediction")
        predictions.append(prediction)
        known.append(prediction)
    return pd.Series(predictions, index=future_index, name="forecast")


model_factories = {
    "linear": LinearRegression,
    "forest": lambda: RandomForestRegressor(
        n_estimators=80, max_depth=6, random_state=50, n_jobs=1
    ),
}
# Four 14-step expanding origins stay entirely inside the development window.
split = TimeSeriesSplit(n_splits=4, test_size=H)
results = []
for train_positions, valid_positions in split.split(development):
    history = development.iloc[train_positions]
    truth = development.iloc[valid_positions]
    assert history.index.max() < truth.index.min() < test.index.min()
    training = make_lag_table(history)
    for name, factory in model_factories.items():
        candidate = factory().fit(training[FEATURES], training["target"])
        forecast = recursive_forecast(candidate, history, truth.index)
        results.append({"model": name, "origin": history.index[-1], "mape": MAPE(truth, forecast)})
    naive = seasonal_naive_forecast(history, truth.index)
    results.append(
        {"model": "seasonal_naive", "origin": history.index[-1], "mape": MAPE(truth, naive)}
    )
cv = pd.DataFrame(results)
mean_mape = cv.groupby("model")["mape"].mean()
# Choose between candidates using development origins, never final test metrics.
selected_name = mean_mape.loc[list(model_factories)].idxmin()
print({"development_mape": mean_mape.to_dict(), "selected_model": selected_name})
```
Line by line
- Shifted features are constructed from each training prefix only.
- Each recursive step uses observations before the origin or earlier predictions.
  A shifted test feature table would instead assume newly observed test targets.
- [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
  supplies four expanding development prefixes; each following window has 14 targets.
- The final 14 rows are outside every selection fold. Mean development MAPE
  chooses a candidate; the seasonal baseline remains a separate comparison.

---

Worked reference for Exercise 3; Final fit and error visualization
```python
training = make_lag_table(development)
model = model_factories[selected_name]().fit(training[FEATURES], training["target"])
fc = recursive_forecast(model, development, test.index)
assert fc.index.equals(test.index) and baseline_fc.index.equals(test.index)
base_mape = MAPE(test, baseline_fc)
print(
    {
        "forecast_origin": str(development.index[-1]),
        "horizon": H,
        "selected_model": selected_name,
        "test_mape": float(MAPE(test, fc)),
        "seasonal_naive_mape": float(base_mape),
    }
)

plt.figure(figsize=(8, 3))
plt.plot(df.index[-120:], df["y"].iloc[-120:], label="actual")
plt.plot(test.index, fc, label="recursive forecast")
plt.plot(test.index, baseline_fc, label="seasonal naive")
plt.legend()
plt.title("Fourteen-step forecasts from one fixed origin")
plt.tight_layout()
plt.show()

err = fc - test
plt.figure(figsize=(8, 3))
plt.plot(err.index, err.to_numpy())
plt.title("Forecast error by target timestamp")
plt.axhline(0, color="k", lw=1)
plt.show()
```
Notes
- A candidate is not guaranteed to beat the baseline; retain both scores.
- MAPE is used only because this fixture stays strictly away from zero.
- Prefer pinball/quantile loss for asymmetric costs
- For multi-step forecasting, compare direct and recursive strategies with
  validated ARIMA or lag-feature baselines before adding a heavier model

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`series.shift(lag)`:** aligns a past value as a current-row feature; positive lags must precede any rolling summary.
2. **`train.iloc[:-horizon]` / `test.iloc[-horizon:]`:** creates a simple chronological boundary with a declared horizon.
3. **rolling-origin loop:** repeats fit/predict at increasing origins while keeping every target strictly in the future.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Chronological baselines establish the task, while shifted features and rolling origins reproduce what information was available.

**Useful alternative:** Exponential smoothing, regression with lags, or domain-specific state-space models may be preferable to automated ARIMA search.

**Trade-off:** Longer training windows provide more data but may include stale regimes; shorter windows adapt faster with higher variance.

**Edge case to test:** Duplicate/missing timestamps, time zones, daylight-saving changes, insufficient seasonal history, and exogenous data publication delays need policies.

**Evidence of correctness:** Assert timestamp ordering/alignment and feature-source cutoffs, beat last/seasonal naive on identical origins, and report errors by origin plus uncertainty.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1: Original lesson practice

**Prompt:** Fit `auto_arima` with `m=7` and `m=30`; compare mean absolute error on the same test window.

**How to reason about it:** Compare seasonal periods on the identical training window and forecast horizon. Bound auto-ARIMA search, report runtime, and remember that the best period may change across forecast origins.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1; forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags; fit m=7 and m=30 using training observations only, forecast the identical timestamped test window, and print MAE plus errors by horizon for both; report convergence/skip status and selected seasonal period.

### Exercise 2: Original lesson practice

**Prompt:** Create last-value and 30-day seasonal-naive forecasts and compare them with ARIMA.

**How to reason about it:** Last-value and seasonal-naive forecasts are required baselines. Build them only from information available at each origin and align prediction indices exactly with the test targets.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2; forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags; on the same forecast origins, print MAE for last-value, 30-day seasonal-naive, and ARIMA; assert each forecast at time t uses only observations before t and include a metric table keyed by model.

### Exercise 3: Original lesson practice

**Prompt:** Difference the training series and inspect autocorrelation without using test-period observations.

**How to reason about it:** Differencing and autocorrelation diagnostics use training data only. Inspect stationarity assumptions and avoid differencing mechanically without understanding what must be inverted for forecasts.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3; forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags; difference only the training series, print its length/NaN handling and selected autocorrelations with confidence bounds, and assert no test-period timestamp entered the transform or lag calculation.

### Exercise 4: Rolling-origin evaluation

**Prompt:** Implement at least four expanding-window forecast origins with a fixed horizon. Compare seasonal-naive and one candidate model using per-origin and aggregate MAE.

**Reasoning before implementation:** At each origin, fit using timestamps at or before that origin and score only the next horizon. Preserve origin in the result table.

One holdout period can favor a model by chance or season. A tidy result table
should contain model, origin, horizon step, actual, prediction, and absolute
error. Aggregate by model and also inspect variation across origins.

Never fit one candidate on the full series and slice its in-sample predictions
for earlier origins. That uses future observations and invalidates the
backtest.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Rolling-origin evaluation; print at least four forecast origins with train-end, horizon timestamps, seasonal-naive MAE, candidate MAE, and aggregate weighted MAE; assert every prediction uses data strictly before its origin.

### Exercise 5: Prediction intervals

**Prompt:** Produce forecast intervals and evaluate empirical coverage and width across rolling origins. Explain why a narrow interval is not useful when it misses too often.

**Reasoning before implementation:** For a nominal 90% interval, count actuals between lower and upper bounds and report support plus average width by horizon.

Coverage and sharpness must be read together. A trivially wide interval can
cover nearly everything, while an overconfident narrow interval misses often.
Report coverage by horizon because uncertainty usually grows farther ahead.

Model-based intervals rely on residual/distribution assumptions. Residual
bootstrap or conformal methods offer alternatives, but still require
forward-only calibration data and exchangeability assumptions.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Prediction intervals; print interval level, per-origin coverage indicator, aggregate empirical coverage, and mean width; compare at least two interval widths/levels and flag severe undercoverage.

### Exercise 6: Timestamp/data-quality debugging

**Prompt:** Validate a series containing duplicate timestamps, missing periods, an irregular interval, and a timezone transition before modeling.

**Reasoning before implementation:** Sort, assert monotonic unique timestamps, infer/declare frequency, and decide aggregation or imputation from domain meaning.

Do not let a library silently reinterpret irregular observations as regular.
Create an expected date range, compare it with observed timestamps, and report
duplicates/missing periods. Aggregate duplicates only with a documented rule.

Timezone-aware series should be normalized deliberately, often to UTC for
storage while retaining local-calendar features separately. Imputation is a
fitted or policy step and must not read future values in a forecasting
evaluation.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Timestamp/data-quality debugging; produce a validation report listing duplicate timestamps, exact missing periods, irregular gaps, timezone/ambiguous transitions, frequency, and chosen repair; assert the cleaned index is unique, ordered, and regular before modeling.
