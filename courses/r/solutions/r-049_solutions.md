# r-049: reference reasoning

Run the [complete reference](r-049_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The fixed-coefficient model isolates forecast arithmetic from parameter estimation. The rolling-origin reference separately verifies that each forecast uses a historical prefix and is scored at the declared next time. This prevents a correct error formula from hiding an invalid information boundary.

The differencing check retains both the new length and changed target. Forecast uncertainty is reported as a property of the fitted model, with its assumptions and omitted uncertainty sources named. No production forecasting claim follows from these synthetic controls.

## Explained practice

### Exercise 1

Derive three forecasts for a zero-mean AR(1) with phi 0.5 and latest value 0.4.

The means are 0.2,0.1 and 0.05.

**Expected evidence:** Exact three-horizon oracle.

**Approach:** Start from the last observation, 0.4, and multiply by phi = 0.5 once for each additional horizon.

**Why it holds here:** With a zero mean AR(1), the expected next value is phi times the current one, so the forecasts are 0.2, 0.1 and 0.05. Fixing phi at 0.5 removes estimation, so the arithmetic can be checked exactly.

**Tempting mistake:** Applying phi once and repeating 0.2 for all three horizons. That ignores that each forecast feeds the next, and it keeps the forecast from decaying toward the zero mean.

**Verify:** `max(abs(as.numeric(f$pred) - c(0.2, 0.1, 0.05)))` returns a value below 1e-10.

### Exercise 2

Explain why an ARIMA order (1,0,0) differs from (0,1,0).

The first is an autoregressive level model; the second differences the series and has a different continuation/mean convention.

**Expected evidence:** Model components and targets distinguished.

**Approach:** Write each model as an equation for this series and compare the three forecasts each implies.

**Why it holds here:** order = c(1, 0, 0) models the level, y equals 0.5 times the previous y plus noise, so forecasts shrink toward 0. order = c(0, 1, 0) models the change, which has mean zero, so every forecast stays at the last level, 0.4.

**Tempting mistake:** Treating both as one lag models that should agree. At horizon 3 one forecast is 0.05 and the other is 0.4, eight times larger.

**Verify:** `predict(arima(y, order = c(0, 1, 0)), n.ahead = 3)$pred` returns 0.4 three times, against 0.2, 0.1 and 0.05 for the AR(1).

### Exercise 3

Construct rolling-origin naive predictions for origins 4 through 7 of 1:8.

Each next value exceeds the last observed value by one, so every error and the MSE are one.

**Expected evidence:** Four records with MSE 1.

**Approach:** For each origin from 4 to 7, slice `series[seq_len(origin)]`, forecast its last value, and score against `series[origin + 1]`.

**Why it holds here:** The predictions are 4, 5, 6 and 7 and the actual next values are 5, 6, 7 and 8, so every error is 1 and the MSE is 1. Each forecast sees only values up to its origin.

**Tempting mistake:** Slicing `seq_len(origin + 1)`, which puts the target inside the training prefix. The last value is then the actual one, so all four errors become 0.

**Verify:** `all(actual - predictions == 1)` returns TRUE and `mean((actual - predictions)^2)` returns 1.

### Exercise 4

Diagnose using mean(y) from all eight values at the first origin.

Values after origin 4 have influenced the predictor, violating the declared information boundary.

**Expected evidence:** Future-data leakage identified.

**Approach:** At origin 4, compute any fitted summary from `series[1:4]` only, then compare it with the summary computed on all eight values.

**Why it holds here:** The honest mean is 2.5 and the full mean is 4.5. Predicting time 5, where the actual value is 5, the full mean gives error 0.5 instead of 2.5, because values 5 to 8 were already inside it.

**Tempting mistake:** Calling `mean(y)` once before the loop and reusing it at every origin. The forecast looks better than any real forecaster could do at time 4.

**Verify:** `mean(series) != mean(series[1:4])` returns TRUE, comparing 4.5 with 2.5.

### Exercise 5

Difference the sequence 1:6 and retain the changed length and meaning.

There are five differences, all one. They describe changes rather than six original levels.

**Expected evidence:** Length 5, all differences 1.

**Approach:** Apply diff to 1:6, record that the result has one fewer element, and label it as changes.

**Why it holds here:** Each change uses two neighboring levels, so 6 levels give 5 changes, all equal to 1. A model fitted to these values forecasts the next change, and a level forecast needs the last level, 6, added back.

**Tempting mistake:** Binding the changes next to the original six levels in one data frame. The lengths 5 and 6 differ, so a row would be filled, recycled or rejected, and change 1 might be read as level 1.

**Verify:** `length(changes)` returns 5 and `all(changes == 1)` returns TRUE.

### Exercise 6

Interpret forecast SEs without claiming all sources of future error are covered.

SEs belong to the fitted time-series model; misspecification, structural change and model-selection uncertainty need additional assessment.

**Expected evidence:** Finite model SEs with explicit limits.

**Approach:** Report `f$se` beside each forecast and list what the standard errors do not include.

**Why it holds here:** With phi fixed at 0.5, the forecast variance grows as sigma squared times 1, 1.25 and 1.3125 over the three horizons. These numbers come from the AR(1) equation alone.

**Tempting mistake:** Reading forecast plus or minus 2 SE as covering all future error. Here phi was fixed rather than estimated, so the SE leaves out coefficient uncertainty entirely, along with any change in the process after time 8.

**Verify:** `all(is.finite(f$se))` and `all(f$se >= 0)` return TRUE.

## What the checks establish

The assertions confirm forecasts of 0.2, 0.1 and 0.05 with finite, nonnegative standard errors, rolling-origin naive predictions on 1 to 8 whose errors are all 1 with mean squared error 1, a full-series mean that differs from the mean available at an early origin, five unit changes in a differenced trend, and origins that always precede their targets. They do not show that the series is stationary or that the model is well chosen.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
