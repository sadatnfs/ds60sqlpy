# Named targets, fixed evaluation and declared parameters

The adapter exposes named Gaussian priors, exact selected L1, fixed coordinates,
bounded fixed-parameter evaluation and a separate parameter-set prediction route.
These additions preserve the original native process, identity, ledger, deadline
and cancellation paths. They do not add Python/R numerical workers or runtime
compilation.

Pure JVM mathematical/serialization checks cover these APIs. Actual prepared
native/Spark checks are defined in `FeatureSparkChecks`; consult current
source-bound qualification before claiming that a particular build/platform has
passed them. Older qualification JSON files describe their exact earlier source
identities and remain unchanged.

## Preserve the target when changing reduction

Legacy `l2_strength` keeps its original meaning: after sum/weighted-mean reduction,
add `l2_strength * sum(theta^2) / 2` on every optimization coordinate. This can
penalize intercepts and log-scales. It is not automatically coefficient-only ridge.

The new `regularization` block instead defines a summed likelihood target:

\[
 S(\theta)+\sum_{j\in G}\left[\frac{p_j}{2}(\theta_j-m_j)^2+
 \frac{1}{2}\log(2\pi/p_j)\right]+
 \sum_{j\in L}\lambda_j|\theta_j|.
\]

Under `weighted_mean`, the entire expression is divided by the validated global
likelihood weight mass. Priors are added once per shared vector, or once per
distinct independently fitted group vector. Selected coefficient names, centers
and positive precisions/strengths are explicit. Omitted names are unpenalized.
Gaussian priors are on the model's declared optimizer coordinates; a prior on
`log_sigma` is not a prior on sigma. A different measure/Jacobian is not inferred.
Nonzero legacy L2 mixed with this new block is rejected.

Gaussian terms include their normalizing constants. L1 is recorded as a penalty
without a Laplace-density constant. Overlapping Gaussian/L1 terms define an
additive point target; the objective is not advertised as normalized posterior
evidence. Priors plus optimization give a MAP/penalized point estimate, not
posterior samples. Arbitrary weights retain weighted/power-likelihood semantics.

## Worked normal-model target

Suppose the four observed values are `-1,1,3,5`, the observation scale is fixed
at 1, the prior on `mu` is normal with center 1 and precision 2, and L1 strength is 1.
The positive-coordinate stationarity equation is `4*mu-8+2*(mu-1)+1=0`, giving
mu 1.5. With L1 strength 20, the zero-coordinate subgradient contains zero and the
solution is exactly 0. These are analytic expectations, not fabricated worker
outputs. They are exercised by pure JVM and prepared-worker test sources.

```scala
import io.ds60.spark.tmbad.PythonBridge

val options = """{
  "initial_parameters":[0,0.2],
  "max_iterations":1000,
  "function_tolerance":0,
  "fixed_parameters":{"log_sigma":0},
  "regularization":{
    "schema_version":1,
    "coordinate_system":"native_optimizer_parameters",
    "normalization":"summed_likelihood_target",
    "gaussian":{"mu":{"mean":1,"precision":2}},
    "l1":{"mu":1}
  }
}"""
val fitted = PythonBridge.fitShared(observations, specification, artifactJson, options)
```

The existing model specification still declares response/id/group/order/weight
columns. Fixed named values must lie inside native bounds. On fitting they
explicitly replace their initial coordinates after the supplied initial vector
passes its original native domain check. Fixed evaluation instead requires an
exactly matching supplied point and never projects it silently.

L1 selects the proximal solver automatically. Explicit BFGS with L1 is rejected.
Gaussian-only targets use the original BFGS route unless an explicit supported
solver is selected. Equality-fixed gradients are excluded from the BFGS secant
update, because those coordinates are outside its optimization tangent space.
An all-fixed target makes one real evaluation and records `all_parameters_fixed`
and zero free parameters, without inventing optimization iterations.

## Convergence and saved model metadata

The proximal solver uses exact soft thresholding plus interval projection,
smooth majorization and composite-descent backtracking. It reports constrained
KKT residuals in summed-target and reduced units. Equality bounds have no zero
raw-gradient condition. A small step or function change with a large KKT residual
is a failed/stalled fit. General nonlinear targets get a first-order stationarity
claim, not a global optimum guarantee.

