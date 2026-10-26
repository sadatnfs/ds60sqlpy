# r-049: reference reasoning

Use the [complete reference](r-049_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The fixed-coefficient model isolates forecast arithmetic from parameter estimation. The rolling-origin reference separately verifies that each forecast uses a historical prefix and is scored at the declared next time. This prevents a correct error formula from hiding an invalid information boundary.

The differencing check retains both the new length and changed target. Forecast uncertainty is reported as a property of the fitted model, with its assumptions and omitted uncertainty sources named. No production forecasting claim follows from these synthetic controls.

## Explained practice

### Exercise 1

Derive three forecasts for a zero-mean AR(1) with phi 0.5 and latest value 0.4.

The means are 0.2,0.1 and 0.05.

**Expected evidence:** Exact three-horizon oracle.

### Exercise 2

Explain why an ARIMA order(1,0,0) differs from(0,1,0).

The first is an autoregressive level model; the second differences the series and has a different continuation/mean convention.

**Expected evidence:** Model components and targets distinguished.

### Exercise 3

Construct rolling-origin naive predictions for origins 4 through 7 of 1:8.

Each next value exceeds the last observed value by one, so every error and the MSE are one.

**Expected evidence:** Four records with MSE 1.

### Exercise 4

Diagnose using mean(y) from all eight values at the first origin.

Values after origin 4 have influenced the predictor, violating the declared information boundary.

**Expected evidence:** Future-data leakage identified.

### Exercise 5

Difference the sequence 1:6 and retain the changed length and meaning.

There are five differences, all one. They describe changes rather than six original levels.

**Expected evidence:** Length 5, all differences 1.

### Exercise 6

Interpret forecast SEs without claiming all sources of future error are covered.

SEs belong to the fitted time-series model; misspecification, structural change and model-selection uncertainty need additional assessment.

**Expected evidence:** Finite model SEs with explicit limits.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
