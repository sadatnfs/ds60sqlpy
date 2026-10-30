# Priors, exact lasso, posterior inference and simulation evidence

Optimization and inference have separate targets. Integrating a normalized
random effect can give a marginal likelihood whose population parameters are
estimated by ML. Adding a prior on those parameters and optimizing gives MAP.
Neither operation alone samples their posterior or propagates all parameter
uncertainty into a forecast.

## Worked contrast: ridge and exact lasso

The Gaussian ridge case uses a nonzero prior center on a selected slope and
leaves the intercept unpenalized. Its analytic solution checks the TMB optimum.
A prior is added once to the summed data likelihood. Repeating it per observation
or partition changes its strength. Dividing only the likelihood by the sample
size while holding a prior fixed also changes the target.

The lasso reference minimizes

\[
 \|y-X\beta\|^2/(2\sigma^2)+\sum_j\lambda_j|\beta_j|.
\]

Its coordinate update uses exact soft thresholding and its acceptance criterion
is the KKT residual. At a zero coordinate, \(|g_j|\le\lambda_j\); at a nonzero
coordinate, \(g_j+\lambda_j\operatorname{sign}(\beta_j)=0\). It does not call
ordinary BFGS through `abs()` or replace lasso with a smooth approximation.

For an orthogonal design with 20 rows, coefficients `(2,0.8,0.03)`, known sigma 1
and penalties `(0,2,2)`, the exact result is `(2,0.7,0)`. The pure R oracle checks
this result and the KKT residual. That is an executed mathematical reference
when its test passes, not qualification of a generic distributed lasso solver.

## Worked contrast: a posterior and a mode

For a proper Gaussian coefficient prior with precision \(P\), known noise scale
and Gaussian observations, the posterior is exactly Gaussian with

\[
 V=(X^TX/\sigma^2+P)^{-1},\qquad
 m_{post}=V(X^Ty/\sigma^2+Pm_0).
\]

The prior mean \(m_0\) is the supplied prior center; the returned `mean` is
the posterior mean \(m_{post}\). The reference API keeps those objects
separate. A response prediction has variance
\(\sigma^2+x_*^TVx_*\), including population-coefficient uncertainty.
The independent posterior draws in this case are exact Gaussian draws, not
MCMC. Draw-count/Monte Carlo checks do not imply a generic sampler for the other
models. For observations 1, 2, 3 with sigma 1 and a standard-normal mean prior,
the posterior mean is 1.5, variance 0.25 and predictive variance 1.25.

The glmmTMB prior example instead compares a logistic MAP with an independently
written penalized objective. Its nonzero slope-prior mean is explicit. A matching
mode verifies that objective contract; it does not produce posterior samples.
The nonlinear and mixed-model cases likewise keep population-parameter
uncertainty separate from latent-effect integration.

An MLE coordinate reparameterization adds no Jacobian. A posterior density
expressed against a different integration measure requires its Jacobian.
Consequently, a density mode depends on coordinates. The examples do not
fabricate a converged-fit record for a generating truth or posterior draw.

## Interpreting a simulation ledger

Each attempt has a case, options, deterministic seed, source/preparation binding,
status and retained output or failure. Seeds differ across independent generated
datasets. Failures are never removed or replaced with favorable seeds.

Bias and MSE over successful estimates are conditional on success. MCSE uses the
sample standard deviation across those independent dataset-level statistics.
A single successful replication has no estimated MCSE. The failure-rate Wilson
interval remains informative when zero failures are observed. A timed-out study
reports how many requested replications were never attempted.

Where pointwise forecast coverage is present, it is first averaged within one
generated dataset. Replicates, not the correlated forecast horizons, determine
the MCSE. Conditional coverage among returned intervals and procedural coverage
counting failed fits are different outputs. The plug-in Gaussian intervals omit
population-parameter uncertainty unless a case explicitly adds it.

A few fixed smoke seeds validate execution paths and numerical contracts. They
do not establish nominal 95% coverage, robustness to misspecification, scaling or
performance superiority. A substantive study must predeclare its scenario grid,
replication count, known/new-group target, leakage-safe tuning/assessment split
and uncertainty layers, then report all failures and Monte Carlo uncertainty.
