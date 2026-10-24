# 25. Time-Series Foundations and Diagnostics

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-025`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Time-series analysis begins by preserving information order. Let y_t denote an observation made at time t, and let F_t contain the information actually available by that time. A forecast of y_(t+h) must depend only on F_t. A smooth curve fitted retrospectively may use later observations and therefore solve a different problem from forecasting. Recording event time, availability time, cadence, missing periods and revisions is part of the statistical model.

### Dependence changes uncertainty

For n observations with common variance \({\sigma}^{2}\) and lag-h correlation rho_h, \(\operatorname{Var}(\bar{Y})=\frac{\sigma^2}{n}\left[1+2\sum_{h=1}^{n-1}\left(1-\frac{h}{n}\right)\rho_h\right]\). Positive serial correlation increases variance relative to independent observations. This is why randomly shuffling adjacent rows can exaggerate both effective sample size and validation performance. The formula assumes a covariance-stationary setting; a strong evolving trend needs separate treatment.

### Stationarity is a model property with several meanings

Strict stationarity asks whether every finite joint distribution is invariant to shifting time. Weak stationarity asks for a constant finite mean and a covariance depending only on lag. The second is often sufficient for linear forecasting tools, but neither says observations are independent. A stationary AR(1) can have strong dependence. A deterministic trend plus stationary noise can be detrended, while a random walk requires a different argument because shocks persist.

### Diagnose before transforming

Plot the series, align missing timestamps, inspect lag and seasonal patterns, then select transformations that match a hypothesis. First differencing turns a linear deterministic trend into a constant increment. Seasonal differencing compares the same seasonal position across cycles. Applying both mechanically can over-difference a stable series and manufacture negative correlation. Unit-root tests depend on deterministic terms, lag choices, sample size and structural breaks; they are pieces of evidence rather than automatic preprocessing switches.

The demonstrations isolate exact algebraic mechanisms: differencing a trend-plus-season fixture, locating a known Fourier frequency, and enforcing past-only feature availability. They deliberately avoid interpreting a tiny manufactured sequence as evidence for a real stochastic model.

## Methods, mechanisms, and limits

### stat-25-01

**Temporal dependence**

Temporal dependence means observations carry information about one another across time. In an AR(1), \(y_t=\phi y_{t-1}+\epsilon_t\), a shock influences later observations through powers of phi. Inspect dependence at the same cadence used by the decision, and keep entire related trajectories together in validation. Treating hourly measurements as independent can understate uncertainty even when the sample contains millions of rows.

### stat-25-02

**Strict stationarity**

Strict stationarity requires the joint law of (Y_t1,...,Y_tk) to equal that of (Y_(t1+h),...,Y_(tk+h)) for every finite selection and shift h. It concerns distributions, not whether a plotted line looks flat. Changes in tail behavior can violate it while the mean remains constant. Empirical diagnostics can challenge plausible stationarity, but finite data cannot prove all such distributional equalities.

### stat-25-03

**Weak stationarity**

Weak stationarity requires finite second moments, constant \(\mathbb{E}[Y_t]=\mu\) and \(\operatorname{Cov}(Y_t,Y_{t-h})=\gamma(h)\). It supports covariance-based tools such as ACF analysis and linear prediction. A constant mean alone is insufficient if variance changes. Strict stationarity with finite second moments implies weak stationarity; weak stationarity need not imply strict stationarity outside special families such as jointly Gaussian processes.

### stat-25-04

**Trend**

A trend is sustained change in the series level over the analysis window. A deterministic trend is modeled through functions of time; a stochastic trend accumulates innovations. Removing a fitted straight line and differencing a random walk address different mechanisms. Inspect whether residual behavior and forecast errors support the chosen treatment, especially near endpoints where estimated trends are least stable.

### stat-25-05

**Seasonality**

Seasonality repeats at a known calendar-related period, such as hours within a day or months within a year. Additive seasonality has roughly constant amplitude; multiplicative descriptions scale amplitude with level and need suitable positive data or transformations. Holidays and variable month lengths are not identical to a fixed numeric period. Use multiple complete cycles and preserve future calendar information without using future outcomes.

### stat-25-06

**Cycles**

Cycles are rises and falls without a fixed calendar period. Economic expansions and contractions can vary in duration and amplitude, so a seasonal dummy with a fixed frequency may describe them poorly. A spectral peak can suggest repeated oscillation but does not establish a stable forecastable cycle. Distinguish a domain mechanism from an attractive pattern discovered after inspecting many candidate periods.

### stat-25-07

**Autocorrelation functions**

The autocorrelation function \(\rho(h)=\frac{\gamma(h)}{\gamma(0)}\) describes linear association between values h steps apart. Estimate it after addressing relevant level changes and missing timestamps. Slow ACF decay can arise from persistence, trend or a unit root, so it does not uniquely identify a model. Standard reference bands depend on assumptions and multiple-lag inspection is not one isolated hypothesis test.

### stat-25-08

**Partial autocorrelation functions**

Partial autocorrelation at lag h measures the remaining linear association after intermediate lags are controlled. For a correctly specified finite-order AR process, the theoretical PACF truncates after its order; finite samples do not exhibit a perfect cutoff. Estimation methods and high-lag sample size matter. Use PACF patterns to propose a few models, then compare residuals and forward validation.

### stat-25-09

**White noise**

White noise has constant mean, constant finite variance and zero autocovariance at nonzero lags in its weak definition. It need not be independent: a sequence can have uncorrelated values but dependent squares. Residual ACF near zero therefore does not prove the absence of volatility clustering. Gaussian white noise adds stronger distributional structure that should not be assumed merely from the label.

### stat-25-10

**Differencing**

First differencing forms \(\Delta y_t=y_t-y_{t-1}\), removing one unit of integration in appropriate models and converting a deterministic linear trend into a constant. It loses the first observation and changes the forecast target, so predictions must be integrated back to levels. Differencing stationary noise can introduce negative lag-one correlation and increase noise. Choose differencing using a model argument and residual/forecast evidence.

### stat-25-11

**Seasonal differencing**

Seasonal differencing forms y_t-y_(t-m) for period m. It cancels an exactly repeating seasonal component, but a trend can remain as a nonzero seasonal increment. The first m observations are lost. Combining ordinary and seasonal differences consumes further information and can over-difference. A wrong seasonal period removes the wrong comparison and can leave structured residuals.

### stat-25-12

**Unit roots**

A unit root in an autoregressive polynomial makes shocks persistent rather than geometrically decaying. A random walk \(y_t=y_{t-1}+\epsilon_t\) has variance growing with t and is not covariance-stationary. Near-unit-root stationary processes can resemble it in short samples. The distinction affects long-horizon uncertainty and whether level relationships require cointegration analysis, not just which button transforms the data.

### stat-25-13

**Augmented Dickey–Fuller tests**

The augmented Dickey-Fuller regression tests a unit-root null using a lagged level and enough lagged differences to handle residual dependence. A constant or trend term changes the null/alternative specification and critical values. Rejecting the null supports the chosen stationary alternative under the test assumptions. Failure to reject can reflect weak power; lag selection and structural breaks should be reported.

### stat-25-14

**KPSS tests**

KPSS starts from a null of level or trend stationarity and examines cumulative residual behavior relative to a long-run variance estimate. Its null differs from ADF, so the two can offer complementary evidence. Results depend on bandwidth and deterministic-term choice. If both tests reject their respective nulls, consider breaks, misspecification or finite-sample limitations instead of declaring a logical contradiction.

### stat-25-15

**Cointegration**

Cointegration occurs when individually integrated series have a stationary linear combination, such as \(y_{t}-\beta\cdot x_{t}\). The combination represents an equilibrium relation even though levels wander. Regressing unrelated trending series can look convincing without cointegration. Define integration order, deterministic terms and testing method, then use an error-correction model when short-run changes adjust toward a supported long-run relation.

### stat-25-16

**Granger causality**

Granger causality asks whether past X improves prediction of Y beyond the included past information. It is a conditional predictive statement, not proof that intervening on X changes Y. Omitted common drivers, measurement timing and model order can create misleading results. Align availability times and compare the restricted and expanded forecasting models under assumptions appropriate to the series properties.

### stat-25-17

**Cross-correlation analysis**

Cross-correlation compares X_t with Y_(t+h) across lags. Shared trends or strong autocorrelation can generate broad apparent lead-lag patterns without a meaningful direct relationship. Prewhitening or a joint dynamic model may clarify the comparison. State the lag sign convention explicitly, because different tools reverse it, and never use a variable whose measurement is only available after the forecast origin.

### stat-25-18

**Spectral analysis**

Spectral analysis represents second-order variation by frequency rather than lag. A frequency in cycles per observation converts to a period by taking its reciprocal. This is useful for oscillations and multiple seasonalities, but sampling cadence limits identifiable frequencies and irregular timing requires different methods. Detrending, windowing and domain plausibility matter before treating a frequency peak as a stable mechanism.

### stat-25-19

**Periodograms**

A periodogram estimates power from squared Fourier coefficients. Its raw values can be noisy even with long samples, so smoothing or averaging often stabilizes interpretation. Finite windows cause leakage when an oscillation does not align with a Fourier bin. A spike at zero frequency may reflect the mean or trend rather than a meaningful cycle. Report frequency units and preprocessing.

### stat-25-20

**Fourier representations**

Fourier terms \(\sin(\frac{2\cdot \pi\cdot k\cdot t}{m})\) and \(\cos(\frac{2\cdot \pi\cdot k\cdot t}{m})\) encode smooth periodic components with period m and harmonic k. Regression coefficients set amplitude and phase. A small number of harmonics can represent long seasonal periods parsimoniously, while too many terms can fit noise. Future time indices are known, but choosing harmonics using the full future evaluation period leaks model-selection information.

### stat-25-21

**Wavelet analysis**

Wavelets localize variation in both time and scale using translated, rescaled basis functions. They can reveal transient oscillations or abrupt local changes that a global Fourier representation spreads over time. Boundary handling, wavelet family and scale resolution affect conclusions. A visually sharp coefficient is not automatically an anomaly; calibrate it against a stated noise model and multiple-scale inspection.

### stat-25-22

**Time-series decomposition**

Decomposition writes a series as trend, seasonal and remainder components, often additively as \(y_t=T_t+S_t+R_t\). This is a representation, not a unique physical separation. Smoothing choices change each component, and a small remainder does not guarantee forecastability. Retrospective centered smoothers use future observations, so refit decomposition within each forecast origin for honest forecasting evaluation.

### stat-25-23

**STL decomposition**

STL estimates seasonal and trend components using locally weighted regression and can reduce the influence of outliers through robust iterations. It allows evolving seasonal shapes, but requires an appropriate regular cadence and period. Endpoint components have different information support from interior components. In forecasting, fit the decomposition only on history and specify how the extracted components will be projected forward.

### stat-25-24

**Ljung–Box tests**

The Ljung-Box statistic combines squared residual autocorrelations through several lags to test a no-autocorrelation null. Degrees of freedom should reflect estimated model parameters where appropriate. A significant result suggests leftover linear structure or misspecification; a nonsignificant result does not prove independent Gaussian errors. Choose lags meaningfully, report the tested range and inspect variance and outliers separately.

### stat-25-25

**Structural breaks**

A structural break changes parameters or distributional behavior at a time, such as a new measurement system or intervention. One stable model spanning the break can create misleading persistence diagnostics. Use known change dates when available; when searching for unknown dates, account for the search and minimum segment sizes. Forecast comparisons should reflect whether the future resembles the old regime, new regime or neither.

## Worked Python demonstrations

Complete offline program: [chapter_25.py](../examples/chapter_25.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_25.py
```

