# Distributed likelihoods with DataFrames and PySpark ML

`ds60-spark-likelihood` is an independent Python package. Its primary DataFrame
and ML interfaces use Spark, CPU float64 PyTorch automatic differentiation and a
SciPy driver optimizer. They do not import a classroom server or require R.
Install the package and its optional Spark/Torch/SciPy dependencies explicitly
before execution; fitting never installs software. The repository's prepared
native runtime is the reproducible validation environment.

```python
from ds60_spark_likelihood.dataframe import DataFrameObjective, fit_independent_groups
from ds60_spark_likelihood.ml import SparkLikelihoodEstimator, SparkLikelihoodModel
```

The ML submodule requires PySpark. Importing the core package remains lightweight.
A source installation from the repository root can use
`python -m pip install './packages/spark-likelihood[spark,torch,scipy]'` in an
appropriate prepared environment. Spark also needs a compatible Java runtime.
Use the maintained runtime lock/build instructions for the exact qualified
versions. This guide's examples run inside that prepared Linux environment;
Windows learners can use Docker through WSL 2.

## Three different estimation problems

For a row-additive model, a worker evaluates independent observation losses and
their gradients. For shared fixed coordinates \(\theta\),

\[
F(\theta)=\sum_i w_i\ell_i(\theta),\qquad
\nabla F(\theta)=\sum_i w_i\nabla\ell_i(\theta).
\]

For a complete-unit model, a worker evaluates one scalar joint likelihood for an
entire independent group. Its weight applies to that joint contribution:

\[
F(\theta)=\sum_g w_g L_g(\theta),\qquad
\nabla F(\theta)=\sum_g w_g\nabla L_g(\theta).
\]

The unit must not be split into unrelated row losses. A covariance edge between
two units can invalidate this factorization, regardless of how the data are
partitioned in Spark. The package does not claim support for arbitrary cross-unit
latent covariance.

A third problem fits each group separately, producing a different parameter
vector for every group. `fit_independent_groups` is explicitly separate from the
shared estimator and initially supports row-additive models. Its outputs are
individual fitted states, never a silently averaged pooled model.

`reduction="weighted_mean"` divides a row model by the total observation weight
and a joint model by the total unit weight. It does not divide a group likelihood
by the number of rows. A requested global L2 penalty is added once after that
selected data reduction; changing the reduction changes the interpretation of
its coefficient. The MLE examples below use the default sum and zero penalty.

## Features, labels and weights are explicit

`featureCols` maps every canonical registered feature name to one existing
primitive numeric Spark column. `labelCol` is separate. An intercept is a real
explicit design column; the package does not secretly add one. Boolean, decimal,
string or vector-UDT feature columns need deliberate preparation before this
initial scalar-column interface. Null/nonfinite values fail instead of being
silently dropped or imputed.

Integer observations are checked before float64 conversion. An integer that
cannot be represented exactly, such as \(2^{53}+1\), is refused instead of
silently changed. Exact representable integers and explicit finite floating-point
measurements remain valid. Group identities and ordering keys retain their
appropriate integer/string meaning rather than passing through measurement
conversion.

Row models use `weightCol`. Joint models use `unitWeightCol`, whose value must be
constant across all rows of each complete unit. The adapter takes that value
once, not its row sum. The separate arguments make an accidental row/unit weight
substitution an error.

DataFrames have no implicit global row order. Prediction retains each original
row and all its columns, then appends one scalar output. Keep a row ID and sort
explicitly for display. Complete-unit temporal models additionally declare
`requires_order=True`; they must receive deterministic `orderCols`, and duplicate
within-unit keys are rejected. Exchangeable models can omit ordering keys; their
finite rows are canonically sorted within a bounded unit for reproducible input
identity without changing their declared exchangeable likelihood.

## Worked case 1: one shared normal model and unlabeled prediction

This model has no predictors, so its feature map is empty. The registered
prediction target is the conditional mean, not a sampled future observation or
an interval.

```python
import math
from pyspark.sql import SparkSession
from ds60_spark_likelihood.ml import SparkLikelihoodEstimator, SparkLikelihoodModel

spark = SparkSession.builder.master("local[2]").appName("normal-likelihood").getOrCreate()
training = spark.createDataFrame(
    [("a", -1.0), ("b", 0.0), ("c", 1.0), ("d", 2.0), ("e", 4.0), ("f", 5.0)],
    "row_id string, outcome double",
).repartition(2)
estimator = SparkLikelihoodEstimator(
    modelId="normal_mean",
    featureCols={},
    labelCol="outcome",
    initialParameters=[0.0, math.log(2.0)],
    parameterBounds=[[-10.0, 10.0], [-5.0, 5.0]],
    maxIter=80,
    tol=1e-5,
)
model = estimator.fit(training)
print(model.parameter_names, model.parameters)
print(model.fit_summary)
future = spark.createDataFrame([("new-b",), ("new-a",)], "row_id string")
model.transform(future).orderBy("row_id").show()
model.save("/tmp/likelihood-models/normal-v1")
reloaded = SparkLikelihoodModel.load("/tmp/likelihood-models/normal-v1")
reloaded.transform(future).orderBy("row_id").show()
spark.stop()
```

