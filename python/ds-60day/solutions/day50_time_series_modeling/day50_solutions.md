# Day 50 — Solutions: Time Series Modeling

We implement seasonal naive baselines, leakage‑safe feature engineering with TimeSeriesSplit, and evaluation with MAPE including error visualization.

Contents
- Exercise 1: Seasonal naive baseline and beat it
- Exercise 2: Use TimeSeriesSplit and compare models
- Exercise 3: Evaluate with MAPE and visualize errors

---

Setup
```python
import pandas as pd, numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error as MAPE
import matplotlib.pyplot as plt

# Example daily data with weekly seasonality
rng = pd.date_range('2020-01-01', periods=400, freq='D')
np.random.seed(0)
y = 10 + 2*np.sin(2*np.pi*rng.dayofyear/7) + np.random.normal(0,0.8,len(rng))
df = pd.DataFrame({'ds': rng, 'y': y}).set_index('ds')
```

Exercise 1 — Seasonal naive baseline
```python
# 7-day seasonal naive: forecast y_t = y_{t-7}
H = 14  # horizon
df['y_lag7'] = df['y'].shift(7)
valid = df.iloc[-(H+7):]  # ensure lag available
baseline_fc = valid['y_lag7'].iloc[-H:]
truth = valid['y'].iloc[-H:]
base_mape = MAPE(truth, baseline_fc)
print({'baseline_MAPE': float(base_mape)})
```
Explanation
- Use last week’s value as forecast; compute MAPE on final horizon
- Always align lags to avoid peeking into the future

---

Exercise 2 — TimeSeriesSplit and models
```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Feature engineering with leakage‑safe lags and rolling means
df['lag1'] = df['y'].shift(1)
df['lag7'] = df['y'].shift(7)
df['roll7'] = df['y'].shift(1).rolling(7).mean()
df = df.dropna()

X = df[['lag1','lag7','roll7']].values
y = df['y'].values

split = TimeSeriesSplit(n_splits=5)
res = []
for tr, va in split.split(X):
    Xtr, Xva = X[tr], X[va]
    ytr, yva = y[tr], y[va]
    # Models
    lr = LinearRegression().fit(Xtr, ytr)
    rf = RandomForestRegressor(n_estimators=300, random_state=0).fit(Xtr, ytr)
    # Predictions
    p_lr = lr.predict(Xva); p_rf = rf.predict(Xva)
    res.append({
        'mape_lr': MAPE(yva, p_lr),
        'mape_rf': MAPE(yva, p_rf)
    })

cv = pd.DataFrame(res)
print(cv.describe().loc[['mean','std']])
```
Line‑by‑line
- shift(1) on rolling mean prevents leakage (uses only past values)
- TimeSeriesSplit preserves order; no shuffling
- Compare models with average MAPE over folds

---

Exercise 3 — Final fit and error visualization
```python
# Fit best model on full train and forecast last H steps using a walk‑forward loop
H = 14
train = df.iloc[:-H].copy(); test = df.iloc[-H:].copy()

model = RandomForestRegressor(n_estimators=500, random_state=0).fit(train[['lag1','lag7','roll7']], train['y'])
fc = model.predict(test[['lag1','lag7','roll7']])
print('Test MAPE vs baseline:', MAPE(test['y'], fc), 'vs', base_mape)

plt.figure(figsize=(8, 3))
plt.plot(df.index[-120:], df['y'].iloc[-120:], label='actual')
plt.plot(test.index, fc, label='forecast')
plt.legend(); plt.title('Forecast vs actual'); plt.tight_layout(); plt.show()

# Error over time
err = pd.Series(fc, index=test.index) - test['y']
err.plot(title='Forecast error'); plt.axhline(0,color='k',lw=1); plt.show()
```
Notes
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

### Reasoning notes for original Exercise 1

**Prompt:** Fit `auto_arima` with `m=7` and `m=30`; compare mean absolute error on the same test window.

**How to reason about it:** Compare seasonal periods on the identical training window and forecast horizon. Bound auto-ARIMA search, report runtime, and remember that the best period may change across forecast origins.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Fit autoarima with m=7 and m=30; compare mean absolute error on the same test window`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 2

**Prompt:** Create last-value and 30-day seasonal-naive forecasts and compare them with ARIMA.

**How to reason about it:** Last-value and seasonal-naive forecasts are required baselines. Build them only from information available at each origin and align prediction indices exactly with the test targets.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Create last-value and 30-day seasonal-naive forecasts and compare them with ARIMA`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 3

**Prompt:** Difference the training series and inspect autocorrelation without using test-period observations.

**How to reason about it:** Differencing and autocorrelation diagnostics use training data only. Inspect stationarity assumptions and avoid differencing mechanically without understanding what must be inverted for forecasts.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Difference the training series and inspect autocorrelation without using test-period observat...`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.








### Exercise 4 — Rolling-origin evaluation

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

**Verify:** For task `Implement at least four expanding-window forecast origins with a fixed horizon. Compare seaso...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Exercise 5 — Prediction intervals

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

**Verify:** For task `Produce forecast intervals and evaluate empirical coverage and width across rolling origins....`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.








### Exercise 6 — Timestamp/data-quality debugging

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

**Verify:** For task `Validate a series containing duplicate timestamps, missing periods, an irregular interval, an...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.
