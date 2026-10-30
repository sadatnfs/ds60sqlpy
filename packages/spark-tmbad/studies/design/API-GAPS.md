# Interface requirements and current boundaries

This document proposes interfaces; it does not declare them implemented. The
current smooth optimizers and source-bound artifacts remain unchanged.

## Fixed-parameter evaluation

The Torch package already exposes `DataFrameObjective.evaluate(parameters)` and
returns a bounded `ObjectiveEvaluation` with value, gradient, data counts,
parameter digest and reduction metadata. The native worker protocol evaluates
values/gradients and selected exact-model Hessians, but a corresponding public
Spark fixed-parameter evaluator is not currently assumed by the study runner.

A proposed native `evaluate_shared(frame, spec, parameters, options)` should use
the same full partition, source/model, data-ledger and failure validation as
fitting. It must not expose a partial sum or collect observations. A declared
exact-model Hessian could be summed at common parameters; the generic native
random-effect Laplace path currently declares first outer derivatives only.
Never manufacture an exact Hessian label from finite differences of that score.

## Priors and selected penalties

A future prior/penalty specification needs named parameter selection, center,
precision/scale, coordinate measure, normalization convention and a digest.
For a diagonal Gaussian prior, the global negative log prior contributes
`0.5 * sum(precision[j] * (theta[j]-center[j])**2)` once. Zero precision on an
intercept means it is unpenalized, not that a proper Gaussian prior with infinite
variance has been numerically evaluated. Correlated Gaussian priors need a
validated positive-definite precision factor, not an arbitrary dense matrix.

Under weighted-mean reduction, reproducing a prior added to a summed likelihood
requires dividing that prior by the global likelihood weight mass as well. The
choice is part of the inferential target, not a tuning convenience. Frequency,
importance and survey weights have different statistical interpretations.

For now, an explicitly named all-coordinate L2 study can use the existing scalar
option. It records the penalty on intercept and log-scale coordinates. A
slope-only ridge/MAP comparison needs either the public evaluator plus an
explicit study-level global penalty, or a reviewed package prior interface.
No prior is inserted into every executor partition or every observation.

## Nonsmooth regularization

Exact lasso minimizes a smooth data loss plus `lambda * sum(abs(beta[j]))` on a
declared subset. It needs a proximal or coordinate-descent method and KKT checks
at zero coordinates. The existing native inverse-BFGS and Torch L-BFGS-B routes
are smooth optimizers. A derivative of `abs` at zero, epsilon smoothing or a
Gaussian prior is not an implementation of exact lasso.

The initial serial orthogonal-design oracle provides exact soft-thresholded
solutions and KKT checks. A study-level proximal implementation may call the
Torch public evaluator, with an explicitly qualified step rule and convergence
residual. Native distributed lasso waits for an equivalent public evaluator.
These tools must remain clearly distinguished from a new production optimizer.

## Posterior and uncertainty operations

Neither package automatically supplies a posterior over fixed/population
parameters. A MAP optimizer is a point estimator. Proposed posterior-Laplace
support would need the negative log posterior Hessian at a qualified interior
mode, positive curvature, coordinate/Jacobian declarations and a warning when
boundaries or multiple modes defeat the Gaussian approximation.

Actual posterior sampling needs a separately prepared sampler and its own
convergence, ESS, R-hat, divergence and posterior-predictive checks. Launching a
Spark job for every HMC gradient is possible in principle but is not established
as an efficient distributed Bayesian engine here. Begin with exact conjugate
references and small serial samplers; validate any distributed likelihood
against them before claiming scalability.

## Forecast schemas and covariance

Native known-group and unseen-group targets already distinguish conditioning and
pointwise uncertainty for the prepared models. The Torch package currently
exposes explicit point targets; it does not automatically provide the native
history/forecast surface. A comparison may derive a labeled mathematical
reference from fitted Torch parameters, but may not call that a Torch API forecast.

Future targets need an explicit horizon/time grid, covariate scenario, history
role, missingness/measurement-error convention, and whether they return a full
joint covariance or only pointwise moments. New-group latent uncertainty and
fixed-parameter uncertainty cannot be silently omitted or double-counted.
A general latent AR1/OU model with measurement noise differs from a directly
observed AR1 process. Cross-unit covariance needs a coupled objective or a
complete connected block, not a naive partition split.

## Prediction from truth and posterior parameter sets

Do not fabricate a converged MLE model document for each generating parameter or
posterior draw. A truth parameter, a fitted estimate and a posterior draw have
different provenance. The native worker protocol accepts explicit parameters,
but the current public fitted-model facade is not an appropriate container for
invented optimization diagnostics. The Torch `predict_dataframe` function already
accepts an explicit vector without claiming a fit; study records must still label
its purpose and source.

A proposed native `predict_at_parameters`/`forecast_at_parameters` surface should
accept a prepared runtime/model identity, named numeric coordinates, a bounded
parameter-set ID and an explicit purpose such as `simulation_truth`,
`posterior_draw` or `sensitivity`. It should validate the same support, history,
future fields, output identities and conditioning rules as ordinary predictions.
A posterior batch must carry a separate source/sampler/target receipt rather than
an invented `converged=true` field. The library can validate structural provenance;
a label alone cannot prove that samples came from a calibrated posterior.

Small parameter-draw arrays or Gaussian sufficient statistics can reside on the
driver. Observations remain distributed. Chunk draw batches within explicit
limits, retain draw IDs and random-number provenance, and do not serialize sampler
functions or native pointers. Posterior forecast paths must preserve shared
latent effects and cross-horizon innovations within each draw. Independent
pointwise draws cannot establish the intended joint path distribution.
