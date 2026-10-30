# Additional likelihoods and uncertainty targets

Version 0.2 adds eight row likelihoods and one exact complete-group Gaussian
likelihood. They use the same prepared native process, distributed reducer and
Python/Scala APIs as the original models. No R or Python numerical callback runs
on an executor. Read the loaded manifest for the exact field order, parameter
names, bounds and model digests; a saved result binds to that particular artifact.

The [original gallery](EXAMPLES.md) still describes its original fourteen models.
The [additional checks](../python/docs/NEW-MODEL-CHECKS.md) describe independent
numerical references and actual Spark check commands for the new registry entries.
Preparation, objective evaluation, optimization, prediction and calibration each
need their own evidence. A derivative check does not establish successful fitting
for every dataset or parameter regime.

## Choose an observation model

Let \(\eta=\beta_0+\beta_1 x\), \(p=\operatorname{logit}^{-1}(\eta)\),
and \(\phi=\exp(\mathrm{log\_precision})\). Row likelihoods are independent
conditional on their shared parameters. Their `response` prediction and forecast
targets take the listed future fields without `y`.

| Model ID | Training fields | Statistical target | Future fields |
| --- | --- | --- | --- |
| `binomial_logistic` | `x, trials, y` | Binomial count with logistic success probability | `x, trials` |
| `beta_binomial` | `x, trials, y` | Beta-binomial count with mean probability \(p\) and concentration \(\phi\) | `x, trials` |
| `beta_regression` | `x, y` | Beta density with shapes \(p\phi,(1-p)\phi\) | `x` |
| `lognormal_regression` | `x, y` | Normal log response with mean \(\eta\) and log-scale standard deviation \(\sigma\) | `x` |
| `student_t_regression` | `x, y` | Student-t location \(\eta\), scale \(s\), and \(\nu=2+\exp(d)\) degrees of freedom | `x` |
| `zero_truncated_poisson` | `x, exposure, y` | Positive-count Poisson conditioned on \(Y>0\) | `x, exposure` |
| `zero_inflated_poisson` | `x, z, exposure, y` | Structural zero probability plus an ordinary Poisson component | `x, z, exposure` |
| `hurdle_poisson` | `x, z, exposure, y` | Zero hurdle probability plus a positive-count Poisson component | `x, z, exposure` |

Every density includes its response-dependent normalization. In particular,
lognormal likelihoods include the \(\log y\) Jacobian, and count likelihoods
include combinatorial/factorial terms. Beta regression requires \(0<y<1\);
an exact zero or one needs a different observation model, not silent clipping.
Binomial counts require integer \(0\le y\le n\le 10^6\). Zero-truncated
Poisson rejects zero responses. Lognormal requires positive responses.

All these models provide first and second derivatives of their row objective.
The native process checks finite outputs. Near-zero Hessian entries can lose
relative precision even when absolute derivative error is small; do not interpret
passing absolute numerical checks as uniform relative accuracy at every scale.

### Beta-binomial example

A binomial with \(n=12,p=0.4\) has mean \(4.8\) and variance \(2.88\).
A beta-binomial with the same mean and \(\phi=5\) has

\[
\operatorname{Var}(Y)=np(1-p)\frac{n+\phi}{1+\phi}=8.16.
\]

The extra variation is within an observation's count distribution. It does not
create correlation between different rows. If multiple rows share a latent
effect, use an appropriate complete-group model instead of calling independent
beta-binomial rows a correlated panel.

Prepare `beta_binomial` using columns `x`, `trials` and `y`, map observation IDs
explicitly, and fit with the ordinary shared interface. Its parameter order is
`intercept`, `slope`, `log_precision`. Initial values must respect the descriptor
bounds. A prediction frame supplies IDs, `x` and `trials`; its `tmbad_mean`,
`tmbad_variance` and `tmbad_sd` describe count-scale observation uncertainty at the
chosen population parameters. They exclude uncertainty in the estimated parameters.

The implementation evaluates small beta-function increments directly to avoid
subtracting nearly equal large log-gamma values. Endpoint count cases, million-trial
cases and analytic/independent derivatives are included in the numerical checks.
The regularized fit is a different target from an unpenalized likelihood fit;
record the selected prior and reduction in any comparison.

### Zeros, exposure and robust responses

For the Poisson models,
\(\mu=\mathrm{exposure}\exp(a_0+a_1x)\). Mixture models use a separate
\(\pi=\operatorname{logit}^{-1}(c_0+c_1z)\). Their distinction is visible at zero:

\[
P_{\mathrm{ZIP}}(Y=0)=\pi+(1-\pi)e^{-\mu},\qquad
P_{\mathrm{hurdle}}(Y=0)=\pi.
\]

The hurdle's positive component is normalized by \(1-e^{-\mu}\). Its response
mean is \((1-\pi)\mu/(1-e^{-\mu})\), while the zero-inflated mean is
\((1-\pi)\mu\). Both report full mixture variances. Increasing the exposure
changes the count component; it does not automatically change the zero predictor.
Providing `x` where the model expects `z` changes the model, so use explicit column
mappings and retain those mappings with the fit.

