# Likelihoods, predictions and forecast targets

The four custom models are original templates compiled by TMB using CppAD. They
are independent references for the primary TMBad route. A shared AD framework is
not an independent mathematical oracle, so each example also uses a direct
formula, dense covariance, finite differences or quadrature where appropriate.

## Selected Gaussian prior and a correlated mixed model

For Gaussian regression, the likelihood is

\[
 y_i\sim N(x_i^T\beta,\sigma^2).
\]

Positive entries in `prior_precision` contribute normalized Gaussian priors
\(\beta_j\sim N(m_j,p_j^{-1})\). A zero entry contributes no coefficient penalty.
The example fixes the observation scale through TMB's parameter map. Its oracle
is

\[
 \hat\beta=(X^TX/\sigma^2+P)^{-1}(X^Ty/\sigma^2+Pm).
\]

The intercept is explicitly unpenalized. This differs from the primary package's
historical scalar L2 option on every optimization coordinate. Leaving log-scale
free would also change the analytic solution and needs a different comparison.
The strict fit checks optimizer status, finite parameters, projected score and
positive fixed-parameter curvature. An optimizer exit alone is insufficient.

For the mixed model,

\[
 y_{gi}=\beta_0+\beta_1x_{gi}+b_{g0}+b_{g1}x_{gi}+\epsilon_{gi},
 \quad b_g\sim N(0,D),\quad \epsilon_{gi}\sim N(0,\sigma^2).
\]

The template uses two standard normal latent coordinates and an explicit
correlated transform. The observed group covariance is
\(V_g=Z_gDZ_g^T+\sigma^2I\). The independent R oracle evaluates this multivariate
normal density directly. Because the model is Gaussian, TMB's random-effect
Laplace integral should agree with this exact density up to numerical precision.
This statement does not extend to the nonlinear or non-Gaussian examples.

Known-group prediction conditions on that group's observed history. Its effect
mean is \(DZ_g^TV_g^{-1}(y_g-X_g\hat\beta)\). The example compares that mean with
TMB's reported conditional effects and returns the full three-target conditional
covariance. New-group predictions instead integrate a fresh effect from \(D\).
Both condition on fitted population parameters and omit their uncertainty.

## Nonlinear mixed growth

The growth model is

\[
 y_{gi}=b_0+\exp(a+u_g)(1-\exp(-\exp(k)t_{gi}))+\epsilon_{gi},
 \quad u_g\sim N(0,\tau^2).
\]

The positive rate is \(\exp(k)\), and the random effect is on log amplitude.
A conditional-mode curve uses \(\exp(a+\hat u_g)\). The mean for a fresh group
uses \(\exp(a+\tau^2/2)\), which is different because exponentiation is nonlinear.
The new-group variance combines observation noise with the lognormal amplitude
variance. It does not silently substitute the conditional mode for an integrated
mean or add population-parameter uncertainty.

The example centers a one-group numerical integral at the conditional mode,
splits integration at that mode, checks adaptive error estimates, and repeats
the calculation over a wider scale-aware interval. It contrasts this finite-domain
reference with its Laplace approximation. Interval stability does not rigorously
bound omitted tails. Their difference is reported, not asserted to be zero.
Changing the group effect variance is a useful stress case: a broad or skewed
conditional effect distribution can make a local Gaussian approximation less
accurate even when optimization succeeds. A held-out future time is a covariate
prediction for this curve, not an AR process forecast.

## Original Gaussian panel and AFModel distinctions

The new panel model combines a fixed intercept, scaled time trend and known
covariate with independent Gaussian panel intercepts/slopes. Residual covariance
is

\[
 C(t,s)=\tau_0^2+\tau_1^2(t/c)(s/c)
       +\sigma_t\sigma_s\phi^{|t-s|},
 \qquad \sigma_t=\exp(\rho+\delta t/c),\quad\phi=\tanh(\eta).
\]

TMB evaluates each complete panel's exact Gaussian density. Its first derivative
is checked against two finite-difference step sizes and its value against an
independently constructed dense covariance. Observations from a connected panel
must remain together. Splitting its covariance into row-additive pieces changes
the model.

The future mean and covariance use the full Gaussian conditioning equations:

\[
 m_*+C_{*h}C_{hh}^{-1}(y_h-m_h),\qquad
 C_{**}-C_{*h}C_{hh}^{-1}C_{h*}.
\]

The fitted sample ends before the future time grid. Forecast covariates are
explicit scenarios and contain no future response. This one-origin example is
not by itself a completed rolling-origin study or a coverage claim.

AFModel motivated the questions about trends, panel effects, lags, differences
and variance schedules. This is an original model with its own likelihood. It
does not reproduce every historical AFModel branch. In particular:

- A time-dependent observation scale changes a normalized density. It is not
  equivalent to multiplying the whole log density by forgetting weights.
- Bounding each AR coefficient separately does not establish AR(p) stationarity.
  This example uses only one explicit AR1 parameter with absolute value below 1.
- A post-fit coefficient-sign filter is not a prior density or valid automatic
  post-selection uncertainty calculation.
- Random-walk residual additions do not automatically supply a parameter
  posterior or calibrated joint forecast distribution.

## Real upstream families and covariance structures

`glmm_family` calls the pinned library directly. NB1 and NB2 have different
variance conventions; beta-binomial introduces trial correlation; the Student-t
example fixes degrees of freedom with the documented parameter map. Lognormal
means and scales are on the data scale in this pinned upstream family.

Zero inflation adds a structural-zero probability to an ordinary count component.
A hurdle uses a positive truncated count component. The worked examples compare
`conditional`, `zprob` and `response` predictions and check
\(E[Y]=(1-p_0)E[Y\mid\text{count component}]\). Do not compare a truncated
component mean with an untruncated NB2 mean without its normalization.

The covariance examples call actual upstream AR1, OU, CS, diagonal, Toeplitz or
unstructured terms. Residual dispersion is fixed near zero in those examples
so that a second free diagonal component is not confounded with the covariance
being fitted. Positive definiteness and parameter identification remain separate
checks. A matrix-shaped output alone does not establish either.

`glmm_ar_forecast` deliberately fits a latent AR1 effect plus independent
measurement noise. Its covariance differs from directly observed AR1. It then
uses an original Gaussian conditioning calculation with the fitted covariance,
clearly labeled as such. It does not advertise a generic upstream forecasting
method or treat raw covariance optimization coordinates as native TMBad ones.

The pinned upstream `simulate.glmmTMB` binomial-family branch returns one
success/failure matrix per replicate. The beta-binomial example checks its
row count, integer support and exact trial totals, then reports success counts
and proportions separately. Averaging a flattened success/failure matrix would
remove the response signal. This schema follows the [pinned simulator source](https://github.com/glmmTMB/glmmTMB/blob/1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c/glmmTMB/R/methods.R).
