# Prepare a custom C++ likelihood

Custom models enter through [native/models/custom_models.hpp](../native/models/custom_models.hpp).
Its `custom_models()` function returns reviewed model declarations and C++
functors. The worker registry includes those models when the artifact is built.
There is no runtime source string, Python import path, compiler flag or R object
in a fit request.

The supplied `quadratic_gaussian` extension is an original complete example.
It models \(y_i=\beta_0+\beta_2x_i^2+\epsilon_i\), with independent Gaussian
errors of standard deviation \(\sigma\). Its ordered parameter vector is
`intercept`, `curvature`, `log_sigma`; its fit fields are `x`, `y`.

## Declare data and parameters before differentiation

A native `Model` has a descriptor, input validator, objective and optional
prediction callback. The descriptor binds the following choices:

- A stable model ID and version, with a digest generated during preparation.
- Ordered fit field names and fixed parameter names.
- Parameter bounds and the row or complete-unit factorization.
- Random-effect dimension and `none`, `exact` or `laplace` marginalization.
- Whether the unit is ordered, its maximum size and supported derivative orders.
- Separate prediction/forecast targets, each with fields, output columns,
  conditioning, uncertainty and a `needs_history` flag.

Native data rows follow descriptor field order, independently of DataFrame
storage order. `ModelSpec.columns` supplies the mapping. IDs, group keys and
order keys are explicitly supplied to the JVM adapter. Do not infer an observed
response, exposure, censoring variable or time index from a column's spelling.

## Row objective and its weights

The extension's objective receives AD parameters and ordinary numerical data.
The existing implementation is equivalent to:

```cpp
model.objective = [](const ADVector &p, const Data &data) {
  using std::exp;
  AD total = 0;
  for (std::size_t i = 0; i < data.rows.size(); ++i) {
    const double x = data.rows[i][0];
    const AD residual = data.rows[i][1] - p[0] - p[1] * x * x;
    total += data.weights[i] * (p[2] + 0.5 * log_two_pi +
                                0.5 * residual * residual * exp(-2 * p[2]));
  }
  return total;
};
```

The callback includes each row weight exactly once and returns a scalar negative
log likelihood. Keep normalization constants when the objective is advertised
as normalized likelihood. Data-only functions such as a count's factorial term
can use ordinary C++ arithmetic. Parameter-dependent calculations must remain
in AD arithmetic so their derivatives are retained.

Input validation applies to the data's scientific support, beyond matrix shape
and finiteness. For the quadratic example, both fit and prediction reject design
values outside the declared numerical domain. A prediction callback needs its
own field checks because its inputs need not contain the fit response.

## Prediction and future covariates

The quadratic extension declares `response` with fields `x` and output columns
`mean`, `variance`, `sd`. At fitted parameters it returns
\(\beta_0+\beta_2x^2\), \(\sigma^2\), and \(\sigma\). It does not require `y`.
Its forecast hook declares the same moments for independently modeled future
observations at supplied covariates, with empty history. This does not add a
time-series relationship.

After preparing and selecting an artifact containing this extension:

```python
import math
from ds60_spark_tmbad import ModelSpec

training = spark.sql("""
  SELECT id AS row_id, CAST(id / 4.0 - 2 AS DOUBLE) AS x,
         CAST(1.5 + 0.7 * POWER(id / 4.0 - 2, 2) + 0.2 * SIN(id) AS DOUBLE) AS y
  FROM range(16)
""")
fitted = api.fit_shared(
    training.repartition(2),
    ModelSpec("quadratic_gaussian", {"x": "x", "y": "y"}, id_columns=["row_id"]),
    options={"initial_parameters": [1.0, 0.5, math.log(0.4)]},
)
requested = spark.sql("""
  SELECT 100 AS row_id, CAST(-1.0 AS DOUBLE) AS design
  UNION ALL SELECT 101, CAST(1.5 AS DOUBLE)
""")
print(fitted.model["fit"])
fitted.predict(
    requested,
    options={"target": "response", "columns": {"x": "design"}},
).show()
```

`api` is the explicitly prepared `SparkTMBad` client from the Python guide.
The frontend does not compile the extension when this example executes.

## Complete units and generic Laplace models

