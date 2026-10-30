# Validating generic Laplace integration on a Gaussian model

This is the same Gaussian random-intercept model evaluated through the generic dense Laplace engine.
The gallery uses exactly the same observations, starting point and future cases as its exact
counterpart.

## Likelihood and parameterization

\[
L(\theta)=f(\theta,\hat u)+\tfrac12\log H_{uu}(\theta,\hat u)-\tfrac12\log(2\pi),\qquad f_u(\theta,\hat u)=0.
\]

A Gaussian joint density is quadratic in its latent coordinate, so the Laplace formula is exact for
this model. This makes it a useful oracle for the generic mode, curvature and total outer-gradient
machinery. The descriptor advertises first outer derivatives only for the generic Laplace route.

## The actual fixture

The shared gallery fixture contains 80 observations across 10 complete groups. Its native fit fields
are `y`. Row identity is `row_id`, with explicit `series` group keys. The fixed-seed generator
writes 12 significant digits of canonical precision. These are public synthetic observations, not a
production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `beta` | 0.7 | 0.5 |
| `log_sigma` | -0.7985077 | -0.5108256 |
| `log_tau` | -0.5108256 | -0.2231436 |

Generating values describe how the fixture was constructed. They are not claimed to be the exact MLE
of a finite sample. Stored log or atanh coordinates must be transformed before interpreting their
original-scale scientific quantities.

## Fit the DataFrame

Run from the package directory with a prepared classic Spark session named `spark`. The common
`frame` helper constructs a bounded SQL `VALUES` DataFrame; it does not introduce a PythonRDD or
Python UDF into the executor plan.

```python
import json
import sys
from pathlib import Path
from ds60_spark_tmbad import ModelSpec, PreparedRuntime, SparkTMBad

sys.path.insert(0, str(Path("python/examples").resolve()))
from gallery.run_gallery import frame

recipe = json.loads(Path("python/examples/gallery/fixtures.json").read_text())["cases"][
    "gaussian_random_intercept_laplace"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "gaussian_random_intercept_laplace",
    {"y": "y"},
    id_columns=["row_id"],
    group_columns=["series"],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={
        **recipe["fit_options"],
        "initial_parameters": [0.5, -0.510825623766, -0.223143551314],
    },
)
print(fitted.model["parameter_names"])
print(fitted.model["parameters"])
print(fitted.model["fit"])
```

The shared fit uses one population parameter vector across all input partitions. Inspect
`converged`, the raw/projected scores, active bounds and the stop reason. The API withholds
predictions from an unconverged fit by default; do not use a diagnostic override to make an example
appear successful.

## Response-free prediction

```python
history = training.where("series = 's0'")
requested = frame(
    spark,
    [{"row_id": 1000, "series": "s0"}, {"row_id": 1001, "series": "s0"}],
    ["row_id", "series"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    history=history,
    options={
        "target": "existing_group",
        "columns": {},
        "output_prefix": "prediction_",
        "history_columns": {"y": "y"},
    },
)
predicted.orderBy("row_id").show()
```

The requested rows contain no future `y`. A history-dependent target receives its historical
response in a separate DataFrame. Native field names and Spark column names are mapped explicitly
instead of inferred from their spelling.

## Forecast the declared target

```python
future = frame(
    spark,
    [{"row_id": 1000, "series": "s0"}, {"row_id": 1001, "series": "s0"}],
    ["row_id", "series"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "existing_group",
        "history_columns": {"y": "y"},
        "future_columns": {},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

The second worked case requests a new group or stationary series, with an ID absent from training
and an explicitly empty history:

```python
unseen = frame(
    spark,
    [{"row_id": 2000, "series": "unseen"}, {"row_id": 2001, "series": "unseen"}],
    ["row_id", "series"],
    ordered=False,
)
new_group = fitted.forecast(
    training.limit(0),
    unseen,
    options={
        "target": "new_group",
        "history_columns": {"y": "y"},
        "future_columns": {},
        "output_prefix": "new_group_",
    },
)
new_group.orderBy("row_id").show()
```

The guide's existing/new-group targets use the model's declared Gaussian conditional moments.
Inner-mode stationarity and positive curvature are checked separately from outer fit convergence. A
generic Laplace objective requires smooth, correctly normalized joint density code.

## A fixed-parameter calculation

The fixed beta=2, sigma=tau=1, history [4,4] calculation gives the same mean 10/3 and variance 4/3
as exact Gaussian integration. Agreement here establishes a Gaussian case; it does not establish
exactness for Poisson or arbitrary non-Gaussian integrals.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/gaussian_random_intercept_laplace.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/gaussian_random_intercept_laplace

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json gaussian_random_intercept_laplace
```

The Python script saves and reloads model JSON and checks the small predicted tables against
independent formulas at the returned fit. The Scala counterpart exercises the same JVM facade,
fixture and declared targets, checking convergence, finite outputs and retained row identities.
Those are separate execution records.

## Recorded execution

Observed in the installed Python wheel on Linux arm64, Spark 4.0.1, `local[2]`.

The native build is `324c97bdfa9c` and JAR digest is `80e5f77b54db`. The [retained
report](../../qualification/arm64-python-gallery.json) contains full identities, source hashes,
diagnostics and unrounded values.

| Stored parameter | Observed estimate | Original-scale interpretation |
| --- | --- | --- |
| `beta` | 0.68134204 | 0.68134204 |
| `log_sigma` | -0.83300204 | sigma = 0.43474221 |
| `log_tau` | -1.1250752 | tau = 0.32462805 |

The fit converged with projected gradient norm 5.7134012e-06; raw gradient norm 5.7134012e-06. It
used 11 iterations and 26 objective calls, including 3 reviewed numerical candidate rejections.
Observed objective value: 55.362764. Active bound indices: `[]`.

### Observed prediction: `existing_group`

| `row_id` | `series` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | s0 | 0.64899373 | 0.20829946 | 0.45639836 |
| 1001 | s0 | 0.64899373 | 0.20829946 | 0.45639836 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: exact posterior latent and future observation variance; parameter uncertainty excluded.

### Observed prediction: `new_group`

| `row_id` | `series` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 2000 | unseen | 0.68134204 | 0.29438416 | 0.5425718 |
| 2001 | unseen | 0.68134204 | 0.29438416 | 0.5425718 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: prior latent and observation variance; shared latent induces cross-step dependence.

### Observed forecast: `existing_group`

| `row_id` | `series` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | s0 | 0.64899373 | 0.20829946 | 0.45639836 |
| 1001 | s0 | 0.64899373 | 0.20829946 | 0.45639836 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: exact posterior latent and future observation variance; parameter uncertainty excluded.

### Observed forecast: `new_group`

| `row_id` | `series` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 2000 | unseen | 0.68134204 | 0.29438416 | 0.5425718 |
| 2001 | unseen | 0.68134204 | 0.29438416 | 0.5425718 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: prior latent and observation variance; shared latent induces cross-step dependence.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Calling this result a general exact random-effects integrator.
- Differentiating only the joint density at a frozen latent mode and dropping curvature derivatives.
- Requesting an outer Hessian when the descriptor declares only first derivatives.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.