# 26. Classical Forecasting Methods

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-026`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A forecast is a conditional distribution for future observations, not merely an extrapolated line. Begin with a baseline whose assumptions you can explain, then add structure only when past-only validation supports it. The last observation is a strong baseline for a random walk, while the same seasonal position is often stronger for a stable seasonal process. A more complicated method must outperform the appropriate baseline over the horizons and losses that matter.

### Recursions make model assumptions visible

Simple exponential smoothing updates a level through \(\ell_t=\alpha y_t+(1-\alpha)\ell_{t-1}\). Here alpha is between zero and one and determines responsiveness: a larger alpha discounts history faster. Holt adds a trend state; Holt-Winters adds seasonal state. A state is an unobserved summary updated by new information. Different error, trend and seasonal specifications imply different likelihoods and forecast distributions even if point-recursion notation looks similar.

ARIMA starts from lag relations and differencing. An AR(1) with intercept c obeys \(y_t=c+\phi y_{t-1}+\epsilon_t\). If \(|\phi|<1\), its long-run mean is \(\frac{c}{1-\phi}\), and forecasts shrink toward that mean rather than automatically toward zero. A moving-average time-series model uses past innovations; it is not the moving window used for smoothing a chart. Confusing these two meanings leads to wrong implementations.

### State estimation and uncertainty

A linear Gaussian state-space model writes \(x_t=Fx_{t-1}+w_t\) and \(y_t=Hx_t+v_t\). The latent state x may include level, trend or other components, while Q and R describe process and observation noise covariance. Kalman filtering first predicts the state and covariance, then uses the innovation to update them. Smoothing conditions on future observations too, making it appropriate for retrospective state reconstruction but not a real-time forecasting feature without refitting.

### Select the whole forecasting procedure

Specify transformations, missing-value handling, seasonal periods, regressor availability, order search and uncertainty construction before evaluating. Residual checks diagnose an assumed mechanism, while rolling-origin forecasts assess utility. Conditional forecasts with future regressors known by assumption should be distinguished from operational forecasts requiring those regressors to be predicted. Model uncertainty and regime changes are not automatically covered by a narrow conditional interval.

## Methods, mechanisms, and limits

### stat-26-01

**Naive forecasts**

The naive forecast sets every future point to the latest observed value. It is the conditional mean under a zero-drift random walk, making it a principled baseline rather than a trivial mistake. Its uncertainty grows with horizon under that model. It performs poorly when stable seasonality or a predictable deterministic trend dominates, but should remain in the comparison whenever persistence is strong.

### stat-26-02

**Seasonal naive forecasts**

Seasonal naive forecasting repeats the most recent observation from the same seasonal position. For period m, horizon h maps back to the appropriate point in the last complete season. It assumes that seasonal structure persists without a new trend correction. Missing seasonal positions, holidays and changing cadence need explicit rules. Compare forecasts at each relevant horizon rather than one aggregate score.

### stat-26-03

**Drift forecasts**

The drift method adds h times the average historical increment to the latest value: y_T+h*(y_T-y_1)/(T-1). It extrapolates the endpoint slope and therefore depends strongly on unusual first or last observations. The method is a useful trend baseline, but a structural break or saturating process makes indefinite linear extrapolation implausible. Record the fitting window as part of the method.

### stat-26-04

**Moving-average smoothing**

A moving-average smoother replaces each observation with an average over a chosen window. A trailing window is available online; a centered window uses later observations and is retrospective. The window suppresses short fluctuations but delays response to a real change. This operation is different from an MA(q) stochastic model, which combines current and past innovations rather than observed values.

### stat-26-05

**Simple exponential smoothing**

Simple exponential smoothing maintains a weighted level with weights decaying geometrically into the past. Alpha near one follows recent values closely; alpha near zero changes slowly. It is suitable when level varies but persistent trend/seasonality are absent or already modeled. Initial level and alpha affect early results. A point recursion needs an associated error model to produce calibrated prediction intervals.

### stat-26-06

**Holt’s method**

Holt updates both level and slope, then forecasts \(l_{T}+h\cdot b_{T}\). The trend update estimates how the level is changing after adjusting for the previous slope. This separates a gradual increase from noise more flexibly than endpoint drift. Undamped extrapolation can become unrealistic at long horizons, so inspect slope stability and compare a damped alternative under the same validation origins.

### stat-26-07

**Holt–Winters methods**

Holt-Winters adds seasonal states to level and trend. Additive seasonality is natural for constant-sized seasonal effects; multiplicative seasonality models effects proportional to the level and imposes data constraints. The seasonal period and initialization need enough history. Zero or negative values complicate multiplicative forms. Good in-sample seasonal fit does not ensure a stable future seasonal shape.

### stat-26-08

**Damped-trend methods**

A damped trend forecasts with b_T times the sum \(\phi+\phi^2+\cdots+\phi^h\) for damping factor \(0<\phi<1\). The total trend contribution approaches a finite limit as horizon increases, unlike linear extrapolation. This is a modeling choice about long-run behavior, not a universal correction. Estimate and validate damping over useful horizons, especially when short history cannot identify it well.

### stat-26-09

**ETS models**

ETS organizes exponential-smoothing models by error, trend and seasonality components. A state-space formulation supplies a likelihood and forecast distribution rather than only smoothing equations. Additive and multiplicative errors produce different uncertainty behavior. Candidate restrictions, numerical initialization and information criteria affect selection. Compare the selected procedure out of sample and reject models incompatible with the data support.

### stat-26-10

**Autoregressive models**

An AR(p) predicts from p earlier observations plus an innovation. Its lag-polynomial roots determine stationarity; coefficient magnitudes cannot be inspected independently for p greater than one. Conditional forecasts recursively replace unknown future lags with forecasts. An apparent high-order fit can absorb trend or seasonality that should be modeled directly. Check residual dependence and use time-ordered validation.

### stat-26-11

**Moving-average time-series models**

An MA(q) time-series model writes \(y_t=\mu+\epsilon_t+\sum_{j=1}^{q}\theta_j\epsilon_{t-j}\). Past errors, not past observed values, form the dependence mechanism. Invertibility identifies a stable representation of innovations from observations. Once the horizon exceeds q, known past innovations no longer affect the conditional mean, although forecast uncertainty remains.

### stat-26-12

**ARMA models**

ARMA combines autoregressive persistence and a finite moving-average innovation structure for a stationary process. AR and MA terms can nearly cancel, making parameters hard to identify and encouraging unnecessarily complex fits. Residual independence assumptions still matter. Use a modest candidate set and examine uncertainty or instability of coefficients instead of interpreting every fitted term as a physical mechanism.

### stat-26-13

**ARIMA models**

ARIMA(p,d,q) applies an ARMA model to a series differenced d times. Differencing changes the target and the implied long-run behavior, while forecasts must be integrated back to levels. Intercept or drift handling depends on differencing and software convention. Over-differencing can increase noise and distort dependence. Verify model equations and residual behavior rather than selecting orders mechanically.

### stat-26-14

**Seasonal ARIMA**

Seasonal ARIMA adds lag-m autoregressive/moving-average terms and possibly seasonal differences, commonly written (p,d,q)(P,D,Q)_m. The seasonal period is a substantive cadence choice. Seasonal and ordinary differencing interact, and a short history may not identify all parameters. Multiple seasonalities or calendar effects may be better handled through regression terms instead of an oversized lag polynomial.

### stat-26-15

**Dynamic regression**

Dynamic regression combines explanatory variables with time-correlated errors or lagged effects. Future regressor values must be available, scheduled or forecast under explicit assumptions. A good fit using realized future weather or promotions can leak information unavailable at prediction time. Regression coefficients also remain associational unless a separate causal design supports intervention interpretation.

### stat-26-16

**Distributed-lag models**

A distributed-lag model includes x_t,x_(t-1),... to represent an effect spread across time. Lag coefficients can be highly collinear, so smoothness restrictions or regularization may improve stability. Their sum often describes a cumulative response under a sustained shift, subject to the full dynamic model. Choose lags using timing mechanisms and validation rather than searching until one coefficient is significant.

### stat-26-17

**Transfer-function models**

A transfer-function model expresses an input-output relation using lag-polynomial filters, often with autocorrelated residual noise. It can represent delayed and decaying responses parsimoniously. Identification requires careful prewhitening and separating common trends from input response. Future inputs still need a scenario or forecast. A fitted dynamic relationship is not automatically an experimentally identified causal transfer.

### stat-26-18

**Vector autoregression**

Vector autoregression predicts each variable using lags of all variables in a system. With k variables and p lags, parameter counts grow quickly, making small-sample overfitting a serious issue. Stability, lag order and innovation covariance influence forecasts. Impulse responses require a shock-identification convention and should not be interpreted causally from an unrestricted covariance matrix alone.

### stat-26-19

**Vector error-correction models**

A vector error-correction model represents changes while including stationary long-run combinations of integrated levels. The adjustment coefficients describe how variables respond to disequilibrium. Cointegration rank and deterministic terms determine the model. Incorrect rank or unsupported equilibrium restrictions can distort forecasts and interpretation. It is appropriate when both short-run dynamics and long-run level relationships are substantively justified.

### stat-26-20

**State-space models**

A state-space model separates latent system evolution from noisy observations. The transition equation controls how the hidden state changes, while the observation equation maps it to measurements. This formulation handles missing observations and multiple components naturally when assumptions are specified. State interpretation and identifiability depend on the parameterization; two decompositions can fit similarly while telling different stories.

### stat-26-21

**Kalman filtering**

Kalman filtering updates a linear Gaussian state using the innovation \(y_t-Hx_{\mathrm{pred}}\) and gain \(K=P_{\mathrm{pred}}H^{\mathsf T}(HP_{\mathrm{pred}}H^{\mathsf T}+R)^{-1}\). Higher measurement noise lowers the weight on the observation. The covariance update quantifies remaining state uncertainty under the model. Nonlinearity, heavy tails or misspecified noise covariance require additional methods or robustness checks.

### stat-26-22

**Kalman smoothing**

Kalman smoothing estimates past states conditional on a later complete observation set, using a backward pass after filtering. It usually reduces retrospective uncertainty because more information is available. That is useful for reconstructing a latent trajectory, but smoothed states leak future information if used as historical online features. Compare filtering and smoothing as different conditioning problems, not competing implementations.

### stat-26-23

**Structural time-series models**

Structural time-series models assign separate stochastic states to level, trend, seasonality and other interpretable components. Their disturbance variances control how quickly each component can change. If several flexible components explain the same variation, decomposition may be weakly identified. Use domain constraints and inspect posterior or likelihood uncertainty rather than presenting a unique latent story as observed fact.

### stat-26-24

**Bayesian structural time series**

Bayesian structural time series places priors over states, variances and often regression inclusion. Forecast distributions integrate parameter and state uncertainty under those priors. For counterfactual applications, credible causal interpretation additionally requires unaffected controls, stable relationships and an intervention design. A posterior interval from a forecasting model alone does not establish identification of an intervention effect.

### stat-26-25

**Dynamic linear models**

Dynamic linear models use time-varying linear states and coefficients, often with Bayesian sequential updating or discount factors. A coefficient can evolve instead of remaining fixed across the entire history. Greater adaptivity trades stability for responsiveness. The evolution variance or discount choice is consequential and should be calibrated by forecast behavior, especially around sparse data and regime changes.

### stat-26-26

**ARCH and GARCH**

ARCH/GARCH models describe conditional variance, often while conditional mean follows a separate model. A GARCH(1,1) uses \(\sigma_t^2=\omega+\alpha\epsilon_{t-1}^2+\beta\sigma_{t-1}^2\), with positivity constraints and suitable persistence conditions. Volatility clustering can exist with nearly zero return autocorrelation. Heavy-tailed innovations, leverage effects and structural changes require checking beyond the variance recursion.

## Worked Python demonstrations

Complete offline program: [chapter_26.py](../examples/chapter_26.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_26.py
```

