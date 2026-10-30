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
Explore the [original 14-model gallery](docs/EXAMPLES.md) and the
[nine additional likelihoods](docs/EXTENDED-MODELS.md). The prepared registry now
contains 23 models. Read the
[Python guide](docs/PYTHON.md) for complete DataFrame examples,
[model contracts](docs/MODELS.md) for statistical meaning and input boundaries,
[custom-model authoring](docs/CUSTOM-MODELS.md) for prepared C++ extensions,
and [protocol](docs/PROTOCOL.md) for the common native and JVM contract.
Version 0.2 adds [named Gaussian priors, exact L1 penalties, fixed parameters and
declared parameter sets](python/docs/EXTENDED-TARGETS.md). Its public evaluation
API reports the likelihood and penalty components without inventing fit status.
The optional [R/TMB/glmmTMB reference project](reference/README.md) has its own
preparation, dependencies and qualification records.

### Build a standalone image

Copy this entire directory into a fresh project, enter that directory, and build:

```sh
docker build --tag spark-tmbad:0.2.0 .
docker run --rm --network none --entrypoint /opt/spark-tmbad/tmbad-worker \
  spark-tmbad:0.2.0 --describe
docker run --rm --network none --hostname localhost \
  --env SPARK_LOCAL_IP=127.0.0.1 spark-tmbad:0.2.0 \
  --master 'local[2]' /src/python/examples/validate_installed.py \
  --manifest /opt/spark-tmbad/artifact.json
```

The default Dockerfile uses public Python 3.12.12 and Apache Spark 4.0.1 bases,
installs Debian Bookworm's GCC12/OpenSSL and JDK17 dependencies, verifies pinned
native source archives, builds a wheel and JAR, and installs them in the final
runtime. It does not need another DS60 checkout, classroom image or R runtime.
Image preparation needs network access; model execution does not download or
compile dependencies. The example above is a local Spark check, not evidence of
multiple worker containers or another architecture.

`CPP_IMAGE`, `PYTHON_IMAGE` and `SPARK_IMAGE` are explicit build overrides for
prepared environments. `PREPARED_OS_PACKAGES=1` skips apt preparation only when
the chosen images already contain every declared compiler/runtime dependency.
That opt-out does not skip source hashes, compilation, native checks, wheel
installation or final-runtime artifact validation. Record the actual base image
identities and native architecture with any qualification result. Do not treat
a build using prepared overrides as qualification of different default bases.
It is not an offline-build switch: the default preparation stages still fetch
hash-pinned native sources and Python build wheels. For a fully offline build,
use the archive-based commands in the preparation guide and already prepared
packaging tools.

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
