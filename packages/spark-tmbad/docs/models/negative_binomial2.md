# An NB2 likelihood for overdispersed counts

NB2 adds a positive shape parameter to a log-linear count mean with exposure. It can represent
conditional variance larger than the mean while retaining an explicit normalized count likelihood.

## Likelihood and parameterization

\[
\mu_i=e_i e^{\beta_0+\beta_1x_i},\quad k=e^r,\quad P(Y=y)=\frac{\Gamma(y+k)}{\Gamma(k)\Gamma(y+1)}\left(\frac{k}{k+\mu}\right)^k\left(\frac{\mu}{k+\mu}\right)^y,\quad \operatorname{Var}(Y)=\mu+\mu^2/k.
\]

The descriptor orders intercept, slope and log_shape. Larger shape approaches the Poisson variance;
shape is the inverse of several common dispersion conventions. The native implementation uses
bounded, independently checked special-function arithmetic and retains integer-count support checks.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `x, exposure, y`.
Row identity is `row_id`. The fixed-seed generator writes 12 significant digits of canonical
precision. These are public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `intercept` | 0.2 | 0 |
| `slope` | 0.6 | 0.3 |
| `log_shape` | 1.098612 | 0.6931472 |

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
    "negative_binomial2"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "negative_binomial2",
    {"x": "x", "exposure": "exposure", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.0, 0.3, 0.69314718056]},
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
history = training.limit(0)
requested = frame(
    spark,
    [{"exposure": 1.0, "row_id": 1000, "x": -0.5}, {"exposure": 1.5, "row_id": 1001, "x": 1.0}],
    ["exposure", "row_id", "x"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    options={
        "target": "response",
        "columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "prediction_",
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
    [{"exposure": 1.0, "row_id": 1000, "x": -0.5}, {"exposure": 1.5, "row_id": 1001, "x": 1.0}],
    ["exposure", "row_id", "x"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "response",
        "history_columns": {"x": "x", "exposure": "exposure", "y": "y"},
        "future_columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

Returned variance is count variance at the fitted shape. It includes the NB2 mixing variation
represented by the likelihood but excludes uncertainty in estimating its parameters. Future rows
still require positive exposure.

## A fixed-parameter calculation

For mean 6 and shape 3, observation variance is 18. For the same mean and shape 30, variance is 7.2.
The mean is unchanged by this comparison, but predictive count variability changes substantially.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/negative_binomial2.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/negative_binomial2

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json negative_binomial2
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
| `intercept` | 0.37781473 | 0.37781473 |
| `slope` | 0.48672345 | 0.48672345 |
| `log_shape` | 1.4359766 | shape = 4.2037485 |

The fit converged with projected gradient norm 8.9461374e-07; raw gradient norm 8.9461374e-07. It
used 9 iterations and 27 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 232.87931. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1 | 1.1439109 | 1.4551883 | 1.2063119 |
| 1001 | 1 | 1.5 | 3.5608643 | 6.5771613 | 2.5645977 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: NB2 observation variance mu+mu^2/shape; no parameter uncertainty.

### Observed forecast: `response`

| `row_id` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1 | 1.1439109 | 1.4551883 | 1.2063119 |
| 1001 | 1 | 1.5 | 3.5608643 | 6.5771613 | 2.5645977 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: NB2 observation variance mu+mu^2/shape; no parameter uncertainty.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Using a dispersion coefficient where this parameterization requires shape, or forgetting its log transform.
- Dropping normalization terms near large counts and assuming a small difference cannot affect derivatives.
- Interpreting an independent-observation forecast as a serially correlated count process.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.