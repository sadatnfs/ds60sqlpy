# Day 50 — Time Series Modeling (Companion Guide)

## Learning objectives
- Establish baselines (naive, seasonal naive) and proper splits
- Engineer lag/rolling features; use TimeSeriesSplit
- Fit ARIMA/Prophet or tree models and compare

## Why this matters
Good baselines and leakage-aware validation are crucial for credible forecasts.

## Core concepts and examples
### Baselines and split
```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
split = TimeSeriesSplit(n_splits=5)
# naive forecast
y_pred = y.shift(1)  # last value
```

### Lag/rolling features
```python
df['lag1'] = df['y'].shift(1)
df['roll7'] = df['y'].rolling(7).mean()
```

### ARIMA (statsmodels)
```python
import statsmodels.api as sm
model = sm.tsa.ARIMA(y, order=(1,1,1)).fit()
fc = model.forecast(steps=14)
```

## Common pitfalls
- Random CV on time series; use temporal splits
- Target leakage from future-derived features (like centered rolling)
- Optimizing MSE when business cares about MAPE or pinball loss

## Practice exercises
1) Implement seasonal naive baseline and beat it
2) Use TimeSeriesSplit and compare models across folds
3) Evaluate with MAPE and visualize errors over time

## Further reading
- statsmodels tsa: https://www.statsmodels.org/stable/tsa.html
- sktime: https://www.sktime.net