### Compare assumptions on one visible series

For [10,12,14,16], naive predicts [16,16,16], drift predicts [18,20,22], and \(\alpha=0.5\) smoothing ends at 14.25. The level trace is 10,11,12.5,14.25. Smoothing lags this deterministic rise because it has no trend state. These are different structural assumptions, not contradictory arithmetic.

### Follow autoregressive shrinkage

With intercept two and phi one-half, the long-run mean is four. Starting from ten, repeated conditional forecasts are 7,5.5,4.75,4.375. The sequence approaches four rather than zero. Every step substitutes a conditional expectation for an unobserved future lag; uncertainty would need its own recursion.

### Weight a noisy measurement

A prior mean zero with variance four meets measurement three with variance one. Gain \(\frac{4}{4+1}=0.8\) gives posterior mean 2.4 and variance 0.8. Raising measurement variance to sixteen reduces gain to 0.2. The update demonstrates how uncertainty controls trust, conditional on a correctly specified linear Gaussian model.

### Separate mean and variance prediction

A shock of three enters GARCH through its square, nine. With \(\omega=0.1\), \(\alpha=0.2\), \(\beta=0.7\) and previous variance one, the next variance is 2.6. The calculation says volatility rises; it does not predict whether the next signed return will be positive.

### Complete executable example

