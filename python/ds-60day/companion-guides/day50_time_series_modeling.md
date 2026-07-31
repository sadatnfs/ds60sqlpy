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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 50 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags

### The mental model

Time-series prediction preserves order. A forecast made at an **origin**
may use only information available by that origin and predicts a stated
horizon. Random train/test splitting leaks future patterns and produces
an evaluation that no real forecast can reproduce.

Last-value and seasonal-naive forecasts are strong required baselines.
Lag and rolling features must be shifted so the row at time `t` never
sees the value it is trying to predict. Rolling-origin evaluation repeats
realistic forecast origins and reports performance across time regimes.

### Worked examples and syntax anatomy

- **`series.shift(lag)`:** aligns a past value as a current-row feature; positive lags must precede any rolling summary.
- **`train.iloc[:-horizon]` / `test.iloc[-horizon:]`:** creates a simple chronological boundary with a declared horizon.
- **rolling-origin loop:** repeats fit/predict at increasing origins while keeping every target strictly in the future.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — construct a seasonal-naive forecast on matching timestamps

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

index = pd.date_range("2026-01-01", periods=28, freq="D")
values = pd.Series(np.tile([10, 12, 11, 14, 15, 13, 9], 4), index=index)
horizon, season = 7, 7
train, test = values.iloc[:-horizon], values.iloc[-horizon:]
forecast = pd.Series(train.iloc[-season:].to_numpy(), index=test.index)
print({"mae": mean_absolute_error(test, forecast),
       "forecast_index_matches": forecast.index.equals(test.index)})
assert mean_absolute_error(test, forecast) == 0.0
```

**Expected observation:** The exact weekly pattern gives zero error and the forecast is explicitly aligned to test timestamps.

**Assumption to name:** A seven-day season was available and stable; real data rarely repeat perfectly.

### Focused example B — build a trailing feature that excludes the current target

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import pandas as pd

series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], name="value")
features = pd.DataFrame({
    "target": series,
    "lag_1": series.shift(1),
    "trailing_mean_2": series.shift(1).rolling(2).mean(),
})
print(features)
assert features.loc[3, "trailing_mean_2"] == 25.0
```

**Expected observation:** At row 3, the trailing mean uses rows 1 and 2 (20 and 30), never the current target 40.

**Assumption to name:** Rows are sorted, timestamps are unique, frequency/gaps are understood, and past targets are available at prediction time.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Computing rolling features before shifting or tuning seasonal order against the final horizon.

**Debug it deliberately:** For one prediction timestamp, list the maximum source timestamp for every feature and assert it is no later than the forecast origin.

**Stop condition:** Do not report a forecast metric without horizon, origins, timestamp alignment, baseline, missing-period policy, and leakage audit.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Fit `auto_arima` with `m=7` and `m=30`; compare mean absolute error on the
   same test window.

**Verify:** Practice 1 — forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags — fit m=7 and m=30 using training observations only, forecast the identical timestamped test window, and print MAE plus errors by horizon for both; report convergence/skip status and selected seasonal period.

2. Create last-value and 30-day seasonal-naive forecasts and compare them with
   ARIMA.

**Verify:** Practice 2 — forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags — on the same forecast origins, print MAE for last-value, 30-day seasonal-naive, and ARIMA; assert each forecast at time t uses only observations before t and include a metric table keyed by model.

3. Difference the training series and inspect autocorrelation without using
   test-period observations.

**Verify:** Practice 3 — forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags — difference only the training series, print its length/NaN handling and selected autocorrelations with confidence bounds, and assert no test-period timestamp entered the transform or lag calculation.

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

**Verify:** Rolling-origin evaluation — print at least four forecast origins with train-end, horizon timestamps, seasonal-naive MAE, candidate MAE, and aggregate weighted MAE; assert every prediction uses data strictly before its origin.

5. **Prediction intervals:** Produce forecast intervals and evaluate empirical coverage and width across rolling origins. Explain why a narrow interval is not useful when it misses too often.
   **Progressive hint:** For a nominal 90% interval, count actuals between lower and upper bounds and report support plus average width by horizon.

**Verify:** Prediction intervals — print interval level, per-origin coverage indicator, aggregate empirical coverage, and mean width; compare at least two interval widths/levels and flag severe undercoverage.

6. **Timestamp/data-quality debugging:** Validate a series containing duplicate timestamps, missing periods, an irregular interval, and a timezone transition before modeling.
   **Progressive hint:** Sort, assert monotonic unique timestamps, infer/declare frequency, and decide aggregation or imputation from domain meaning.

**Verify:** Timestamp/data-quality debugging — produce a validation report listing duplicate timestamps, exact missing periods, irregular gaps, timezone/ambiguous transitions, frequency, and chosen repair; assert the cleaned index is unique, ordered, and regular before modeling.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-50` — Day 50 — Time-Series Modeling and Forecast Evaluation.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize forecast horizons, temporal backtesting, naive baselines, and leakage-safe lags. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day50_time_series_modeling.md`
- learner artifact: `python/ds-60day/notebooks/day50_time_series_modeling.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-49`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
