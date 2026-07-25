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
