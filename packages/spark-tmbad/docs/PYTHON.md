# Python DataFrame API

The frontend is a driver API over the same JVM adapter used by Scala. A method
passes `_jdf` and JSON over Py4J. Native likelihood, derivative, prediction and
forecast work runs in the executor's prepared C++ worker process. The frontend
does not add Python UDFs, Python map functions or R to the model execution plan.

An upstream DataFrame can still require Python if its own plan contains a
Python UDF or PythonRDD. The package does not remove those upstream operators.
The supplied acceptance examples use Spark SQL and `range`, so their numerical
execution does not depend on Python executors. Prepared Parquet inputs provide
another JVM-native source for that boundary.

## Explicit environment preparation

Use a classic Spark 4.0.1 session with Scala 2.13 and a compatible JDK. Spark
Connect is unsupported. Install the independent wheel into the driver Python
environment:

```sh
python -m pip install ./python
```

Prepare the native binary, model registry and matching JAR separately. The
artifact manifest identifies their exact bytes and target Linux architecture.
Keep the worker and JAR at the manifest's absolute driver paths, and place
the matching JAR on the Spark classpath before creating a session:

```sh
spark-submit \
  --master 'local[2]' \
  --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/validate_installed.py \
  --manifest /opt/spark-tmbad/artifact.json
```

Those paths illustrate a prepared deployment. Select the paths actually emitted
by preparation. This command makes a local Spark execution, not a multi-node
qualification. For a cluster, the adapter distributes a verified immutable binary snapshot
through SparkFiles and checks its bytes on each executing task. Every executor
still needs the declared Linux architecture, compatible native libraries and
private writable/executable temporary storage. Provide adequate native memory
overhead in addition to JVM heap.
No runtime operation downloads an artifact or compiles model source.

The compiler and runtime ABI must also match. The worker's required glibc,
libstdc++/CXXABI and shared libraries must be available inside the executor image.
Architecture alone is insufficient: an executable built with a newer compiler
can fail to start in an older Spark runtime with a missing `GLIBCXX` or `CXXABI`
symbol version. Build against the intended executor's compatible toolchain and
run the prepared binary in that exact runtime before claiming Spark readiness.

```python
from ds60_spark_tmbad import FittedModel, ModelSpec, PreparedRuntime, SparkTMBad

runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
descriptor = api.describe(spark, "normal")
print(descriptor["parameter_names"])
print(descriptor["predict"])
probe = api.probe(spark, "normal")
```

`describe` returns bound metadata without a Spark job. `probe` explicitly runs
the JVM adapter's bounded native handshake in Spark. A probe is a readiness
check for the task placement actually observed, not proof that every machine
in a changing cluster is qualified. Every fit and prediction task performs
its own artifact and worker identity checks.

`from_manifest` checks bounded strict JSON and hashes local binary/JAR files by
default. A driver without those local files can use `verify_files=False` only
when its deployment deliberately supplies them to the executing JVM/native
hosts. This skips the Python file check; it does not waive the JVM's artifact
checks or distribute the files. `PreparedRuntime(manifest_dict)` validates
metadata only. Neither constructor loads native code.

## Shared fit and response-free prediction

This example creates fixture rows through Spark SQL, then fits one Gaussian
distribution. In an application, replace `observations` with a versioned,
immutable DataFrame source and keep its snapshot stable during optimization.

```python
observations = spark.sql("""
  SELECT id AS row_id, CAST(id + 1 AS DOUBLE) AS measurement
  FROM range(4)
""")
spec = ModelSpec(
    "normal",
    {"y": "measurement"},
    id_columns=["row_id"],
)
fitted = api.fit_shared(
    observations.repartition(2),
    spec,
    options={
        "initial_parameters": [0.0, 0.0],
        "max_iterations": 100,
        "gradient_tolerance": 1e-6,
        "reduction": "sum",
    },
)
print(fitted.model["parameters"])
print(fitted.model["fit"])

requested = spark.sql("SELECT id AS row_id FROM range(3)")
predicted = fitted.predict(
    requested,
    options={"target": "response", "columns": {}, "output_prefix": "fit_"},
)
predicted.show()
```

The maximum-likelihood mean is 2.5. The fitted standard deviation is
\(\sqrt{1.25}\), using the maximum-likelihood denominator of four. Parameter
order is the descriptor's `mu`, `log_sigma`; the returned target columns are
`mean` and `sd`, prefixed here with `fit_`. The requested frame contains only
row IDs. No dummy response is needed. Output preserves those identifiers;
Spark does not promise global row order. Row IDs must be globally unique; when
a natural ID repeats per group, declare the composite key explicitly, for
example `id_columns=["series", "time"]`.

