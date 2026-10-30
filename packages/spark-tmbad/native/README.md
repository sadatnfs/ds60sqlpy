# Native likelihood and forecasting engine

This directory contains original C++ model definitions, the bounded numerical
engine, and a framed process worker. The numerical process uses TMBad 1.9.25 and
Eigen. It does not start R, Python, a compiler, or a shell. Scala owns Spark
partitioning and the small global optimizer; Python is a driver facade.

The model registry is compiled into a prepared artifact. A request selects one
prepared model ID and supplies bounded numerical data. It cannot supply C++
source, include paths, R expressions, library paths, or compiler options. The
artifact's source/toolchain/dependency identity and each descriptor digest are
checked at the process boundary. See [the protocol](../docs/PROTOCOL.md) and the
package build tooling for preparation. A development binary with a placeholder
identity is only suitable for diagnostics and is not a qualified artifact.

## Model definitions and targets

| Model | Parameter order | Fit data order | Factorization and integration |
| --- | --- | --- | --- |
| `normal` | `mu, log_sigma` | `y` | Independent rows |
| `linear_gaussian` | `beta0, beta1, log_sigma` | `x, y` | Independent rows |
| `poisson_exposure` | `intercept, slope` | `x, exposure, y` | Independent rows |
| `bernoulli_logistic` | `intercept, slope` | `x, y` | Independent binary rows |
| `negative_binomial2` | `intercept, slope, log_shape` | `x, exposure, y` | Independent overdispersed counts |
| `gamma_regression` | `intercept, slope, log_shape` | `x, y` | Independent strictly positive responses |
| `saturating_growth` | `baseline, log_amplitude, log_rate, log_sigma` | `time, y` | Original nonlinear mean with independent Gaussian errors |
| `quadratic_gaussian` | `intercept, curvature, log_sigma` | `x, y` | Independent rows; original extension example |
| `gaussian_random_intercept` | `beta, log_sigma, log_tau` | `y` | Complete group, exact Gaussian integral |
| `gaussian_random_intercept_laplace` | `beta, log_sigma, log_tau` | `y` | Complete group, generic Laplace engine |
| `poisson_random_intercept` | `beta, log_tau` | `exposure, y` | Complete group, generic Laplace engine |
| `poisson_random_slope` | `beta0, beta1, log_tau0, log_tau1` | `x, exposure, y` | Complete group, two-dimensional generic Laplace |
| `ar1` | `mu, atanh_phi, log_sigma` | `time, y` | Complete stationary AR1 series |
| `gaussian_ar1_random_intercept` | `beta, atanh_phi, log_sigma, log_tau` | `time, y` | Complete group, exact Gaussian integral with AR1 residuals |

The authoritative descriptor comes from `--describe`. It declares the available
prediction and forecast targets, field order, bounds, derivative orders and
uncertainty semantics. Do not infer targets from a model's name. In particular,
both Poisson random-effect models declare separate existing/new-group moment
targets. A custom model may leave its targets empty. Undeclared operations fail
rather than manufacturing predictions.

The row-model `response` forecast predicts future independent observations at
supplied covariates, with empty history. It is not a time-series conditioning
operation. Random-intercept models distinguish `existing_group`, requiring the
complete observed group, from `new_group`, requiring empty history. AR1 models
require exact integer time indices with unit spacing. A conditional forecast
starts one step after the final observed index; duplicate indices, gaps and a
missing history fail. `stationary_new_series` uses empty history. Future response
labels are never accepted as predictor fields.

## What the generic Laplace path computes

An author provides a normalized joint negative log density
\(f(\theta,u;y)\), fixed parameter vector \(\theta\), and one bounded vector of
random effects \(u\) per complete unit. The engine finds a local stationary mode
\(\hat u(\theta)\) and computes

\[
 L(\theta)=f(\theta,\hat u;y)
 +\tfrac12\log\det H_{uu}(\theta,\hat u)
 -\tfrac q2\log(2\pi),
 \qquad H_{uu}=\frac{\partial^2 f}{\partial u\partial u^\top}.
\]