The Student-t model's `log_scale` is not a log standard deviation. Its observation
variance is \(s^2\nu/(\nu-2)\). The degrees-of-freedom transform enforces finite
variance; models with \(\nu\le2\) are outside this registry entry. Long-tailed
responses can reduce sensitivity to outliers, but heavy tails do not solve omitted
covariates, dependence or an incorrect forecast origin.

For lognormal regression, \(\exp(\eta)\) is the conditional median, and
\(\exp(\eta+\sigma^2/2)\) is the conditional mean. The declared target returns
data-scale mean and variance. Taking the exponent of a fitted log mean alone would
answer a different question.

## Correlated Gaussian random slopes

`gaussian_correlated_random_slope` operates on a complete group of `x, y` rows:

\[
y_i=\beta_0+\beta_1x_i+b_0+b_1x_i+\epsilon_i,
\quad
\begin{bmatrix}b_0\\b_1\end{bmatrix}
\sim N\!\left(0,
\begin{bmatrix}\tau_0^2&\rho\tau_0\tau_1\\
\rho\tau_0\tau_1&\tau_1^2\end{bmatrix}\right),
\quad\epsilon_i\sim N(0,\sigma^2).
\]

Its coordinates are `beta0`, `beta1`, `log_sigma`, `log_tau0`, `log_tau1` and
`atanh_correlation`, with \(\rho=\tanh(\mathrm{atanh\_correlation})\).
The Gaussian integral is exact. An augmented QR factorization retains the latent
prior contribution even when the residual variance is very small or all group
covariates coincide. It does not form a rounded normal-equation matrix and then
subtract two nearly equal quadratic forms.

Use `fit_shared` with group columns for one population vector across independent
groups. All rows of each group must remain together, within the descriptor's
complete-unit bound. A group weight multiplies the whole group's marginal
likelihood. Arbitrary row weights would define a different covariance model and
are rejected. `fit_groups` estimates a separate vector per grouping key; that is
not a substitute for sharing population information across groups.

Two response-free targets are available:

- `new_group` uses the correlated latent prior and observation variance. It
  rejects supplied history because this target describes an unseen group.
- `existing_group` conditions on explicitly supplied complete history and uses
  exact Gaussian posterior moments of the latent intercept/slope, plus future
  observation variance.

For \(\beta=(1,2),\sigma=0.5,\tau_0=0.8,\tau_1=0.3,\rho=0.25\), a new
observation at \(x=2\) has mean \(5\) and variance
\(0.25+0.64+4(0.09)+4(0.25)(0.8)(0.3)=1.49\). Existing-group history changes both
the conditional mean and latent variance. Future rows in one group remain
correlated, although the public output gives each row's marginal moments rather
than a dense joint predictive covariance matrix.

The `forecast` API applies these targets to supplied future covariates. It does
not forecast the covariates themselves or introduce an AR process. Use the
existing AR(1) models for conditional time-series transitions. No target here
includes population-parameter posterior uncertainty.

## Priors, fixed coordinates and prepared points

The [extended target API](../python/docs/EXTENDED-TARGETS.md) permits Gaussian
priors with named means and precisions, selected exact L1 penalties and explicit
fixed coordinates. Priors are expressed in the native optimizer coordinates.
For example, a Gaussian prior on `log_sigma` is a prior on a transformed scale,
not on `sigma`; a change of intended probability measure needs the appropriate
Jacobian. Optimization of that target is MAP, not posterior sampling.

An L1 target uses the proximal solver and reports KKT stationarity separately from
the smooth gradient. A nonzero smooth score at an exact L1 solution is expected.
Fixing all coordinates produces an evaluation with explicit all-fixed status,
not a fictitious iterative fit. Weighted-mean reduction scales the entire summed
target by the same verified weight mass, including the one global prior.

`PreparedParameters` binds declared simulation truth, a sensitivity point or a
separately obtained posterior draw to a prepared model. It can predict and
forecast without fabricated convergence metadata. Declaring a posterior draw
does not run a posterior sampler. Preserve its source/provenance and distinguish
predictive variation across parameter draws from observation variance at one draw.

## Boundaries and reproducible checks

The optional [TMB/glmmTMB project](../reference/README.md) supplies real upstream
family/covariance examples, custom nonlinear and panel models, and serial
reference calculations. Those upstream capabilities are not automatically native
registry features. The original nonlinear random-amplitude draft is deliberately
not registered: its latent target can have multiple modes, so a zero-start local
Laplace solve would not establish the intended marginal likelihood.

Run the numerical and Spark commands in the
[new-model check guide](../python/docs/NEW-MODEL-CHECKS.md), then the
[isolated Compose harness](../integration/README.md) with the matching wheel and
native installation. Keep exact source, artifact, input, command and outcome
receipts. A local native ARM64 check does not establish AMD64 execution, GPU
support, multi-host scale or forecast calibration. Use the
[simulation studies](../studies/README.md) for explicitly seeded repetitions,
retained failures and Monte Carlo uncertainty.