An output name collision is an error. Choose another `output_prefix` instead
of overwriting an existing column. Numerical support, duplicates, missing keys,
invalid field mappings and model limits are also errors, rather than silent
row filtering.

## Independent group fits

```python
grouped_data = spark.sql("""
  SELECT id AS row_id,
         CASE WHEN id < 4 THEN 'A' ELSE 'B' END AS series,
         CAST((id % 4) + 1 + CASE WHEN id < 4 THEN 0 ELSE 100 END AS DOUBLE) AS y
  FROM range(8)
""")
grouped = api.fit_groups(
    grouped_data,
    ModelSpec("normal", {"y": "y"}, id_columns=["row_id"], group_columns=["series"]),
    options={"initial_parameters": [50.0, 4.0], "max_iterations": 200},
)
model_rows_path = "/owned/models/by-series"
grouped.models.write.mode("errorifexists").parquet(model_rows_path)
grouped = api.from_group_models(spark.read.parquet(model_rows_path))
grouped.models.show(truncate=False)
future_ids = spark.sql("""
  SELECT 100 AS row_id, 'A' AS series
  UNION ALL SELECT 101, 'B'
""")
grouped.predict(future_ids, options={"target": "response", "columns": {}}).show()
```

Group A estimates mean 2.5 and group B estimates mean 102.5. These are two fitted
parameter vectors. A shared fit of the combined input would estimate one pooled
mean. `.models` remains a distributed DataFrame containing group keys,
`tmbad_model_json` and fit diagnostics. No API call collects every group's model
on the Python driver. An explicit `.show()` above only previews bounded rows.

`fit_groups` returns a lazy Spark model DataFrame. Each downstream action can
recompute its fits unless the caller deliberately materializes the result. The
example writes once to a fresh immutable Parquet location and loads once before
prediction. Use storage shared by the executors in a cluster. Deliberate
`persist()` plus an action is another option when the caller owns its cache
lifetime; the package does not silently evict caller caches. This distinction
matters when many independent groups are expensive to fit.

## Conditional prediction and forecasts

Select exact target names and fields from the prepared model descriptor. A
target's `needs_history` flag distinguishes a response-free target from a
conditional target. A conditional prediction has two distinct input frames:

```python
conditional = fitted.predict(
    target_rows,
    history=history_rows,
    options={
        "target": selected_prediction_target,
        "columns": target_field_mapping,
        "history_columns": history_field_mapping,
    },
)
forecast = fitted.forecast(
    history_rows,
    future_rows,
    options={
        "target": selected_forecast_target,
        "history_columns": history_field_mapping,
        "future_columns": future_field_mapping,
        "output_prefix": "forecast_",
    },
)
```

The variables above deliberately name a selected model's contract. They are not
generic target defaults. The prepared normal model declares an independent future
observation target named `response`, with empty history. It repeats the fitted
Gaussian moments for each requested future row; it does not condition on a time
series. Linear Gaussian and Poisson/exposure row models similarly use explicitly
supplied future covariates.

For a random-intercept model, history supplies the observations used to estimate
the existing group's latent effect; a new-group target integrates over a new
effect instead. For an ordered AR(1) model, history and future keys determine
the endpoint, cadence and forecast horizon. The model declares whether outputs
are conditional means, latent variances, observation variances or covariances.
Those quantities do not automatically include parameter-estimation uncertainty.

`GroupedModels` exposes the same prediction and forecast methods. The JVM joins
each complete future group to its fitted model and matching history. Supply the
declared group and order columns consistently. A dependent group exceeding its
limit is rejected; repartitioning cannot make an invalid split valid.

This complete AR(1) example uses one ordered, synthetic series and three future
rows. The fitted model declares time cadence one. The future frame therefore
starts at 36, immediately after the final observed time 35.

```python
import math

history_rows = spark.sql("""
  SELECT id AS row_id, id AS time, 'A' AS series,
         CAST(1.0 + 0.3 * SIN(id / 2.0) + 0.2 * COS(id * 2.0) AS DOUBLE) AS y
  FROM range(36)
""")
series_fit = api.fit_shared(
    history_rows.repartition(2),
    ModelSpec(
        "ar1",
        {"time": "time", "y": "y"},
        id_columns=["row_id"],
        group_columns=["series"],
        order_columns=["time"],
    ),
    options={
        "initial_parameters": [1.0, math.atanh(0.4), math.log(0.3)],
        "max_iterations": 200,
    },
)
future_rows = spark.sql("""
  SELECT id + 1000 AS row_id, id + 36 AS time, 'A' AS series
  FROM range(3)
""")
forecasts = series_fit.forecast(
    history_rows,
    future_rows,
    options={
        "target": "conditional_history",
        "history_columns": {"time": "time", "y": "y"},
        "future_columns": {"time": "time"},
        "output_prefix": "forecast_",
    },
)
print(series_fit.model["fit"])
forecasts.orderBy("time").show()
```