The mathematical mean MLE is approximately 1.8333. The second coordinate is log
standard deviation, with the ML variance using the number of observations as its
denominator. The future DataFrame contains no response column, and no fake label
is constructed. A constant-response dataset can lack an interior scale MLE;
explicit bounds define a constrained problem and must not be disguised as an
unconstrained interior estimate.

The model is returned only after the driver reports success and the projected
score meets the requested tolerance. Raw score, projected score, iterations,
function calls, active bounds, counts and a bounded trace tail remain visible.
Those checks establish numerical stopping behavior, not identifiability, global
optimality or calibrated uncertainty.

## Worked case 2: a linear Gaussian model in an actual ML pipeline

The two design columns are explicit. The registered flat coordinates are
`beta_0`, `beta_1`, `log_sigma`; canonical features are `x0` and `x1`.

```python
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import SparkSession
from ds60_spark_likelihood.ml import SparkLikelihoodEstimator

spark = SparkSession.builder.master("local[2]").appName("linear-likelihood").getOrCreate()
training = spark.createDataFrame(
    [
        (0, 1.0, -2.0, 0.1),
        (1, 1.0, -1.0, 0.6),
        (2, 1.0, 0.0, 1.6),
        (3, 1.0, 1.0, 2.1),
        (4, 1.0, 2.0, 3.2),
        (5, 1.0, 3.0, 3.8),
        (6, 1.0, 4.0, 4.85),
        (7, 1.0, 5.0, 5.35),
    ],
    "row_id int, intercept double, feature double, response double",
).repartition(2)
estimator = SparkLikelihoodEstimator(
    modelId="linear_gaussian",
    modelConfig={"feature_count": 2},
    featureCols={"x0": "intercept", "x1": "feature"},
    labelCol="response",
    initialParameters=[0.0, 0.0, 0.0],
    parameterBounds=[[-10.0, 10.0], [-10.0, 10.0], [-5.0, 3.0]],
    tol=1e-5,
)
pipeline = Pipeline(stages=[estimator]).fit(training)
future = spark.createDataFrame(
    [(20, 1.0, -3.0), (19, 1.0, 6.0)],
    "row_id int, intercept double, feature double",
)
pipeline.transform(future).orderBy("row_id").show()
pipeline.save("/tmp/likelihood-models/regression-pipeline-v1")
restored = PipelineModel.load("/tmp/likelihood-models/regression-pipeline-v1")
restored.transform(future).orderBy("row_id").show()
spark.stop()
```

An independent least-squares calculation on this fixture gives coefficients about
1.5267857143 and 0.7821428571. The normalized Gaussian likelihood's scale MLE uses
mean squared residuals. The native acceptance compares all fitted coordinates and
future means with those references and performs a real PipelineModel round trip.
An existing prediction column is not overwritten silently. Use a different
`predictionCol` if the input already contains that name.

## Worked case 3: a genuine joint Gaussian group likelihood without R

The complete-unit model integrates a group-specific Gaussian intercept exactly
inside Torch. It optimizes shared `beta`, `log_sigma` and `log_tau`. This is not
independent row least squares and does not pass a scalar loss through a per-row
kernel.

```python
import math
from pyspark.sql import SparkSession
from ds60_spark_likelihood.ml import SparkLikelihoodEstimator

spark = SparkSession.builder.master("local[2]").appName("joint-likelihood").getOrCreate()
centers = [-1.2, -0.8, -0.4, 0.0, 0.2, 0.7, 1.0, 1.3]
offsets = [-0.2, -0.1, 0.0, 0.1, 0.2]
records = [
    (f"g{g}", j, 3.0 + center + offset, 1.0)
    for g, center in enumerate(centers)
    for j, offset in enumerate(offsets)
]
training = spark.createDataFrame(
    records, "group_id string, ordinal int, y double, unit_weight double"
).repartition(2)
model = SparkLikelihoodEstimator(
    modelId="gaussian_random_intercept",
    featureCols={},
    labelCol="y",
    groupCol="group_id",
    orderCols=["ordinal"],
    unitWeightCol="unit_weight",
    initialParameters=[3.0, math.log(0.4), math.log(0.5)],
    parameterBounds=[[0.0, 6.0], [-6.0, 2.0], [-6.0, 2.0]],
    maxIter=120,
    tol=1e-5,
).fit(training)
print(model.parameters)
print("variances", math.exp(2 * model.parameters[1]), math.exp(2 * model.parameters[2]))
future = spark.createDataFrame([("unseen-a",), ("unseen-b",)], "entity string")
predicted = model.transform(future)
print(predicted.schema["prediction"].metadata["target"])
predicted.show()
spark.stop()
```

For this balanced, unweighted fixture, the exact MLE reference is
\(\hat\beta=3.1\), \(\hat\sigma^2=.025\), and \(\hat\tau^2=.6675\).
With \(G=8\) groups and \(m=5\) rows per group, the within-group residual sum of
squares is .8, giving \(\hat\sigma^2=.8/[8(5-1)]\). The mean squared deviation of
group means about the fitted overall mean is .6725, so
\(\hat\tau^2=.6725-.025/5\). These formulas are specific to the balanced example;
do not apply them blindly to unequal groups, unequal weights or constrained
boundary solutions.