For a unit model, each callback receives one complete independent group. The
engine applies the scalar unit weight to the resulting objective once. Do not
replace a unit weight with per-row weights or split a dependent group into
independent pieces.

A prepared generic Laplace model sets `fit_kind="unit"`,
`marginalization="laplace"`, `random_dimension=q`, and currently
`derivative_orders={1}`. Its descriptor lists only the \(d\) fixed parameters.
During joint evaluation, the AD vector contains those \(d\) parameters followed
by the \(q\) latent effects. The objective returns the normalized joint negative
log density of data and random effects. The Gaussian and Poisson
random-intercept implementations in [models.hpp](../native/include/ds60_tmbad/models.hpp)
show this contract.

The engine solves for a local latent mode, checks its score and positive
curvature, and evaluates the Laplace marginal objective. Its outer gradient
includes the mode's effect on curvature. Differentiating only the joint density
at a frozen mode would produce a different gradient. Dense limits are \(q\le8\)
and \(d+q\le16\), with a separate complete-unit row limit. These limits do not
make an arbitrary multimodal joint density globally optimized.

Prediction remains an author-declared callback. For a Poisson random intercept,
the existing-group target uses approximate Gaussian posterior moments from the
Laplace mode/curvature, while a new group uses exact prior lognormal moments.
Both exclude parameter-estimation uncertainty. The prepared Poisson random-slope
example now declares the same existing/new-group distinction for future x and
exposure. Its existing-group calculation uses the full two-dimensional posterior
covariance, including its off-diagonal term. A new custom model still needs its
own explicit prediction and forecast hooks; the transport cannot invent them.

## Smoothness and recorded control flow

The Laplace engine records the joint objective once per complete unit and outer
parameter evaluation, then reuses that tape while Newton iterations change the
latent coordinates. An ordinary C++ branch chosen from the current numerical
value of an AD parameter or latent effect can therefore freeze the branch that
was taken during recording. Later iterates may evaluate the wrong expression.
Reusing a recorded tape is not automatic retaping.

Use a smooth formulation across the declared parameter/latent domain, or only
AD conditional operations whose value and derivative behavior have been
explicitly qualified for this backend. Test both sides and the transition of
every parameter-dependent condition. A branch based only on fixed data can
define a recording path for that data, but it still needs its declared support
and shape checks. Do not convert AD coordinates to ordinary doubles to choose
the model expression.

The inner mode needs valid gradient and curvature; the marginal outer gradient
also differentiates curvature. Nonsmooth penalties, boundary modes and arbitrary
branching do not become valid Laplace models merely because a C++ template
compiles. This interface does not promise unchanged TMB-template compatibility.
The solver returns a locally stationary mode with checked positive curvature,
within the dense \(q\le8\), \(d+q\le16\) limits. It does not implement a solver
for globally coupled sparse random fields.

## Qualify and rebuild the artifact

Add independent mathematical oracles before treating a custom model as ready.
Check changed data, non-optimal parameter points, support failures and two
finite-difference steps. Verify complete-unit behavior, weights and each named
prediction/forecast target. Gaussian exact integration can validate a Laplace
implementation in that Gaussian case; it cannot establish exactness for a
non-Gaussian integral.

Rebuild the worker and manifest through the preparation route, then rebuild or
select the matching JAR. Preserve source, compiler, dependency, binary and model
digests. Run direct native numerical checks and the actual installed Spark path
as separate acceptance steps. A changed prepared source identity requires a
matching runtime and deliberate refitting or model migration; editing stored
hashes is not migration.

Trusted custom functors run under the worker's process/resource restrictions.
They must not spawn processes, access networks, compile source or retain a native
pointer across tasks. An invalid initial evaluation is fatal. During later line
searches, only reviewed numerical domain, inner-mode, curvature or nonfinite
evaluation failures can reject an entire candidate, after the response identity
and terminal error exit have been verified. Every partial numeric contribution
for that candidate is discarded. Protocol, artifact, resource and cancellation
failures remain hard failures.

`fit.rejected_candidates` records this numerical backtracking. It does not relax
the inner mode score or the outer convergence criteria. Choose transforms,
bounds and input validation that make the intended optimization domain usable.
A failed worker is terminated and cannot be reused for a later candidate.