```python
import numpy as np

def baselines_and_smoothing():
    y=np.array([10.,12.,14.,16.]);h=np.arange(1,4)
    naive=np.repeat(y[-1],3);drift=y[-1]+h*(y[-1]-y[0])/(len(y)-1)
    level=y[0]
    for value in y[1:]:level=.5*value+.5*level
    assert naive.tolist()==[16.,16.,16.]
    assert drift.tolist()==[18.,20.,22.] and level==14.25
    print("Naive:",naive,"drift:",drift,"SES level:",level)

def recursive_ar():
    phi=.5;intercept=2.;current=10.;forecast=[]
    for _ in range(4):
        current=intercept+phi*current;forecast.append(current)
    assert np.allclose(forecast,[7.,5.5,4.75,4.375])
    assert intercept/(1-phi)==4.
    print("AR forecasts:",forecast,"long-run mean:",4.)

def scalar_kalman():
    prior_mean=0.;prior_variance=4.;measurement=3.;measurement_variance=1.
    gain=prior_variance/(prior_variance+measurement_variance)
    posterior=prior_mean+gain*(measurement-prior_mean)
    variance=(1-gain)*prior_variance
    assert np.isclose(gain,.8) and np.isclose(posterior,2.4) and np.isclose(variance,.8)
    noisy_gain=4/(4+16)
    assert noisy_gain<gain
    print("Kalman gain, posterior mean, variance:",gain,posterior,variance)

def volatility_update():
    omega,alpha,beta=.1,.2,.7
    next_variance=omega+alpha*3**2+beta*1.
    assert np.isclose(next_variance,2.6) and alpha+beta<1
    print("Variance after shock 3:",next_variance)

def main():
    baselines_and_smoothing();recursive_ar();scalar_kalman();volatility_update()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Is moving-average smoothing an MA model?** No. Smoothing averages observed values in a window. An MA time-series model combines current and past innovations. Their recursions, parameter interpretation and forecast distributions differ.

**Interview: Why can smoothing leak information?** A retrospective smoother conditions a past state on observations that arrived later. Real-time forecasting can use only filtered states computed from the information available at the origin. The difference is the conditioning set, not whether the code is deterministic.

**Interview: How should a forecast using external variables be evaluated?** Reconstruct the future values actually available at each origin, or forecast them using past data. Label scenario forecasts conditional on assumed inputs separately. Evaluating with realized future covariates measures an easier task than deployment.

## Primary sources and official APIs

- [Hyndman and Athanasopoulos, exponential smoothing, ARIMA and dynamic regression](https://otexts.com/fpp3/)

- [statsmodels state-space tools](https://www.statsmodels.org/stable/statespace.html)

## Reading connections

[Previous chapter](25-time-series-foundations-and-diagnostics.md) | [Book contents](../README.md) | [Next chapter](27-advanced-forecasting-and-forecast-evaluation.md)
