# Current interfaces and remaining boundaries

Native 0.2 now implements the named-target, fixed-evaluation and declared-parameter
interfaces below. Local Linux ARM64 Spark checks qualify those bounded API paths;
new simulation studies still need their own executed receipts. Torch capabilities
are stated separately. Historical 0.1 artifacts and observed results retain their
original version and exact source identities.

## Fixed-parameter evaluation

The Torch package exposes `DataFrameObjective.evaluate(parameters)` and returns a
bounded ObjectiveEvaluation. Native 0.2 exposes
`SparkTMBad.evaluate_shared(frame, spec, parameters, options=...)` with complete
named coordinates or the descriptor-ordered vector. It performs the same
source/model, partition, data-ledger and failure validation used by fitting and
returns bounded values, scores, count/weight accounting and target diagnostics.
It does not run an optimizer, collect observations or fabricate convergence.

The public evaluator currently returns first derivatives, not a distributed
Hessian. The native process exposes selected exact-model Hessians; its generic
random-effect Laplace path declares first outer derivatives only. An exact-model
Hessian reducer would need a separate public contract and qualification. Never
manufacture an exact Hessian label from finite differences of a score.

## Priors and selected penalties

Native 0.2 regularization identifies named Gaussian means and positive precisions,
selected L1 strengths, native optimizer coordinates, a summed-likelihood target
and a digest. A Gaussian term contributes its quadratic and normalizing constant
once per fitted parameter vector. Omitting a coordinate leaves it unpenalized;
an explicitly listed zero precision is rejected. A prior on log_sigma is a prior
on that optimization coordinate, with no implicit change-of-measure Jacobian.

For summed data loss S, selected normalized Gaussian loss P and selected L1 penalty
Q, the new target is `(S + P + Q) / d`, where d is one or the global likelihood
weight mass. Thus sum and weighted_mean preserve the point optimum. L1 is an
explicit penalty without a Laplace-density normalizer. Frequency, importance and
survey weights still require different statistical interpretations.

The legacy scalar l2_strength remains an all-coordinate penalty added after
reduction. Nonzero legacy L2 cannot be combined with the new regularization
block. A study must compare these distinct conventions explicitly. No prior is
inserted into every executor partition or observation. Torch's current scalar
option has not acquired the native named-target schema by analogy.

Named fixed_parameters are exact equality constraints, including known nuisance
scales. A supplied evaluation point must satisfy them already. All-fixed fitting
performs one evaluation, records all_parameters_fixed and estimates no coordinate.
Dense correlated priors on population parameters, general prior families,
arbitrary callbacks and parameter-sharing maps remain outside this schema. The
new correlated latent Gaussian slope model is a different feature from a dense
prior on the fitted population vector.

## Nonsmooth regularization

Native 0.2 implements selected exact L1 with proximal gradient and constrained KKT
qualification. Nonempty L1 selects that solver by default; explicit BFGS with L1
is rejected. At a zero coordinate, the smooth data/prior score can be nonzero
while the L1 subgradient interval satisfies KKT. Equality-fixed coordinates have
no free-direction KKT requirement. Study acceptance must use the declared target
stationarity and units, not the old smooth projected-gradient test.

The serial orthogonal-design reference supplies exact soft-thresholded solutions
and independent KKT checks. Its current four-column design is not the native
one-covariate linear_gaussian descriptor. A native intercept-and-slope study can
use a declared two-column orthogonal design and fix log_sigma. Normalized Gaussian
constants must be added when comparing a named-prior objective with the older
quadratic-only reference. Torch's L-BFGS-B route remains smooth; no new Torch
proximal optimizer or native/Torch named-target parity is claimed.

## Posterior and uncertainty operations

Neither package automatically supplies a posterior over population parameters.
MAP is a point estimator. Parameter-posterior Laplace would require the actual
negative log posterior curvature at a qualified interior mode, coordinate and
Jacobian declarations, and refusal or warnings for boundaries or multiple modes.
Random-effect Laplace integration is a different operation.

Actual posterior sampling needs a separately prepared sampler and its own
convergence, ESS, R-hat, divergence and posterior-predictive checks. Begin with
exact conjugate references and small serial samplers before claiming scalability.
An exact Gaussian fixed-parameter posterior reference does not turn all native
model families into generic Bayesian inference engines.

## Forecast schemas and covariance

Native known-group and unseen-group targets distinguish conditioning and pointwise
uncertainty for the prepared models, including the new exact correlated Gaussian
slope model. The public outputs remain marginal moments, not a full future joint
covariance. Torch exposes explicit point targets and does not automatically supply
the native history/forecast surface. A mathematical forecast derived from fitted
Torch parameters must remain labeled as such.

Study records need an explicit horizon/covariate scenario, available history,
missingness convention and uncertainty layers. New-group latent uncertainty and
population-parameter uncertainty cannot be silently omitted or double-counted.
A general latent AR1/OU model with measurement noise differs from directly
observed AR1. Cross-unit covariance still needs a coupled objective or complete
connected block rather than a naive partition split.

## Prediction from truth and supplied posterior parameter sets

Native PreparedParameters is a separate source-bound type with no fit, convergence
or training-count fields. It supports predict and forecast from one declared
parameter vector, with purpose simulation_truth, sensitivity or posterior_draw
and the corresponding provenance. The existing support, history, future-field,
row-identity and conditioning contracts still apply. allow_unconverged is rejected
for this type. Torch predict_dataframe already accepts an explicit vector; its
study records also need purpose and source.

A posterior label only validates structural provenance. It cannot prove that a
sampler ran, converged or produced a calibrated posterior. General draw batching,
joint path simulation and posterior-averaged forecasts remain study/sampler work.
Retain draw IDs and weights; combine moments by E[v + mu^2] - E[mu]^2 rather than
averaging conditional variances alone. Keep shared latent effects and innovations
within each path. Independent pointwise draws do not establish the intended joint
path distribution. Observations and all independent fitted models remain on Spark.

See the [implemented target contract](../../python/docs/EXTENDED-TARGETS.md),
[additional model contracts](../../docs/EXTENDED-MODELS.md), and
[new-model checks](../../python/docs/NEW-MODEL-CHECKS.md). Their API and numerical
qualification does not replace the study-specific Monte Carlo and classroom gates.