The future frame has no `y`. It returns one row for each requested time with
`forecast_mean`, `forecast_variance` and `forecast_sd`. For fitted parameters
\(\mu, a, s\), the native model uses \(\phi=\tanh(a)\) and
\(\sigma=\exp(s)\). Conditional on the last observed value \(y_T\), horizon
\(h\) has mean \(\mu+\phi^h(y_T-\mu)\) and variance
\(\sigma^2\sum_{j=0}^{h-1}\phi^{2j}\). These moments condition on the fitted
parameters. Always inspect the fit diagnostics before interpreting them.

The installed acceptance example also includes a complete random-intercept
fixture. It compares existing-group and new-group predictions and forecasts
with independent Gaussian formulas, so those two conditioning cases cannot
silently become the same operation.

## Safe model persistence

```python
fitted.save("normal-model.json")
loaded = FittedModel.load("normal-model.json", runtime=runtime)
loaded.predict(requested, options={"target": "response", "columns": {}}).show()
```

Model save accepts one local filesystem file. The default refuses an existing
file. `overwrite=True` explicitly replaces it atomically. It does not implement
S3, HDFS or database storage. A JSON model contains parameters, mappings,
diagnostics and content identities, without training observations, native
pointers or executable Python imports. Loading checks model digest, parameter
order/domain, binary build/digest, native platform, engine and optional JAR hash.
A stale model or mismatched prepared runtime is rejected. Preserve the matching
prepared installation or image with the model JSON. The identity includes the
native binary hash, Linux architecture and JAR hash, so rebuilding the artifact
or changing ARM64 to AMD64 requires an explicit new qualification/migration
decision even when model names match. The package does not silently migrate
models between architectures or support a mixed-architecture executor set.
A driver may run on another OS when its actual native executors match the
declared Linux artifact; the driver OS does not change the model identity. The same wire JSON can
be exchanged with Scala: `fitted.to_json()` exports it and
`FittedModel.from_json(text, runtime=runtime)` validates and loads it.

The independent-model example above writes its rows once through Spark storage.
A later consumer can load that immutable result without repeating the fits:

```python
restored = api.from_group_models(spark.read.parquet(model_rows_path))
restored.predict(future_ids, options={"target": "response", "columns": {}}).show()
```

The supplied runtime remains explicit. Each model JSON is validated in the JVM
when an operation executes. Wrapping a DataFrame alone does not certify that
every persisted row is valid.

## Verification and failures

Run the pure contract suite without PySpark:

```sh
cd python
PYTHONPATH=src python -m unittest discover -s tests -v
```

These tests cover JSON and model/runtime binding, not Spark behavior. Run the
installed integration example in a prepared runtime for actual native and
Spark execution. Keep compilation, pure tests, native numerical checks, Spark
execution and remote cluster acceptance as separate evidence.

If the adapter is absent, restart Spark with its matching JAR. If binary or model
identity differs, prepare a matching artifact or deliberately refit under the
new one. Never edit a hash in a saved model to bypass a mismatch. If optimization
stalls, inspect raw/projected gradients, bounds, initialization and data support;
do not label a small objective change as convergence. The optional
`fit.rejected_candidates` count records reviewed numerical trial rejections.
A rejected initial evaluation is fatal; later candidate rejection discards the
whole distributed numeric result before backtracking. Artifact, transport,
resource and cancellation failures are never treated as numerical trial scores.

Prediction and forecasting reject `fit.converged=false` by default, including
independent group model rows. `options={..., "allow_unconverged": True}` is an
explicit diagnostic override only. It preserves the failed-fit diagnostics and
does not make those estimates acceptable scientific results. A converged score
also does not prove model identification or a global optimum.

The separate `examples/validate_native_oracles.py` runs the framed native worker
directly against original analytic references in `examples/numerical_oracles.py`.
It checks Gaussian marginal values/gradients/Hessians, scalar Poisson Laplace
modes and total outer gradients, existing/new-group moments, and AR(1) forecast
variances. Its receipts explicitly identify native-only execution. It provides
no evidence about Spark scheduling, JVM transport or executor packaging.