The Gaussian comparison is exact because the joint density is quadratic in the
latent effects. The Poisson examples are approximations. A successful numerical
mode is not proof that a Laplace approximation is statistically accurate, that a
multimodal objective has a global optimum, or that an arbitrary latent model can
be distributed over unrelated batches.

The outer gradient includes both the log-determinant term and the changing mode:

\[
 \frac{d\hat u}{d\theta_a}=-H_{uu}^{-1}f_{u\theta_a},\qquad
 \frac{dL}{d\theta_a}=f_{\theta_a}
 +f_u^\top\frac{d\hat u}{d\theta_a}
 +\tfrac12\operatorname{tr}\!\left(H_{uu}^{-1}\frac{dH_{uu}}{d\theta_a}\right).
\]

TMBad records the joint function and its derivatives, including the third
partial derivatives needed for the total change of curvature. No finite
difference gradient is used by the engine. Independent finite differences and
analytic/dense-integral calculations are test oracles. Cholesky solves implement
the implicit derivatives and trace; dimensions are deliberately small.

The inner solver has at most 80 iterations, 30 backtracking trials per iteration,
a bounded damping sequence and latent coordinates in `[-50, 50]`. It requires an
absolute latent score at most `1e-9` and positive, adequately conditioned final
curvature. Near machine precision, a small undamped Newton correction may be
accepted only when the loss changes within an explicit rounding allowance and
the score strictly improves. This does not relax the final score test. Mode,
score, curvature and correction counts are returned as diagnostics. Failed
curvature or nonconvergence terminates the worker with an error.

Dense Laplace currently allows `q <= 8` and `d + q <= 16`. Its outer Hessian is
not implemented; a request for it is refused. Exact and row objectives can
provide a dense Hessian for at most 16 fixed parameters. These are limits for
low-dimensional statistical estimation, not large neural-network training.

A unit weight multiplies the final marginal objective and gradient once. It does
not multiply the joint density before integration. Row weights apply only to
independent row contributions. Shared priors or penalties belong once in the
global objective, not once in each Spark partition. Cross-group random-effect
covariance and arbitrary globally coupled latent effects are unsupported by this
partition-additive design.

## Prediction and multi-step uncertainty

For a Gaussian random intercept, the exact posterior latent variance and mean
are

\[
 v_u=(\tau^{-2}+n\sigma^{-2})^{-1},\qquad
 m_u=v_u\sigma^{-2}\sum_i(y_i-\beta).
\]

An existing-group future observation has mean \(\beta+m_u\) and variance
\(\sigma^2+v_u\). A new-group observation has mean \(\beta\) and variance
\(\sigma^2+\tau^2\). Future observations in the same group share latent
uncertainty. The current output contains pointwise variances, not a full joint
forecast covariance matrix or simultaneous intervals.

For AR1, \(\phi=\tanh(\eta)\), where `eta` is `atanh_phi`, and `sigma` is the
innovation standard deviation. Conditional on the last exact observation,

\[
 E[y_{t+h}]=\mu+\phi^h(y_t-\mu),\qquad
 \operatorname{Var}(y_{t+h})=\sigma^2\sum_{j=0}^{h-1}\phi^{2j}.
\]

For the combined random-intercept/AR1 model, let \(m_u,v_u\) be the posterior
latent moments computed from the whole AR-correlated history. Then

\[
 E[y_{t+h}]=\beta+\phi^h(y_t-\beta)+(1-\phi^h)m_u,
 \quad\operatorname{Var}(y_{t+h})=(1-\phi^h)^2v_u
 +\sigma^2\sum_{j=0}^{h-1}\phi^{2j}.
\]

The independent oracle constructs the full covariance matrix and conditions the
multivariate Gaussian directly, rather than repeating the engine's rank-one
precision calculation. Negative autocorrelation and more than one forecast step
are covered.