### Remove a known seasonal component without guessing

The fixture is 10+3t plus a four-position pattern [0,2,0,-2]. Comparing y_t with y_(t-4) cancels the repeating pattern and leaves \(3\cdot 4=12\). First differencing those increments then gives zero. This exact algebra explains the transformation; it does not justify differencing an arbitrary observed series twice.

### Read a frequency in the correct units

A sine with period eight is observed for 32 equally spaced positions, exactly four cycles. Its peak is at 0.125 cycles per observation, whose reciprocal is eight. Changing the sampling interval changes the physical units. A non-integer number of observed cycles would spread power across bins and require a leakage-aware interpretation.

### Preserve the information set

At origin three, a row with event time four is unavailable, and a historical row would also be unavailable if its arrival time exceeded the origin. The lag feature for time four is the value 15 from time three, not the current outcome 18. These explicit index checks are the foundation for rolling-origin validation.

### Complete executable example

```python
import numpy as np


def differencing_trace():
    t = np.arange(16, dtype=float)
    seasonal = np.tile([0.0, 2.0, 0.0, -2.0], 4)
    y = 10 + 3 * t + seasonal
    seasonal_difference = y[4:] - y[:-4]
    assert np.allclose(seasonal_difference, 12.0)
    assert np.allclose(np.diff(seasonal_difference), 0.0)
    print(
        "Seasonal difference:",
        seasonal_difference[:4],
        "then first difference:",
        np.diff(seasonal_difference)[:3],
    )


def frequency_trace():
    t = np.arange(32, dtype=float)
    y = np.sin(2 * np.pi * t / 8)
    power = np.abs(np.fft.rfft(y - y.mean())) ** 2
    frequency = np.fft.rfftfreq(len(y), d=1.0)
    peak = frequency[np.argmax(power[1:]) + 1]
    assert np.isclose(peak, 1 / 8)
    print("Peak cycles per observation:", peak, "period:", 1 / peak)


def information_order():
    event_time = np.array([1, 2, 3, 4])
    available_time = np.array([1, 3, 3, 5])
    origin = 3
    allowed = (event_time <= origin) & (available_time <= origin)
    assert allowed.tolist() == [True, True, True, False]
    y = np.array([10.0, 12.0, 15.0, 18.0])
    lag1 = np.r_[np.nan, y[:-1]]
    assert lag1[3] == 15 and lag1[3] != y[3]
    print(
        "Available rows at origin 3:", np.flatnonzero(allowed), "lagged feature at time 4:", lag1[3]
    )


def main():
    differencing_trace()
    frequency_trace()
    information_order()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does a flat-looking series establish stationarity?** No. Its variance, tails or dependence can change while its mean looks stable. State the stationarity property required by the method, inspect relevant diagnostics and assess whether the assumption remains useful over the decision horizon.

**Interview: What if ADF and KPSS disagree?** Their null hypotheses differ. Interpret both with their trend/constant specification, lag or bandwidth settings and sample size. Near-unit roots, breaks and low power can make the result inconclusive; a forecast comparison and domain explanation are more useful than forcing a binary label.

**Interview: Why is Granger causality weaker than intervention causality?** It measures incremental predictive information conditional on a chosen history. Shared causes, timing and omitted variables can supply that information without a causal effect of manipulating the predictor.

## Primary sources and official APIs

- [Hyndman and Athanasopoulos, Forecasting: Principles and Practice](https://otexts.com/fpp3/)

- [statsmodels ADF API and null specification](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html)

- [statsmodels KPSS API and stationarity null](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html)

## Reading connections

[Previous chapter](24-explainability-fairness-and-model-robustness.md) | [Book contents](../README.md) | [Next chapter](26-classical-forecasting-methods.md)
