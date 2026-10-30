# An exactly marginalized Gaussian random intercept

This model estimates shared population parameters from complete independent groups. All observations
in one group share a latent intercept, so a storage partition is not a valid statistical unit by
itself.

## Likelihood and parameterization

\[
Y_{gi}=\beta+u_g+\epsilon_{gi},\quad u_g\sim N(0,\tau^2),\quad \epsilon_{gi}\sim N(0,\sigma^2),\quad \Sigma_g=\sigma^2 I+\tau^2\mathbf1\mathbf1^T.
\]

The native objective integrates u exactly using the compound-symmetry covariance. The scalar unit
weight is applied once to the whole marginal group likelihood. Existing-group prediction uses the
supplied history to update that group's latent intercept; a new group uses its prior distribution.

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
    "gaussian_random_intercept"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "gaussian_random_intercept",
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

Existing-group variance combines future observation noise with posterior uncertainty about u.
New-group variance includes the full prior tau squared. Both condition on fitted population
parameters, so neither includes uncertainty in beta, sigma or tau.

## A fixed-parameter calculation

With beta=2, sigma=tau=1 and existing history [4,4], posterior latent mean is 4/3 and latent
variance is 1/3. A future observation has mean 10/3 and variance 4/3. A new group instead has mean 2
and variance 2.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/gaussian_random_intercept.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/gaussian_random_intercept

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json gaussian_random_intercept
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
used 11 iterations and 26 objective calls, including 0 reviewed numerical candidate rejections.
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

- Splitting one group into independent chunks to satisfy a row limit.
- Using fit_groups when the intended model has one shared beta and shared variance components.
- Using a new-group mean for an observed group without explicitly choosing that scientific target.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.