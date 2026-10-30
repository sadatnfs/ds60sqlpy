# Spark/TMBad

Spark/TMBad is an independent package for fitting trusted custom C++ likelihoods
and making declared predictions and forecasts from Spark DataFrames. Scala and
Python frontends share a JVM adapter. Spark executors run a prepared native
TMBad process, with no R runtime and no Python numerical workers.

The package has four explicit layers:

| Layer | Responsibility |
| --- | --- |
| Native model registry | Prepared C++ likelihoods, AD derivatives, declared prediction and forecast hooks |
| Native process protocol | Bounded requests, identity checks, process isolation and complete success/failure handling |
| JVM adapter | DataFrame validation, complete-group assembly, distributed evaluation, optimization and model joins |
| Python frontend | Lightweight Py4J calls, explicit input mappings and source-bound JSON persistence |

Use `fit_shared` for one parameter vector across all independent rows or groups.
Use `fit_groups` for separate group models. Predictions require a named target
declared by the prepared model. Conditional predictions take an explicit history
DataFrame. Forecasts take separate history and future DataFrames. A response-free
prediction never requires a dummy observed response column.

The original package code is MIT-licensed. TMBad is a separately prepared
dependency from TMB 1.9.25 with its GPL-2 license and source notices retained.
A process boundary does not relicense that dependency. Review the retained
dependency source and notices when distributing a prepared native artifact.

## Prepare and use

Prepare the native worker and matching JVM JAR first. Their manifest binds the
native source, compiled binary, model declarations, architecture and optional
JVM artifact. Keep the manifest-selected binary and JAR available on the driver
and start Spark with that JAR. The adapter verifies and distributes an immutable
worker snapshot through SparkFiles. Executors need the declared Linux
architecture, compatible shared libraries and private executable temporary
storage. Runtime operations do not download dependencies or compile models.

The Python wheel is independently installable from `python/`:

```sh
python -m pip install ./python
```

Follow [runtime preparation](docs/PREPARATION.md) for the native/JAR manifest setup.
Explore the [14-model gallery](docs/EXAMPLES.md), and read the
[Python guide](docs/PYTHON.md) for complete DataFrame examples,
[model contracts](docs/MODELS.md) for statistical meaning and input boundaries,
[custom-model authoring](docs/CUSTOM-MODELS.md) for prepared C++ extensions,
and [protocol](docs/PROTOCOL.md) for the common native and JVM contract.

Match the native compiler ABI and shared libraries to the executor runtime as
well as its Linux architecture. Successful compilation in a different image
does not prove that the worker can start in the Spark executor image.

This package remains separate from the classroom application and the existing
Spark/PyTorch package. Its native platform target is Linux on native ARM64 or
AMD64. Actual qualified architectures and runtime checks must be read from
current validation records. A local Spark run is not multi-node acceptance or
a performance benchmark.

## Limits

Only compiled registry models are callable. There is no runtime C++ compiler,
arbitrary Python model import, unchanged TMB/R-template compatibility, JNI path,
GPU backend or Spark Connect adapter. Complete dependent units cannot be split
to fit a batch limit, and cross-group covariance cannot be dropped to manufacture
an additive objective. A forecast or uncertainty target exists only when the
native model explicitly implements it.

The protocol and descriptors define numerical limits and supported derivatives.
Fitting diagnostics distinguish convergence, active bounds, stalling and failure.
Inspect those diagnostics and the declared conditioning/uncertainty scope before
using a scientific result.