For Poisson random intercepts, existing-group moments use a Gaussian Laplace
approximation to the latent posterior. New-group moments integrate the Gaussian
latent prior analytically, giving Poisson/lognormal moments. The two-effect
random-slope model uses design vector \(a=(1,x)^\top\), latent log-rate mean
\(a^\top\hat u\) and variance \(a^\top H^{-1}a\) for an existing group.
The new-group variance is \(\tau_0^2+x^2\tau_1^2\). If the latent log-rate
variance is \(v\) and the mixed count mean is \(m\), the pointwise count
variance is \(m+m^2\operatorname{expm1}(v)\). These forecasts condition on
supplied future covariates, not sequential time dynamics. These two targets
have different approximation boundaries, explicitly present in metadata. All
current targets condition on fitted parameters and exclude parameter-estimation
uncertainty. Parameter transformations are optimization coordinates: a
frequentist likelihood does not acquire a Jacobian simply because a positive
scale is represented by its logarithm.

## Additional response families and special-function accuracy

Bernoulli logistic regression computes the negative log likelihood as
`softplus(-eta)` for a success and `softplus(eta)` for a failure. Stable equivalent
expressions avoid overflowing exponentials and avoid subtracting nearly equal
numbers when a success already has probability near one. This is a row model;
its expression is recorded again for each requested parameter vector. It is not
a branch-frozen latent-mode solver.

NB2 uses mean \(\mu=e\exp(\beta_0+\beta_1x)\) and positive shape \(k\), with
variance \(\mu+\mu^2/k\). Gamma regression uses mean
\(\mu=\exp(\beta_0+\beta_1x)\), shape \(k\), and variance \(\mu^2/k\).
Their common parameter `log_shape` is restricted to `[-4,6]`. Counts are bounded
nonnegative integers; Gamma responses must be strictly positive. The exposure
is explicit only for the count model. These are different distributional
assumptions despite sharing a log-linked mean.

