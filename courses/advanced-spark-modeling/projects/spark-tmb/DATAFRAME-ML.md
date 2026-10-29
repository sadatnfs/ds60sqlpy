# Fit and predict with DataFrames and PySpark ML

This companion fits one shared custom likelihood using Spark to distribute data
units, native R/TMB to evaluate each unit's value and gradient, and SciPy1.15.3 on
the driver to update the common parameter vector. It also provides real Python
PySpark ML `Estimator` and `Model` stages. It does not collect the training rows
into the driver or serialize a live R objective into a Spark closure.

Prepare the optional Spark/TMB image using this project's main README first.
The examples require its registered `normal_location` and `linear_regression`
templates, typed parameter layout, response-free prediction declarations and
pinned SciPy environment. The examples save beneath `/models`, which must be a
dedicated writable mount. For a disposable first run, replace that prefix with
`/tmp/tmb-models`; temporary output does not survive container removal.
Run them with Spark4.0.1 inside that prepared Linux
image; Windows uses Docker through WSL 2. Importing the core companion alone does
not start Spark or R. Import `spark_tmb.ml` when using these optional ML stages.

## The statistical contract

At a shared fixed vector \(\theta\), each independent unit returns a scalar NLL
and a gradient in exactly the registered flat coordinate order. The driver uses

\[
F(\theta)=\sum_g F_g(\theta),\qquad
\nabla F(\theta)=\sum_g\nabla F_g(\theta).
\]

An independent-row model can be evaluated in bounded row chunks. A complete-group
model must keep its dependent rows together. The DataFrame adapter requires an
explicit group column and deterministic within-group ordering columns for that
case. It refuses groups above 4,096 observations instead of splitting a latent
unit and silently changing the likelihood.

DataFrames have no intrinsic global row order. Prediction preserves each original
row and column through partition-local processing and appends one scalar output.
It does not promise a global ordering. Keep a row-ID column and explicitly sort
for display or comparisons. Complete-group ordering is a different requirement:
its keys are sorted inside each bounded unit, and duplicate keys are rejected.
For temporal models, convert timestamps into a deliberate numeric or string
ordering representation with a stated timezone and tie policy.

The declaration that units are independent is a scientific assumption. A group
label cannot make a globally coupled spatial process independent. Use another
model/decomposition when latent covariance crosses units.

## Worked case 1: a shared normal model and genuinely unlabeled prediction

The registered `normal_location` template fits `mu` and `log_sigma` and explicitly
declares a conditional-mean prediction. Its prediction path takes a row count
without requiring any observed responses. Save the following as an owned project
script and run it with the prepared `spark-submit` environment:

```python
import math
from pyspark.sql import SparkSession
from spark_tmb.ml import TMBEstimator, TMBModel

spark = SparkSession.builder.master("local[2]").appName("normal-tmb-ml").getOrCreate()
training = spark.createDataFrame(
    [("a", -1.0), ("b", 0.0), ("c", 1.0), ("d", 2.0), ("e", 4.0), ("f", 5.0)],
    "row_id string, outcome double",
).repartition(2)

estimator = TMBEstimator(
    modelId="normal_location",
    dataCols={"y": "outcome"},
    initialParameters=[0.0, math.log(2.0)],
    parameterBounds=[[-10.0, 10.0], [-5.0, 5.0]],
    maxIter=80,
    tol=1e-5,
)
model = estimator.fit(training)
print(model.parameter_names, model.parameters)
print(model.fit_summary)

unlabeled = spark.createDataFrame(
    [("future-b", "keep this label"), ("future-a", "and this label")],
    "row_id string, note string",
)
model.transform(unlabeled).orderBy("row_id").show(truncate=False)

model.save("/models/normal-v1")
reloaded = TMBModel.load("/models/normal-v1")
reloaded.transform(unlabeled).orderBy("row_id").show(truncate=False)
spark.stop()
```

