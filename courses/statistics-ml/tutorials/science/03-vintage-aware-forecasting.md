# Forecast from the information that existed at the cutoff

Tutorial ID: `statistics-science-003`. Prerequisites: `statistics-025`, `statistics-026`, `statistics-027`, `statistics-learning-007`. Complete program: [science_03.py](examples/science_03.py).

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

Reference: [Forecasting: Principles and Practice](https://otexts.com/fpp3/). Related book: [forecast evaluation](../../chapters/27-advanced-forecasting-and-forecast-evaluation.md).
