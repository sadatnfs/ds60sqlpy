# Primary-source feature and implementation matrix

This is a research snapshot, not a compatibility promise or an upstream test
report. AFModel is pinned to
[`5362baf5`](https://github.com/sadatnfs/AFModel/tree/5362baf5aa909d9792e0aeef2b9d17c8670841b9).
The glmmTMB C++ implementation is pinned to
[`1db3b469`](https://github.com/glmmTMB/glmmTMB/blob/1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c/glmmTMB/src/glmmTMB.cpp),
whose package DESCRIPTION identifies development version `1.1.15.9000` and
`AGPL-3`. Its [public exports](https://github.com/glmmTMB/glmmTMB/blob/1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c/glmmTMB/NAMESPACE)
were inspected alongside the C++ branches. Upstream code is not copied into
this original MIT study implementation. The separate TMBad dependency keeps
its own GPL-2 notices and corresponding source.

Current native 0.2 support means a specific prepared model in the 23-model registry,
not arbitrary formulas, links or covariate-dependent dispersion. Current Torch
support refers to its existing registered models and extension contracts. A new
custom model still needs original source, explicit registration and actual
qualification. No study below has run glmmTMB or AFModel merely by inspecting it.
Actual local native checks qualify the nine added models' declared values,
derivatives, moments and selected domain refusals; local Spark checks separately
qualify the named-target APIs. Read [the additional model checks](../../python/docs/NEW-MODEL-CHECKS.md)
and [target contract](../../python/docs/EXTENDED-TARGETS.md) for their exact scope.
These receipts do not make the planned simulation studies completed benchmarks.

## Observation families

| Pinned glmmTMB family or group | Existing native route | Existing Torch route | Original study and remaining work |
| --- | --- | --- | --- |
| Gaussian | Normal, one-predictor linear, quadratic, growth, selected Gaussian groups | Normal, general explicit design, nonlinear decay, Gaussian random intercept | sim-001/002/006/008; compare parameterization and normalization |
| Binomial | Bernoulli and binomial_logistic with explicit trial counts | Bernoulli logistic only | sim-018/022; native trial-size model available, study pending |
| Beta-binomial | beta_binomial with constant concentration | Custom model required | sim-022; native model available, distinguish within-count variation from cross-row correlation |
| COM-binomial | Absent | Custom model required | sim-022; normalization and mean parameterization need independent oracles |
| Beta | beta_regression with constant precision | Custom model required | sim-023; native interior-support subset available, study pending |
| Ordered beta | Absent | Custom model required | sim-023; endpoint masses are not clipped continuous observations |
| Gamma | Fixed-shape log-mean regression | Custom model required | sim-024; current native shape is constant across rows |
| Poisson | Exposure regression and selected random effects | Exposure regression | sim-019; preserve exposure and log link |
| Zero-truncated Poisson | zero_truncated_poisson with exposure | Custom model required | sim-020/021; normalized positive-count model available, selection/censoring extensions remain separate |
| Generalized Poisson | Absent | Custom model required | sim-026; support depends on parameterization |
| COM-Poisson | Absent | Custom model required | sim-026; normalizer, mean parameterization and derivative accuracy |
| Truncated generalized/COM-Poisson | Absent | Custom model required | sim-021/026; two normalization layers must be qualified |
| NB1 | Absent | Custom model required | sim-019; variance grows linearly with the mean |
| NB2 | Fixed-shape log-mean/exposure regression | Custom model required | sim-019; variance is mean plus a quadratic term |
| NB12 | Absent | Custom model required | sim-019; distinguish its linear and quadratic dispersion terms |
| Truncated NB1/NB2 | Absent | Custom model required | sim-021; fit to selected positive counts with correct normalization |
| Student-t | student_t_regression with degrees of freedom greater than two | Custom model required | sim-024; native finite-variance model available, scale is not standard deviation |
| Tweedie | Absent | Custom model required | sim-025; atom at zero plus continuous positive mass |
| Lognormal | lognormal_regression with constant log-scale noise | Custom model required | sim-024; native model includes the response Jacobian and data-scale moments |
| Skew normal | Absent | Custom model required | sim-024; distribution shape and mean parameterization need care |
| Bell | Absent | Custom model required | sim-026; special-function and normalizer qualification first |
| Ordinal cumulative-link | Absent | Custom model required | sim-023; ordered thresholds and stable tail probabilities |

The pinned R exports include newer `combinomial`, `nbinom12`, `ordinal`, `bell`
and `skewnormal` constructors. This does not establish that every possible link,
simulation setting or prior combination works. The moving
[family documentation](https://glmmtmb.github.io/glmmTMB/reference/nbinom2.html)
is useful context but does not replace pinned source and model-specific installed
reference tests. The optional project below now covers selected cases. For example, the pinned Gamma branch explicitly uses shape and
scale equal to mean/shape, so its variance is mean-squared/shape. Raw dispersion
coefficients and `predict(type="disp")` must be interpreted through that version's
actual transformation; comparing differently defined numbers is not parity.

## Covariance and independence

The pinned covariance codes include all of the following. Their implementation
is in the C++ termwise density dispatcher; the
[covariance vignette](https://glmmtmb.github.io/glmmTMB/articles/covstruct.html)
provides the conceptual background, although its displayed table predates some
current codes.

| Structure | Current package boundary | Study requirement |
| --- | --- | --- |
| Heterogeneous diagonal `diag` | Native Poisson slope example has two independent latent scales only | sim-028/029; explicit vector scales and named latent layout |
| Homogeneous diagonal `homdiag` | A scalar random-intercept prior is a narrow case | sim-029; do not claim a general covariance formula API |
| Unstructured `us` | Exact two-dimensional Gaussian correlated intercept/slope model; no generic covariance formula API | sim-028/029; native narrow subset available, broader dimensions and structures remain planned |
| Compound symmetry `cs`, `homcs` | Gaussian random intercept implies only a nonnegative homogeneous correlation subset | sim-029; general CS also permits a dimension-dependent negative range |
| AR1 `ar1` | Direct stationary Gaussian AR1 is available natively | sim-013; glmmTMB latent AR1 plus measurement noise is a different model |
| Heterogeneous AR1 `hetar1` | Absent | sim-030; marginal scale schedule and innovation variance cannot be conflated |
| OU `ou` | Absent | sim-030; use elapsed time and nonnegative exponential correlation |
| Spatial exponential `exp` | Absent | sim-031; bounded independent spatial blocks only initially |
| Spatial Gaussian `gau` | Absent | sim-031; range convention and squared distances |
| Matern `mat` | Absent | sim-031; range/smoothness parameterization and special functions |
| Toeplitz `toep`, `homtoep` | Absent | sim-029; independently bounded correlations do not by themselves guarantee positive definiteness |
| Reduced rank `rr` | Absent | sim-032; rank choice, loading constraints and rotation/sign ambiguity |
| Proportional known covariance `propto` | Absent | sim-032; validate the known matrix and its scale |
| Shared/equal covariance `equalto` | Absent as a formula/parameter-sharing API | sim-032; distinguish shared covariance parameters from shared latent variables |

The native model `gaussian_ar1_random_intercept` has covariance equal to a shared
intercept component plus stationary AR1 residual covariance. It is not the same
as a latent AR1 process with a separate measurement-error variance. Native AR1
uses an innovation standard deviation and a tanh correlation coordinate; the
pinned glmmTMB AR1 term uses a marginal standard deviation and another correlation
transform. Compare the implied covariance matrices, not raw optimizer vectors.

A block-diagonal joint model can be evaluated one complete independent block per
Spark unit. A globally connected spatial field, crossed effect spanning units,
or shared latent vector cannot be split this way. The native generic dense
Laplace path currently limits latent dimension to eight and total fixed-plus-
latent dimension to sixteen. A non-Gaussian state vector with one latent state
per time point generally exceeds that limit. Exact Gaussian marginalization or
a separately implemented sparse/Markov method is a different capability.

## Model framework features

| Feature | Current boundary | Study/action |
| --- | --- | --- |
| Separate mean, zero-inflation and dispersion designs | glmmTMB has separate design/offset/parameter blocks; neither package is a general formula compiler | sim-027; typed model schemas and explicit normalization |
| Zero inflation and hurdle composition | Native zero_inflated_poisson and hurdle_poisson with separate scalar x/z predictors and exposure | sim-020; distinguish structural-zero probability, positive component and full response moments; study pending |
| Observation weights | Current packages multiply likelihood contributions and declare reduction | sim-001; do not silently reinterpret these as inverse-variance or survey weights |
| Fixed-parameter priors | Native named diagonal Gaussian means/precisions, selected L1 and exact fixed coordinates; legacy scalar L2 unchanged | sim-002/003/004/010/011; native target API available, new studies and Torch parity remain separate |
| Latent priors | Selected prepared joint models include normalized generative latent densities | sim-008/028; integrating these gives a marginal likelihood, not a posterior over population parameters |
| Prior families | Pinned C++ dispatcher implements normal, Student-t, Cauchy, Gamma and LKJ paths | sim-010/011/035; a beta-prior enum exists but no beta case was found in that C++ prior dispatcher |
| MAP versus MCMC | glmmTMB's prior vignette distinguishes MAP from a separately requested sampler | sim-010/035; current packages do not automatically sample fixed-parameter posteriors |
| ML versus REML | Current package fitting is likelihood/MAP, not REML | sim-033; implement and qualify a different target explicitly |
| Conditional simulation and residual diagnostics | Requires declared conditioning and a simulation operation | sim-017/035; generated data are not evidence that a fitted simulator is calibrated |
| `REPORT`/`ADREPORT` and uncertainty | Native point/moment targets are explicit; full TMB reporting APIs are not reproduced | sim-017/034; parameter uncertainty needs its own calculation and evidence |

## Separately qualified optional R reference

The [optional serial R/TMB/glmmTMB project](../../reference/QUALIFICATION.md)
now has actual native Linux ARM64 preparation and all 24 registered case passes,
using prepared manifest SHA256
`a4b0d9602355cbad614f6dfaa34e8235b86a2750e43213ae689a18a6e0b22566`.
Its [qualification index](../../reference/qualification/index.json) retains exact
case receipts. This includes the original TMB templates and selected real upstream
family, zero-component, covariance, prior and forecast calls. It is separate from
the native 23-model registry and does not implement those upstream interfaces in
Spark/TMBad or Torch. No broad cross-package numerical parity is claimed.

A later bounded serial run attempted seven cases 16 times each: 112 executions,
110 passed and two Gaussian random-slope failures retained. Those failures count
in the denominator. The regularization_posterior case reused one fixed training
dataset and changed posterior-draw randomness; its 16 executions are not 16
independent dataset replications. The retained derived reanalysis therefore sets
its dataset-level bias/MSE MCSE and dataset failure interval to null, while keeping
within-case posterior-draw diagnostics separate. The original raw ledgers and
historical summaries remain unchanged. The other dataset-study summaries retain
their actual successful/failed counts and explicit Monte Carlo uncertainty.
A small repetition count is execution evidence, not a coverage guarantee.

## AFModel-inspired lessons without operational dependencies

The pinned [AFModel objective](https://github.com/sadatnfs/AFModel/blob/5362baf5aa909d9792e0aeef2b9d17c8670841b9/AFModel/src/AFModel.cpp)
contains alternatives for fixed effects, panel intercepts/slopes, level/difference
models, lag terms and observation-scale decay. Its
[fit wrapper](https://github.com/sadatnfs/AFModel/blob/5362baf5aa909d9792e0aeef2b9d17c8670841b9/AFModel/R/run_model.R)
uses the TMB objective/optimizer/reporting pipeline. Our studies use original
synthetic panels and explicitly specified generative models instead of importing
historical operational helpers or claiming to reproduce every branch.

- A time-dependent observation scale is a heteroskedastic likelihood. It is not
  generally equivalent to multiplying the entire log density by forgetting weights.
- Componentwise AR coefficient bounds do not guarantee stationarity for AR(p).
  A global-plus-panel coefficient can also violate a bound after addition.
  sim-015 requires a companion-matrix/root check and separately states invertibility
  assumptions for moving-average terms.
- The helper named `prior_coefs_mean` filters fitted models by coefficient signs.
  That is post-fit selection, not adding a Bayesian prior density. sim-011 contrasts
  sign constraints, truncated priors and selective model filtering.
- Recursive future covariates and first differences require origin-specific input
  availability and careful back-transformation. No future observed outcomes may
  enter a held-out history or a scaling/tuning fit.
- A random-walk uncertainty layer estimated from fitted differences is not
  automatically a parameter posterior or a calibrated predictive distribution.
  sim-016/017 compare it with a declared innovation model and repeated-data coverage.
- A covariance or prior connecting panel effects across panels breaks independent
  per-panel factorization. sim-031/032 keeps connected components whole or labels
  the model unsupported by the current distributed contract.