Standalone TMBad does not supply the full TMB distribution/special-function
layer. This implementation therefore includes an explicitly approximate,
differentiable positive log-Gamma function. It shifts the argument to at least16
using the exact recurrence and applies eight Stirling/Bernoulli terms, through
\(x^{-15}\), in Horner form. Its supported argument domain is \(0<x\le2\times
10^6\). This is not described as an exact `lgamma` implementation. Values,
first derivatives and second derivatives must be independently checked against
`lgamma`, digamma and trigamma over the supported range and recurrence boundaries.
The production score is AD of the prepared expression, never finite differences.
The mathematical expansion and asymptotic bounds are described in
[NIST DLMF 5.11](https://dlmf.nist.gov/5.11); polygamma definitions and identities
are in [DLMF 5.15](https://dlmf.nist.gov/5.15). Observed floating-point and
derivative errors must still come from the independent checks.

NB2 additionally uses a finite exact log-rising-factorial sum for counts at most64
to avoid subtracting large log-Gamma values. Its zero-count term is evaluated
with `log1p`/softplus algebra and remains nonzero in a small-mean case. Larger
counts use the qualified approximation. The helper's value-dependent recurrence
is used by these fixed-parameter row models, which are retaped for each request;
it is not used in any inner latent mode search. A custom latent model must not
reuse a branch-dependent approximation without proving its validity throughout
that inner solve.

## Authoring a prepared custom model

Start with [`models/custom_models.hpp`](models/custom_models.hpp). The original
`quadratic_gaussian` example defines its own likelihood, bounded design support,
parameter ordering, and future-observation callback. The second original custom
model, `saturating_growth`, is nonlinear in fitted parameters: its mean is
\(b+\exp(a)[1-\exp\{-\exp(r)t\}]\). Its AD implementation uses `expm1`
so small nonnegative times do not lose the growth increment to cancellation. Add a reviewed `Model` to
`custom_models()` and prepare a new artifact. Old fitted JSON must continue to
require its original matching artifact; a new source build is not a compatible
silent substitution.

A model definition supplies four parts:

1. A descriptor with distinct names, parameter bounds, exact factorization and
   derivative declarations. Targets independently declare fields, output columns,
   history requirements, conditioning and uncertainty.
2. A validation callback that checks statistical support beyond finite numeric
   shape. Count/exposure and time/cadence checks are examples.
3. An AD objective using `ADVector` and `Data`. For rows, return the weighted sum
   of independent row negative log densities. For an exact unit, return one
   joint/marginal scalar. For Laplace, fixed parameters come first and the `q`
   latent coordinates follow; include normalized latent and observation
   densities and do not apply the unit weight yourself.
4. An explicit prediction callback returning one output row per future input
   row. Leave targets empty if the scientific prediction rule is not defined.
   Return finite values and document which uncertainty is included.

For a custom two-effect latent regression, set `fit_kind="unit"`,
`marginalization="laplace"`, `random_dimension=2`, `derivative_orders={1}` and
choose a fixed layout such as
`(beta0,beta1,log_tau0,log_tau1,u0,u1)`. Write the joint observation density plus
two normalized Gaussian prior terms in the objective callback. The existing
`poisson_random_slope_model()` demonstrates this contract. The engine receives no
model-ID-specific integration branch: the same solver and implicit derivative
path process both it and the one-dimensional model. Complete groups must remain
whole when partitioned. A graph latent variable shared across those groups does
not fit this declaration.

Use differentiable AD arithmetic for parameter-dependent calculations. Ordinary
C++ branches are evaluated when the tape is recorded. Do not pretend that an
arbitrary branch crossing, external callback, or nonsmooth likelihood has the
required derivative semantics. Validate and test a custom model's domain and
change points before preparing it. Runtime users execute trusted reviewed
artifacts; this process boundary is not a sandbox for arbitrary untrusted code.

## Process limits, dependencies and validation

The Linux worker is serial and has no cross-task tape cache. It sets parent-death
`SIGKILL` with a race check, core size zero, a 1 GiB address-space ceiling, a
120-second total CPU budget, and no-new-privileges. A seccomp filter denies child
creation and execution syscalls. Parent Spark tasks still need wall deadlines,
cancellation, bounded stderr draining and exit-code checks. A valid response is
provisional until the native process exits successfully. Resource limits apply
to one worker and do not bound all memory used by a Spark executor.

The wire has a 4 MiB frame limit, depth 32, at most 1024 fields per object,
8192 elements per array, 256 Unicode scalar values per key and 1,000,000 per
string. Invalid UTF-8, unpaired surrogates and decoded duplicate keys are refused.
Integral JSON tokens use the shared interval `[-(2**53-1), 2**53-1]`; explicit
floating-point tokens must be finite. A count encoded as `2.0` is valid when it
satisfies the model's integer support. Structural schema fields remain strict.

Original source here is MIT. The prepared TMBad dependency retains its GPL-2
license and corresponding source; Eigen and JSON dependencies retain their own
notices. A process boundary is not a legal assurance about a combined artifact.
Dependency archives and notices belong to the separately prepared SDK rather
than copied into this original source tree. Pinned source identities are checked
by package preparation. Compiler and standard-library ABI must match executing
Linux workers on their native architecture.

The tests are deliberately separate evidence layers:

- `tests/math_checks.cpp` checks actual TMBad derivatives, a nonsymmetric vector
  Jacobian, independent dense Gaussian integration, non-Gaussian Laplace
  gradients, bad curvature, tape teardown and AR1 moments. The separate
  `tests/special_function_checks.cpp` emits actual AD log-Gamma value/first/second
  derivatives for independent SciPy comparison, including recurrence boundaries.
- `tests/sandbox_checks.cpp` exercises Linux parent-death handling, denied
  fork/exec, address-space refusal and the configured resource limits.
- `tests/test_worker_protocol.py` drives the actual binary, including malformed
  framing/JSON, terminal failures, identities, numerical domains, weighted
  objectives, forecast history and the custom model.
- `../python/examples/validate_native_oracles.py` uses independently authored
  analytic and dense-matrix oracles, including Poisson mode/implicit gradients
  and combined Gaussian conditional forecasts.
- Actual Spark acceptance is a separate JVM/Python integration gate. Native
  compiler or numerical success alone does not qualify that connector, distributed
  scaling, cluster cancellation, or performance.
