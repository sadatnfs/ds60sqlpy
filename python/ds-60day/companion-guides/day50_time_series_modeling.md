# Day 50 — Time-Series Modeling and Forecast Evaluation

**Lesson ID:** `python-50` · **Level:** advanced · **Dependencies:** `ml` · **Network:** offline

Forecasting differs from ordinary random-split prediction because the future
must never influence the past. This lesson compares a small `pmdarima` model
against simple time-safe baselines on deterministic synthetic data.

## Learning objectives

By the end of the lesson, you can:

- construct a chronological train/test split with a declared forecast horizon;
- build last-value and seasonal-naive forecasts;
- fit a bounded seasonal ARIMA candidate with `pmdarima`;
- evaluate every candidate on the same timestamps and metric; and
- engineer lags or rolling features without future leakage.

## Prerequisites

- Complete `python-49` (NLP survey).
- Recall pandas time indexes from `python-21`.
- Install the `ml` dependency group, which includes `pmdarima`.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Forecast horizon | Number of future steps predicted |
| Temporal split | Training observations occur before evaluation observations |
| Naive forecast | Simple rule, such as repeating the latest observation |
| Seasonal-naive forecast | Repeats the observation from one seasonal period earlier |
| Lag | Past value aligned as a current-row feature |
| Rolling statistic | Summary over a trailing window |
| Differencing | Subtracting an earlier observation to reduce trend/seasonality |
| ARIMA | Autoregressive integrated moving-average model |
| Backtesting | Repeating forward train/evaluate windows over historical time |

The key boundary is “information available as of forecast time.” A feature can
be mathematically shifted yet still be operationally unavailable because of
reporting delay.

## Worked example: baseline before complexity

```python
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

rng = np.random.default_rng(42)
index = pd.date_range("2020-01-01", periods=300, freq="D")
values = (
    20
    + np.linspace(0, 10, len(index))
    + 2 * np.sin(2 * np.pi * np.arange(len(index)) / 30)
    + rng.normal(scale=1.0, size=len(index))
)
series = pd.Series(values, index=index, name="y")
train, test = series.iloc[:-30], series.iloc[-30:]

last_value = np.repeat(train.iloc[-1], len(test))
seasonal_naive = train.iloc[-30:].to_numpy()
print("last:", mean_absolute_error(test, last_value))
print("seasonal:", mean_absolute_error(test, seasonal_naive))
```

Every candidate must use this same 30-day horizon and metric. A more complex
model earns its cost only if it improves the relevant evidence reliably.

## Learner exercises and progressive hints

1. Fit `auto_arima` with `m=7` and `m=30`; compare mean absolute error on the
   same test window.
2. Create last-value and 30-day seasonal-naive forecasts and compare them with
   ARIMA.
3. Difference the training series and inspect autocorrelation without using
   test-period observations.

### Progressive hints

1. Change only the seasonal period. Keep the split, horizon, and MAE calculation
   fixed, and bound the search if runtime is high.
2. Build each baseline solely from `train`; verify predictions have the same
   index/length as `test`.
3. Call `train.diff().dropna()` before plotting autocorrelation. The test values
   should not appear anywhere in transformation fitting.

The reference solution extends the lesson with `TimeSeriesSplit`, shifted
rolling features, and a seasonal-naive evaluation. It uses a different
synthetic weekly series to reinforce the method rather than mirror the notebook.

### Additional mastery practice

Evaluate forecasts with forward-only information, multiple origins, meaningful baselines, and timestamp/data-quality checks before adding model complexity.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Rolling-origin evaluation:** Implement at least four expanding-window forecast origins with a fixed horizon. Compare seasonal-naive and one candidate model using per-origin and aggregate MAE.
   **Progressive hint:** At each origin, fit using timestamps at or before that origin and score only the next horizon. Preserve origin in the result table.
5. **Prediction intervals:** Produce forecast intervals and evaluate empirical coverage and width across rolling origins. Explain why a narrow interval is not useful when it misses too often.
   **Progressive hint:** For a nominal 90% interval, count actuals between lower and upper bounds and report support plus average width by horizon.
6. **Timestamp/data-quality debugging:** Validate a series containing duplicate timestamps, missing periods, an irregular interval, and a timezone transition before modeling.
   **Progressive hint:** Sort, assert monotonic unique timestamps, infer/declare frequency, and decide aggregation or imputation from domain meaning.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why is a shuffled train/test split invalid for this forecasting question?
- Why must rolling features use `shift(1)` before the window?
- When does MAPE behave badly, and why is MAE safer for values near zero?
- If ARIMA beats the naive baseline once, what additional evidence is needed?

Expected behavior: the synthetic data and all model code run offline. Different
seasonal periods can produce different search time and MAE; complexity is not
guaranteed to win.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Random CV | Future observations train past predictions | Use forward splits/backtests |
| Rolling mean includes current target | Direct leakage | Shift before rolling |
| Comparing different horizons | Metrics are not comparable | Align timestamps and horizon |
| `auto_arima` search left broad | Long CPU runtime/selection noise | Start with bounded orders and a baseline |
| One final window treated as certainty | Result depends on time regime | Backtest multiple origins |
| Forecast intervals ignored | Point prediction looks overconfident | Evaluate coverage and decision uncertainty |

ARIMA encodes a structured temporal process. Tree models on lag features can
capture nonlinearities but require careful recursive forecasting. Select by
backtested evidence, operational latency, and maintainability.

## Next step

- Work in the [Day 50 learner notebook](../notebooks/day50_time_series_modeling.ipynb).
- Then review the
  [Day 50 solution](../solutions/day50_time_series_modeling/day50_solutions.md).
- Continue to [Day 51 — Target Encoding](day51_advanced_feature_engineering_target_encoding.md).
