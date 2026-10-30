# ds60-spark-tmbad

This independent Python frontend passes Spark DataFrames through Py4J to a
prepared JVM adapter. The JVM distributes native TMBad likelihood evaluation,
fitting, prediction and forecasting in Spark tasks. Python does not evaluate
rows on executors. R is not required.

Importing `ds60_spark_tmbad` requires only Python's standard library. Prepare
PySpark 4.0.1, the matching Scala 2.13 JAR, and a native Linux artifact explicitly
before executing a model. This Python wheel contains no native binary, compiler,
JAR, TMBad source, runtime download or model compilation step.

Install from the package directory:

```sh
python -m pip install .
```

When PySpark is not already prepared, the optional `spark` extra declares the
qualified exact version. Install it deliberately during environment preparation:

```sh
python -m pip install '.[spark]'
```

Start Spark with the matching JAR in `--jars` or `spark.jars` before creating the
session. The manifest's absolute worker path identifies the matching prepared
executable on the driver. The JVM adapter verifies and distributes an immutable
worker snapshot through SparkFiles, then validates the local executor copy.
Executors need the matching Linux architecture, shared libraries and writable
executable temporary storage. Installing the Python wheel alone does not prepare
the native worker or load the JAR into an existing Spark session.

```python
from ds60_spark_tmbad import ModelSpec, PreparedRuntime, SparkTMBad

runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
spec = ModelSpec("normal", {"y": "measurement"}, id_columns=["row_id"])

fitted = api.fit_shared(
    observations,
    spec,
    options={"initial_parameters": [0.0, 0.0]},
)
print(fitted.model["fit"])
predictions = fitted.predict(
    requested_rows,
    options={"target": "response", "columns": {}, "output_prefix": "fit_"},
)
fitted.save("normal-fit.json")
```

`observations` and `requested_rows` are classic PySpark DataFrames with stable
`row_id` columns. `observations` also has a numeric `measurement` column.
`requested_rows` needs no response column because the model's `response` target
has no numerical input fields. Call `api.describe(spark, "normal")` to inspect
the authoritative prepared descriptor.

`fit_shared` estimates one parameter vector for the entire dataset.
`fit_groups` estimates separate models per group and returns `GroupedModels`,
whose `.models` property is a lazy Spark DataFrame. Materialize expensive group
fits once, for example by writing and rereading immutable Parquet before repeated
prediction actions. Both fitted result types expose
`.predict(frame, history=..., options=...)` and
`.forecast(history, future, options=...)` for declared model targets.

`FittedModel.load(path, runtime=runtime)` loads data-only JSON and checks its
model source, native binary, engine, platform and optional JAR identities.
Loading never imports a Python model class or executes code from the file.
Local file save defaults to refusing an existing path; `overwrite=True` is an
explicit replacement. For independent group models, persist the `.models`
DataFrame with Spark storage and rewrap it using `api.from_group_models(df)`.
The JVM validates each model row when executing predictions or forecasts.

In a complete copied project, see the package's [Python guide](../docs/PYTHON.md),
[model contracts](../docs/MODELS.md) and [protocol](../docs/PROTOCOL.md).
These sibling guides belong to the full project distribution; they are not
bundled in the Python-only wheel. The wheel's package metadata includes this
standalone introduction. Keep the complete project when preparing native models
or following the model gallery.
`examples/validate_installed.py` exercises the installed frontend with real
Spark and a prepared native artifact. Pure tests under `tests/` verify Python
contracts only; they are not distributed runtime evidence.

Original frontend code is MIT-licensed. The separately prepared TMBad dependency
retains its upstream TMB GPL-2 terms and notices. This frontend does not
relicense or bundle TMBad, Spark or their dependencies.


## Named targets and declared parameters in 0.2

The [extended-target guide](docs/EXTENDED-TARGETS.md) documents selected Gaussian
priors and L1, exact fixed coordinates, bounded `evaluate_shared` results and the
separate `PreparedParameters` type. A declared truth/sensitivity/posterior-draw
point has source-bound provenance without fabricated fit or convergence fields.
Its prediction metadata preserves point identity. Provenance validation alone
does not certify a posterior sampler or scientific calibration.

Legacy schema1 models remain readable against their exact supported 0.1.0 or
0.2.0 runtime. New target fits use schema2, with explicit loss components and KKT
semantics. New bridge methods require the matching prepared adapter; an old JAR
fails clearly instead of being patched or attached to a running Spark session.
The new runtime acceptance program is `examples/validate_extended.py`; source
and pure-contract checks are separate from actually executing that program.


## Added model checks

The [new-model check guide](docs/NEW-MODEL-CHECKS.md) provides independent native
value/gradient/Hessian references and an installed-wheel Spark check for the nine
added 0.2 models. It separates observed native qualification from Python/Spark
execution, parameter recovery and repeated-sample uncertainty studies.