`dataCols` maps the registry's observation names to existing numeric Spark
columns. `initialParameters` and bounds follow the canonical registry order;
these are log-scale coordinates, so the second bound constrains log sigma.
The scalar predicted value is the fitted mean, approximately 1.8333 for this
fixture. It is not a simulated observation or an interval. No placeholder target
is manufactured for the two future rows.

The fit is accepted only when SciPy reports success and the bound-projected score
meets the requested tolerance. The result retains raw score, projected score,
iterations, function calls, active bounds and a bounded trace tail. These are
optimization diagnostics, not proof of identifiability, a global optimum or
statistical coverage. Constant-response normal data can lack an interior scale
MLE and should not be made to pass by clipping a failed result.

## Worked case 2: a vector parameter inside a Spark ML pipeline

The registered regression declares a two-element native `beta` vector and a
scalar log scale. Its canonical flat order is `beta_0`, `beta_1`, `log_sigma`.
Prediction maps `x_prediction` to the training field `x`, whose Spark column here
is named `feature`. The response column is absent from future data.

```python
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import SparkSession
from spark_tmb.ml import TMBEstimator

spark = SparkSession.builder.master("local[2]").appName("regression-tmb-ml").getOrCreate()
training = spark.createDataFrame(
    [
        (0, -2.0, 0.1),
        (1, -1.0, 0.6),
        (2, 0.0, 1.6),
        (3, 1.0, 2.1),
        (4, 2.0, 3.2),
        (5, 3.0, 3.8),
        (6, 4.0, 4.85),
        (7, 5.0, 5.35),
    ],
    "row_id int, feature double, response double",
).repartition(2)
estimator = TMBEstimator(
    modelId="linear_regression",
    dataCols={"x": "feature", "y": "response"},
    initialParameters=[0.0, 0.0, 0.0],
    parameterBounds=[[-10.0, 10.0], [-10.0, 10.0], [-5.0, 3.0]],
    tol=1e-5,
)
pipeline = Pipeline(stages=[estimator]).fit(training)
future = spark.createDataFrame([(21, -3.0), (20, 6.0)], "row_id int, feature double")
pipeline.transform(future).orderBy("row_id").show()
pipeline.save("/models/regression-pipeline-v1")
restored = PipelineModel.load("/models/regression-pipeline-v1")
restored.transform(future).orderBy("row_id").show()
spark.stop()
```

For a numerical reference, ordinary least squares on the same full fixture gives
the Gaussian coefficient MLE; the scale MLE uses residual squares divided by the
number of observations, not the residual degrees of freedom. The native tests
compare the fitted vector and prediction values with that independent reference.
Changing feature units requires a corresponding change in coefficient
interpretation, starts and bounds.

A prediction output column must be new. An existing `prediction` column is not
overwritten silently; choose another `predictionCol` explicitly. Missing,
non-numeric or case-ambiguous feature columns are rejected. The original rows and
unrelated columns remain attached to their predictions without a driver-side join.

## Complete groups and explicit ordering

Use the lower-level DataFrame objective to inspect a shared latent likelihood at
a specified parameter vector:

```python
import math
from spark_tmb.dataframe import DataFrameObjective
from pyspark.sql.functions import lit

# frame has: unit string, ordinal int, y double
frame = frame.withColumn("latent_group", lit(0))
with DataFrameObjective(
    frame,
    "random_intercept",
    columns={"y": "y", "group": "latent_group"},
    group_col="unit",
    order_cols=["ordinal"],
) as objective:
    result = objective.evaluate([0.7, math.log(0.4), math.log(0.8)])
    print(result.value, result.gradient, result.row_count)
```

The external `group_col` determines complete independent-unit ownership. The
registered model's internal `group` field is separate and must be mapped
explicitly. This example assigns zero to every row inside a unit because it
models one latent intercept for that complete unit. Models with several latent
subgroups must supply their actual contiguous zero-based internal indices;
the adapter does not silently replace them with zeros. Within-unit keys must be unique; a model requiring
several rows at the same timestamp should supply an additional tie-breaking key
that has scientific meaning. Numeric timestamps should use an explicit time unit.

