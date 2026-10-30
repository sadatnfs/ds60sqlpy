# A normalized Gaussian likelihood

Use this model for independent measurements sharing one population mean and standard deviation. It
is the smallest example of fitting one parameter vector across Spark partitions, while retaining the
full normalizing constant.

## Likelihood and parameterization

\[
\sigma=e^s,\qquad L(\mu,s)=\sum_i\left[s+\tfrac12\log(2\pi)+\tfrac12(y_i-\mu)^2e^{-2s}\right].
\]

The optimizer works with log_sigma, so the fitted standard deviation stays positive. For unweighted
data, the MLE mean is the sample mean and the MLE variance uses denominator n. A row weight
multiplies the entire row likelihood term once.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `y`. Row identity is
`row_id`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `mu` | 1.5 | 1 |
| `log_sigma` | -0.3566749 | 0 |

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

recipe = json.loads(Path("python/examples/gallery/fixtures.json").read_text())["cases"]["normal"]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec("normal", {"y": "y"}, id_columns=["row_id"], group_columns=[], order_columns=[])
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [1.0, 0.0]},
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
requested = frame(spark, [{"row_id": 1000}, {"row_id": 1001}], ["row_id"], ordered=False)
predicted = fitted.predict(
    requested, options={"target": "response", "columns": {}, "output_prefix": "prediction_"}
)
predicted.orderBy("row_id").show()
```

The requested rows contain no future `y`. A history-dependent target receives its historical
response in a separate DataFrame. Native field names and Spark column names are mapped explicitly
instead of inferred from their spelling.

## Forecast the declared target

```python
future = frame(spark, [{"row_id": 1000}, {"row_id": 1001}], ["row_id"], ordered=False)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "response",
        "history_columns": {"y": "y"},
        "future_columns": {},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

The returned sd is the observation standard deviation. It is not the standard error of the estimated
mean. The forecast response target describes new independent measurements from the same fitted
population and uses no history.

## A fixed-parameter calculation

At fixed parameters mu=2 and sigma=0.5, every requested future row has mean 2 and sd 0.5, even when
that row contains only its ID. These are analytical reference values, not estimates from the random
gallery sample.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/normal.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/normal

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json normal
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
| `mu` | 1.5201907 | 1.5201907 |
| `log_sigma` | -0.4030345 | sigma = 0.66828904 |

The fit converged with projected gradient norm 6.4621357e-07; raw gradient norm 6.4621357e-07. It
used 7 iterations and 24 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 130.03572. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `mean` | `sd` |
| --- | --- | --- |
| 1000 | 1.5201907 | 0.66828904 |
| 1001 | 1.5201907 | 0.66828904 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: observation only; parameter uncertainty excluded.

### Observed forecast: `response`

| `row_id` | `mean` | `sd` |
| --- | --- | --- |
| 1000 | 1.5201907 | 0.66828904 |
| 1001 | 1.5201907 | 0.66828904 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: observation only; parameter uncertainty excluded.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Using the unbiased sample variance with denominator n-1 as the likelihood MLE oracle.
- Passing sigma directly where the parameter order requires log_sigma.
- Adding a dummy future response column instead of using the declared featureless target.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.