The registered target is `new_group_mean`. It is a population-level mean for a
new group, not a conditional prediction using an estimated latent intercept for
an observed group. Requesting `conditional_group_mean` is refused. A different
conditional target needs its own declared inputs and validated algorithm.

## Independent group estimates remain separate

```python
from ds60_spark_likelihood.dataframe import fit_independent_groups

separate = fit_independent_groups(
    grouped_frame,
    "normal_mean",
    [0.0, 0.0],
    feature_columns={},
    label_col="y",
    group_col="unit",
    bounds=[[-10.0, 10.0], [-5.0, 5.0]],
    tolerance=1e-5,
)
separate.select("group_id", "parameters", "row_count", "projected_gradient_inf_norm").show()
```

Each executor fits a bounded group with the canonical row evaluator and SciPy
optimizer. It returns a DataFrame of distinct estimates and diagnostics; the raw
training observations are not collected on the driver. Each executor therefore
needs the optional Torch and SciPy dependencies. A failed fit is surfaced instead
of silently removing an unfavorable group.

This operation currently rejects complete-unit hierarchical models. Estimating a
shared between-group variance from one isolated group is generally not identified.
For such models use the shared complete-unit estimator above. Never average the
returned independent coefficient vectors as a substitute for the pooled score
solution. Even ordinary normal means need observation-count weighting for unequal
group sizes, while nonlinear likelihoods generally do not have that shortcut.

## Custom factories and prediction semantics

Write custom functions in an importable source module, declare a deterministic
row loss or a distinct complete-unit loss, and register its trusted factory on
the driver. The adapter captures the resolved RegisteredModel for executors;
workers do not need a hidden duplicate global factory registration. They do need
the same importable module/package deployed before execution. Source/configuration
fingerprints are checked in the driver and executor callbacks. This assumes a
trusted immutable deployment and explicit configuration. It is not cryptographic
authenticity or a proof of purity for arbitrary Python runtime state; do not
monkeypatch callback code, defaults or module state after registration.

Prediction callbacks receive only parameters and feature tensors, never response
labels. A model without a declared target cannot transform. Named targets such as
`success_probability`, `expected_count`, `conditional_mean` and `new_group_mean`
represent different scientific quantities, not cosmetic labels.

## Persistence, ownership and limits

JSON stores the model ID, configuration, registered descriptor, parameters,
parameter names, ML options and bounded fit diagnostics. The direct
`SparkLikelihoodModel.load` path reads this fixed JSON schema, resolves a factory
already registered by trusted application code and rejects a changed declared
source/configuration fingerprint. It does not unpickle executable state or import
an artifact-selected model module.

`PipelineModel.load` is an upstream PySpark mechanism with a broader trust
boundary: its metadata-directed class dispatch can import the Python module named
by a stage artifact before our stage reader runs. Use trusted pipeline artifact
directories; the individual-stage JSON reader does not make arbitrary pipeline
metadata inert or authenticated. Standard Spark metadata enables the real
PipelineModel round trips tested here. Keep the model's source package/version available when
resuming work; even a source formatting change can intentionally invalidate a
strict module-source fingerprint.

The persistence implementation supports local/shared filesystem paths and local
`file:` URLs visible to the driver. It does not claim general HDFS/cloud URI
support. `/tmp` paths in these examples are disposable. Use a dedicated writable
persistent volume or shared directory when retaining models across container
replacement. Saving to an existing directory fails by default; the individual
model's explicit `model.write().overwrite().save(...)` is
restricted to an owned model directory and uses staged replacement with a rollback
path. Unrelated files and links are refused by that stage writer. Upstream
`PipelineModel.write().overwrite()` has its own broader filesystem cleanup and is
not protected by our individual-stage ownership guard. Prefer new versioned
pipeline paths and retain recoverable copies before replacing a pipeline.

The DataFrame wrapper delegates caching to the canonical backends, which own only
their derived data. A caller's cached DataFrame is retained. Use the objective as
a context manager for direct evaluations. Input must be a deterministic immutable
snapshot: a cache can be recomputed after loss and is not a database transaction.

The initial driver optimizer supports a bounded low-dimensional parameter vector.
Large neural networks belong to the separate distributed-training integration,
not a million-coordinate driver L-BFGS call. Complete units have explicit row
bounds; the default Gaussian group model permits 256 rows. A group exceeding its
bound is rejected rather than split and reinterpreted as independent pieces.

Native acceptance is run from an installed wheel without R executables or
classroom imports. It covers actual row and complete-unit fits, custom driver-only
registration, label-free prediction, weighted-unit normalization, independent
fits, source refusal, cache ownership and real pipeline persistence. CPU local[2]
proof is distinct from remote-cluster, GPU, performance and statistical-coverage
claims. Consult the current source-bound qualification receipt for what was
actually executed.
