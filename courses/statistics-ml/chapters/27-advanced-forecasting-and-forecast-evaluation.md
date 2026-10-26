# 27. Advanced Forecasting and Forecast Evaluation

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-027`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Advanced forecasting often improves the framing of the task more than the complexity of the model. A retailer may need forecasts that add up from product to category and region, remain useful for sparse demand, describe uncertainty and respect the information available when stock is ordered. A model can minimize one average error while violating all four operational requirements.

### Define the origin, horizon and loss

Let T be the forecast origin and h the horizon. Evaluate y_(T+h) against a forecast built exclusively from data available at T. Direct forecasting fits a separate model for each h; recursive forecasting iterates a one-step model; multihorizon models produce a vector jointly. These approaches share inputs but impose different parameter sharing and error propagation. Use rolling origins and preserve the same forecast availability rules for every candidate.

The preferred forecast depends on the loss. Squared error targets a conditional mean, absolute error a median, and asymmetric pinball loss a quantile. For quantile q, residual \(u=y-\widehat{y}\) has loss \(q\cdot u\) when \(u\ge 0\) and \((q-1)\cdot u\) otherwise. Underforecasting is therefore more expensive at \(q=0.9\). A point estimate called the best forecast is incomplete until the cost of over- and underprediction is specified.

### Coherence is a linear constraint

Write all aggregate and bottom-level series as \(y=Sb\), where b contains bottom-level values and S sums them into the reporting hierarchy. Independently fitted forecasts may not lie in the column space of S. Reconciliation projects them onto that coherent space, using a weighting matrix to express forecast-error uncertainty. Coherence ensures totals agree; it does not create accuracy, nonnegativity or calibrated intervals automatically.

### Evaluate distributions as well as points

A useful predictive distribution should be sharp while calibrated relative to the relevant population. An interval that always spans every plausible value has high coverage but little decision value. Check coverage and width by horizon, subgroup and regime, and use proper scoring rules when comparing full distributions or quantiles. A narrow nominal interval that systematically misses demand spikes is not an improvement.

### A realistic demand workflow

Consider weekly demand for hundreds of items across four stores. Establish seasonal-naive and intermittent-demand baselines, build past-only calendar/lag features, group related series for a global model, and evaluate using repeated historical ordering dates. Forecasts for stockout weeks need a censored-demand model because observed sales cap latent demand. Reconcile store and regional totals, then select quantiles using shortage and holding costs. Compare both operational cost and forecast scores, and retain the assumptions used to predict unavailable future promotion or price inputs.

Neural and other flexible methods enter this workflow as candidates with additional capacity and training cost. Shared learning across series can help short histories, but only when identifiers, scaling, regime differences and validation boundaries are handled deliberately. No architecture eliminates the need for an honest baseline or an independent evaluation period.

## Methods, mechanisms, and limits

### stat-27-01

**Hierarchical forecasting**

Hierarchical forecasting works with nested aggregation, such as products within categories within a company total. The summing matrix S encodes those relationships. Bottom-up, top-down and reconciliation methods use different information and uncertainty assumptions. A top-down allocation can obscure changes in lower-level shares, while bottom-up forecasts can be noisy for sparse items. Evaluate the levels that drive decisions rather than only the grand total.

### stat-27-02

**Grouped forecasting**

Grouped forecasting handles crossed structures, such as totals by both product and region, where a single tree is insufficient. Every marginal aggregation should agree with the same underlying cells. Construct the full aggregation matrix and check redundant relationships before estimation. A method that reconciles only one hierarchy can still produce contradictory totals in another business view.

### stat-27-03

**Forecast reconciliation**

Reconciliation changes base forecasts so they satisfy aggregation constraints. With a linear coherent subspace, projection gives the closest coherent forecast under a chosen distance. The weights determine which forecasts are trusted more. Projection can alter every level, including a good individual forecast, and may produce negative values unless additional constraints are imposed. Compare accuracy and coherence separately.

### stat-27-04

**Minimum-trace reconciliation**

Minimum-trace reconciliation uses the covariance W of base forecast errors to minimize total reconciled error variance under its assumptions. A common form is \(S(S^{\mathsf T}W^{-1}S)^{-1}S^{\mathsf T}W^{-1}\widehat{y}\). Estimating W is difficult with many related series and short history, so shrinkage or structural approximations matter. A mathematically optimal projection using a poor covariance estimate can underperform a simpler method.

### stat-27-05

**Intermittent demand forecasting**

Intermittent demand mixes many zero periods with occasional positive arrivals. Modeling only a continuous conditional mean can miss the distinction between whether demand occurs and how large it is. Evaluate over the inventory lead time, where several periods combine. Zeros caused by stockouts or missing reporting are not equivalent to true no-demand periods and must be classified before fitting.

### stat-27-06

**Croston’s method**

Croston updates separate estimates of positive demand size and intervals between nonzero demands, then forecasts their ratio. Updates occur at demand arrivals rather than every zero period. This makes its dynamics appropriate for sparse series, but the ratio estimator is biased under common assumptions and does not inherently supply a full predictive distribution. It can react slowly when demand stops permanently.

### stat-27-07

**Bias-corrected intermittent methods**

Bias-corrected intermittent methods modify Croston-style estimates or model demand occurrence separately, addressing known bias or obsolescence behavior. The Syntetos-Boylan approximation and TSB illustrate different choices rather than interchangeable labels. Compare them using lead-time losses and changing-demand scenarios. A correction derived under one arrival model does not guarantee better performance for every sparse process.

### stat-27-08

**Dynamic harmonic regression**

Dynamic harmonic regression uses Fourier sine/cosine terms for seasonality and a dynamic error model for remaining dependence. It is useful when seasonal periods are long or several periods coexist. The harmonic count controls seasonal flexibility, while future calendar indices are known. Fit harmonic selection inside each training window and inspect whether changing seasonal shape requires more than fixed coefficients.

### stat-27-09

**TBATS**

TBATS combines transformations, trigonometric seasonality, ARMA errors, trend and possible damping within a state-space framework. It can represent multiple complex seasonalities parsimoniously relative to a huge seasonal lag model. Its flexibility increases computation and makes component identification harder. Compare simpler harmonic or seasonal baselines and examine whether the training history spans enough cycles to estimate the claimed structure.

### stat-27-10

**Piecewise trend models**

Piecewise trend models let slopes change at selected or estimated changepoints. Regularization controls how many changes or how large their effects can be. Retrospective changepoint detection uses information unavailable at the change itself, so evaluate the fitting procedure at each historical origin. Extrapolating the last slope is a substantive assumption, especially after a short-lived shock or measurement revision.

### stat-27-11

**Global forecasting models**

A global forecasting model learns shared parameters from many series, often using identifiers, calendar features and recent history. It can borrow strength for short or sparse series. Scaling, series weighting and train/test partitions determine what is shared and whether large series dominate. A model that sees a future segment from another strongly related series can leak information even when each individual row appears properly lagged.

### stat-27-12

**Local forecasting models**

A local model is fitted separately to each series. It is easy to tailor to distinct dynamics and often interpretable, but short histories provide weak parameter information and maintenance scales with series count. Compare local and global approaches using the same origins and weighting. A global average win may conceal local failures on operationally critical series.

### stat-27-13

**Machine-learning forecasting**

Machine-learning forecasting converts history into supervised features such as lagged targets, rolling summaries and known future calendars. Every rolling feature must be shifted before the forecast target; preprocessing is fitted only on history. Trees and regressors can capture nonlinear interactions but may extrapolate trends poorly. The model is only one component of a complete temporal feature and evaluation pipeline.

### stat-27-14

**Recurrent neural forecasting**

Recurrent forecasting updates hidden state as observations arrive, allowing learned summaries of sequential history. Training often uses windows and teacher forcing, while deployment may feed predictions back into the state. That difference can amplify multistep errors. Sequence lengths, hidden-state resets and series boundaries need explicit handling; backpropagation through a long history does not guarantee the model learns useful long-range dependencies.

### stat-27-15

**Temporal convolutional forecasting**

Temporal convolutional models apply causal filters, often with dilation, so each output sees a bounded historical receptive field. Causality here means no future input enters the computation, not an intervention claim. Dilation increases coverage without a proportionate layer count. Padding mistakes can leak future values, and a receptive field shorter than the relevant seasonal history limits what the model can learn.

### stat-27-16

**Transformer forecasting**

Transformer forecasters use attention to combine positions or variates, with positional and temporal information added explicitly. Masking must respect the forecast information set, including covariate availability. Their flexibility and memory costs require fair comparisons against simpler models and careful scaling. A long context window permits access to history but does not prove that distant information is used accurately or economically.

### stat-27-17

**Neural basis forecasting**

Neural basis forecasting predicts coefficients of basis functions or decomposes output into repeated blocks, sometimes with trend/seasonal interpretations. Restricting the basis can provide useful inductive structure, but an interpretable basis label does not guarantee identifiable physical components. Validate the final forecast and inspect decomposition stability. Generic learned bases trade interpretability for flexibility and still require leakage-free windows.

### stat-27-18

**Probabilistic forecasting**

Probabilistic forecasting estimates quantiles, intervals or a full conditional distribution. It makes uncertainty available to decisions with asymmetric costs or risk constraints. Distributional assumptions, tail behavior and dependence across horizons matter, especially for inventory totals. Independently calibrated marginal quantiles do not automatically produce a coherent joint path distribution or a calibrated aggregate forecast.

### stat-27-19

**Forecast combinations**

Forecast combinations average or stack multiple candidates to reduce model-specific error. Simple averaging is a strong baseline when error correlations are imperfect and weights are hard to estimate. Learned weights need out-of-sample training predictions and may overfit a small validation set. Combining highly correlated models yields limited diversification, and a combined quantile is not generally the same as a mixture-distribution quantile.

### stat-27-20

**Direct multistep forecasting**

Direct multistep forecasting fits a separate target y_(t+h) for each horizon. It avoids feeding prior prediction errors back into later horizons, but uses fewer effective training pairs at large h and can create incoherent horizon-to-horizon behavior. Hyperparameter tuning across many horizons multiplies the selection burden. Evaluate the complete set of horizon models using the same operational origin schedule.

### stat-27-21

**Recursive forecasting**

Recursive forecasting repeatedly applies a one-step model, using earlier predictions as future lag inputs. It shares parameters and is easy to extend to arbitrary horizons, but mistakes and distribution shift can accumulate. Training on observed lags while deploying on predicted lags creates a mismatch. Compare horizon-specific errors and uncertainty, not only the one-step validation score.

### stat-27-22

**Multihorizon forecasting**

Multihorizon forecasting learns several future targets together, sharing representations and sometimes modeling their dependence. Known future covariates can be included at their proper horizons. The loss weights determine which horizons dominate training. Joint output does not automatically guarantee temporal consistency, calibrated path uncertainty or coherence with aggregation constraints; those properties require separate design and checks.

### stat-27-23

**Scenario forecasting**

Scenario forecasting conditions predictions on explicit future paths for drivers, such as price, weather or capacity. It answers what is predicted under those assumptions, not necessarily what an intervention would cause. Separate uncertainty conditional on a scenario from uncertainty about which scenario occurs. State scenario provenance and plausibility rather than presenting one convenient future path as observed fact.

### stat-27-24

**Cold-start forecasting**

Cold-start forecasting predicts for a new series with little or no history using attributes, analogues, shared models or hierarchical priors. The useful similarity measure depends on the demand mechanism. Validation should hold out whole new entities to mimic deployment, not only later rows of known entities. Sparse initial observations can update the forecast, but uncertainty should remain larger when transfer assumptions are weak.

### stat-27-25

**Censored demand estimation**

Censored demand arises when observed sales cannot exceed available inventory or capacity. A zero sale during a stockout is not evidence of zero demand. Likelihood or latent-demand models should use availability and censoring indicators, with identification assumptions about lost sales. Training directly on capped observations can teach the model that constrained periods have low demand and perpetuate understocking.

### stat-27-26

**MASE and RMSSE**

MASE scales mean absolute forecast error by the training-sample error of a naive or seasonal-naive benchmark. RMSSE analogously scales root mean squared error using squared training differences. The denominator must use training data and can be zero for a constant series. Scale-free scores support cross-series comparison, but weighting and undefined-denominator policy determine the resulting operational interpretation.

### stat-27-27

**Pinball loss**

Pinball loss targets a specified conditional quantile. For residual \(u=y-\widehat{q}\), loss is \(\tau\cdot u\) when u is nonnegative and \((\tau-1)\cdot u\) otherwise. At \(\tau=0.9\), underprediction receives nine times the per-unit penalty of overprediction. Quantiles can cross if trained separately, and a low average loss can conceal subgroup miscalibration. Report the quantile level and relevant decision cost.

### stat-27-28

**Continuous ranked probability score**

CRPS compares a predictive cumulative distribution F with the step function at the realized outcome through the integral of [F(z)-1(y<=z)] squared. It is a proper scoring rule for distributions with suitable moments and generalizes absolute error for a point mass. Empirical samples can approximate it. A single average CRPS should still be supplemented with tail and subgroup diagnostics important to the application.

### stat-27-29

**Prediction interval coverage and width**

Interval coverage is the fraction of realized outcomes falling inside an advertised interval; width measures sharpness. Assess both by horizon and meaningful subgroup, because pooled coverage can hide systematic misses. A wider interval can improve coverage without improving usefulness. Calibration requires representative evaluation data and repeated opportunities; one realized outcome cannot validate a nominal 90 percent interval.

### stat-27-30

**Diebold–Mariano tests**

The Diebold-Mariano test compares the mean loss differential of competing forecasts, accounting for serial dependence in that differential. Multistep overlapping forecasts often require a long-run variance estimate. Small samples, nested models and extensive model selection complicate the reference distribution. A significant difference is not automatically operationally important, so report effect size, uncertainty and the tested loss/horizon.

## Worked Python demonstrations

Complete offline program: [chapter_27.py](../examples/chapter_27.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_27.py
```