The adapter persists only its newly derived units and releases that cache on
normal completion and failure. It leaves a caller-owned cached DataFrame intact.
Input must be deterministic and immutable for the fit: Spark can recompute lost
partitions, and an in-memory cache is not a transaction. Metadata binds unit IDs,
counts and contents so changed evaluations fail instead of silently mixing data.

`random_intercept` has no declared response-free prediction. A generic fitted
model's `transform` must therefore refuse it. Choosing a new-group marginal mean,
an existing-group conditional mean or a future observation involves different
latent information and uncertainty. The registry must explicitly implement and
qualify a target before the ML wrapper can expose it.

## Shared fitting and independent fitting answer different questions

`TMBEstimator.fit` performs one shared optimization. The existing
`SparkTMBObjective.fit_independent_units` instead fits every bounded independent
unit separately and returns separate keyed results. Averaging their coefficients
is not a shortcut to the pooled MLE. Even for a normal mean with equal variance,
unequal-sized groups need observation-count weighting to recover the pooled mean;
for general nonlinear likelihoods, averaging separate optima does not solve the
summed score equation.

The DataFrame wrapper deliberately does not reinterpret `groupCol` as a request
to average independently fitted models. For independent fits, construct explicit
complete units and use that separately documented API. For shared effects,
evaluate every contribution at the same driver-supplied parameter vector.

## JSON persistence and artifact mismatch

The direct `TMBModel.load` reader consumes bounded `model.json` numerical state
and an already prepared registry. It does not unpickle R objects or DLL pointers,
or choose a runtime path from the JSON document. Standard Spark ML metadata is
also written for pipeline dispatch. Upstream `PipelineModel.load` has a broader
trust boundary: it can import the stage class module named by pipeline metadata
before our reader runs. Only trusted pipeline directories should be loaded;
our fixed model JSON reader does not make arbitrary pipeline metadata inert. Runtime paths are
trusted application configuration; an advanced loader can select them explicitly
with `TMBModel.read().withRuntime(root=..., build_dir=...).load(path)`.

Load and transform compare the registry SHA256, model-source SHA256, native-library
SHA256 and R/TMB/Matrix/architecture identity with the prepared runtime. A mismatch
fails closed. Keep the qualified image pinned for a saved model; a new binary,
registry or architecture can require a deliberate migration or refit. JSON remains
readable across systems, but this implementation does not silently authorize a
new native artifact merely because its parameter count is the same.

Saving to an existing directory fails by default. `model.write().overwrite().save`
accepts only an existing owned TMB model directory with its expected files. It
stages a complete replacement and retains a rollback path during replacement;
unrelated files or links are refused by this individual-stage writer. Upstream
`PipelineModel.write().overwrite()` has broader filesystem cleanup and is not
protected by that ownership guard; prefer new versioned pipeline paths. The
implementation supports local paths or
local `file:` URLs visible to the driver, not arbitrary HDFS or cloud URI schemes.
Do not use a sensitive or unrelated directory as a model destination.

For persistence across container replacement, place `/models` on a dedicated
learner-owned Docker volume or a deliberately writable shared directory. The
read-only workshop's `/tmp` is disposable. Export or retain the model directory
before removing an ephemeral environment. The ordinary classroom progress volume
is separate and is not mounted or modified by these optional project tests.

## Scope of validation

The native acceptance suite checks the normal and vector-parameter regression
against closed-form/least-squares references, response-free prediction, retained
row identities/schema, caller-cache preservation, complete-group ordering and tie
rejection, JSON and pipeline round trips, and stale-artifact refusal. Pure host
contract tests validate schemas, bounds and detached fake-result handling; they do
not establish Spark/R execution. See the current native qualification receipt
before treating the optional stage as passed on an architecture.

This is a bounded CPU teaching companion. It does not establish remote-cluster
speed, GPU allocation, arbitrary model correctness or calibrated uncertainty.