Unextended fits retain the strict schema 1 contract. Extended fits use schema 2
with a `target` object containing canonical penalties/fixed values, digest,
normalization, effective initial point, free count, solver settings, decomposed
loss and stationarity. The actual proximal trace is separate from the old BFGS
trace, which stays empty for proximal fits.

`fit.raw_gradient_inf` and `fit.projected_gradient_inf` continue to describe the
reduced smooth gradient, so they may be nonzero at an L1 optimum. Read the declared
KKT criterion for L1 convergence. Saved metadata rejects inconsistent digests,
fixed points, negative penalty components, invalid budget/trace records and
contradictory successful/failure statuses. A saved flag alone still cannot prove
historical execution without an actual source-bound receipt.

## Bounded fixed-parameter evaluation

```scala
val evaluation = PythonBridge.evaluateShared(
  observations, specification, artifactJson,
  """{"parameters":[2,0]}""",
  """{"reduction":"sum"}"""
)
```

The vector follows the exact prepared parameter order. The response is bounded
JSON with data/prior/L1 decomposition, full data and smooth gradients, L1
subgradient intervals, fixed mask, KKT norms, parameter/target identities and
complete partition/data/weight accounting. `weight_kind` is `observation` for row
models and `unit` for complete-unit models. The current route requires positive
rows/effective weight, as fitting does. It exposes no raw observations and no
unqualified exact Hessian. Invalid initial support returns no partial evaluation.

## Predict at declared parameters without a pretend fit

A parameter set is a distinct data-only document with kind
`spark-tmbad-parameter-set`. It contains model/artifact identity, complete
coordinates, a parameter-set ID, default key layout, purpose and provenance.
It has no `fit`, `converged`, optimizer trace or training-count fields.

Purposes are `simulation_truth`, `posterior_draw` and `sensitivity`. Their
provenance respectively binds generator/seed, posterior-target/sampler receipt
and chain/draw identity, or a reference digest. These checks validate structural
binding; a label/hash does not establish actual posterior sampling or calibration.

Use `predictAtParameters`, `predictConditionalAtParameters` or
`forecastAtParameters` with the same declared target/history/future column options
as ordinary prediction. `allow_unconverged` is not admitted on this route. Unit
models still require group layout, and ordered models require order layout.
The existing native output and bounded history/future machinery is reused.

Prediction columns carry Spark metadata keys `parameter_set_id`, `purpose` and
`parameter_digest`. One bounded vector is evaluated per call. Combining real
posterior draws requires preserving draw identities/weights and the total
variance `E[conditional_variance + mean^2] - E[mean]^2`, not merely averaging the
conditional variances. No generic sampler or draw-batch inference engine is
implemented by this prediction API.

The target-specification digest is dataset-independent. A full posterior-target
receipt must additionally bind its actual data/weight ledger and coordinate
measure. Artifact and data checks are never replaced by a penalty digest.

## Qualification commands

Use the current prepared toolchain and fresh output paths. Keep test classes in
a separate JAR so they cannot replace production classes:

```sh
python jvm/build.py --output /prepared/spark-tmbad.jar
python jvm/build_checks.py --production-jar /prepared/spark-tmbad.jar \
  --output /prepared/checks.jar
java -cp '/opt/spark/jars/*:/prepared/spark-tmbad.jar:/prepared/checks.jar' \
  io.ds60.spark.tmbad.ContractChecks
java -cp '/opt/spark/jars/*:/prepared/spark-tmbad.jar:/prepared/checks.jar' \
  io.ds60.spark.tmbad.TargetContractChecks
java -cp '/opt/spark/jars/*:/prepared/spark-tmbad.jar:/prepared/checks.jar' \
  io.ds60.spark.tmbad.RegularizationOracleChecks
```

`TargetContractChecks` may take one fresh output directory to export explicitly
synthetic JVM serialization fixtures for Python decoder parity. Their manifest
has no runnable native binary/JAR and is not runtime acceptance. After assembling
a real source-bound artifact, run `SparkChecks` and `FeatureSparkChecks` with that
manifest and fresh reports, then the required copied-package and separate-worker
Compose/recovery checks. Local CPU evidence does not qualify another architecture,
multiple machines or GPU execution.