### Reconcile an inconsistent total

The base total is 100 while its children sum to 90. Under equal-error-variance Euclidean projection, the residual 10 is distributed along the constraint vector [1,-1,-1]: subtract \(\frac{10}{3}\) from the total and add \(\frac{10}{3}\) to each child. The coherent result is approximately [96.667,43.333,53.333]. Different error covariances would allocate the correction differently; coherence alone cannot say which forecast is more accurate.

### Translate error into a decision-specific loss

Training increments are all two, so the MASE scale is two. Forecast errors [2,-2] have MAE two and MASE one. At the 0.9 quantile, the underprediction error two costs 1.8 while the overprediction error minus two costs 0.2. The asymmetric calculation is appropriate only when that quantile or cost ratio is the intended target.

### Check interval claims and information order

Two of three outcomes are inside their intervals, giving empirical coverage two-thirds and average width ten-thirds. The sample is too small to establish population calibration. The same function constructs expanding training windows whose largest index precedes each target, making the no-future-data invariant inspectable rather than relying on a splitter name.

### Complete executable example

```python
import numpy as np


def reconciliation():
    base = np.array([100.0, 40.0, 50.0])
    constraint = np.array([[1.0, -1.0, -1.0]])
    corrected = base - constraint.T @ np.linalg.solve(constraint @ constraint.T, constraint @ base)
    assert np.isclose(corrected[0], corrected[1] + corrected[2])
    assert np.allclose(corrected, [290 / 3, 130 / 3, 160 / 3])
    print("Base total minus children:", (constraint @ base)[0], "reconciled:", corrected)


def losses():
    train = np.array([10.0, 12.0, 14.0, 16.0])
    actual = np.array([18.0, 20.0])
    prediction = np.array([16.0, 22.0])
    error = actual - prediction
    scale = np.mean(np.abs(np.diff(train)))
    mase = np.mean(np.abs(error)) / scale
    q = 0.9
    pinball = np.maximum(q * error, (q - 1) * error)
    assert mase == 1.0 and np.allclose(pinball, [1.8, 0.2])
    print("MASE:", mase, "0.9 pinball losses:", pinball)


def intervals_and_origins():
    actual = np.array([10.0, 15.0, 20.0])
    lo = np.array([8.0, 12.0, 18.0])
    hi = np.array([12.0, 14.0, 22.0])
    covered = (lo <= actual) & (actual <= hi)
    assert covered.tolist() == [True, False, True]
    assert np.isclose(covered.mean(), 2 / 3)
    assert np.isclose(np.mean(hi - lo), 10 / 3)
    origins = [3, 4, 5]
    pairs = [(np.arange(origin + 1), origin + 1) for origin in origins]
    assert all(train.max() < target for train, target in pairs)
    print("Coverage and mean width:", covered.mean(), np.mean(hi - lo), "origins:", origins)


def main():
    reconciliation()
    losses()
    intervals_and_origins()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does reconciliation guarantee better forecasts?** It guarantees the specified aggregation consistency. Accuracy improvement depends on base forecasts, their error covariance and the projection assumptions. Nonnegativity and joint interval calibration are additional requirements, not automatic consequences.

**Interview: Why can a lower RMSE model be wrong for stock decisions?** RMSE targets a conditional mean and penalizes symmetric squared errors. Inventory decisions often have asymmetric shortage and holding costs, implying a different optimal quantile or utility. Evaluate the operational decision and the corresponding predictive target.

**Interview: How would you compare a transformer with seasonal naive?** Use the same historical origins, horizons, available covariates and series weighting. Include preprocessing and tuning inside training windows, evaluate an untouched later period, and report compute cost alongside accuracy, calibration and important segment failures.

## Primary sources and official APIs

- [Hyndman and Athanasopoulos, forecast evaluation and reconciliation](https://otexts.com/fpp3/)

- [Gneiting and Raftery, Strictly Proper Scoring Rules, Prediction, and Estimation](https://doi.org/10.1198/016214506000001437)

## Connected worked tutorial

[A vintage-aware multi-series case](../tutorials/science/03-vintage-aware-forecasting.md). Recreate rolling forecasts using label availability and revision timing, then compare a common baseline.

## Reading connections

[Previous chapter](26-classical-forecasting-methods.md) | [Book contents](../README.md) | [Next chapter](28-survival-analysis-duration-models-and-reliability.md)
