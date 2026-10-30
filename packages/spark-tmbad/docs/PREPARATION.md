# Prepare an explicit runtime

Preparation creates source-bound native and JVM artifacts. It does not start a
classroom, modify learner volumes, publish an image or qualify a remote cluster.
Run these commands from the package directory in a deliberately prepared Linux
environment on native ARM64 or AMD64. Do not use cross-architecture emulation as
evidence for the other platform.

The build environment needs Python 3.11 or newer, a compatible C++17 toolchain,
OpenSSL development headers/libraries, the system GPL-2 license text, and the
pinned dependency archives. The JVM build needs Spark 4.0.1's Scala 2.13 JAR set
and JDK 17 or 21. The Python driver frontend supports the versions declared in
`python/pyproject.toml`. The native model operation does not require Python or R on executors; an
upstream DataFrame with its own Python UDF or PythonRDD retains that separate
Python dependency.

Match the compiler's libstdc++/CXXABI requirements and glibc/shared-library
requirements to the target executor image. The default compiler selection is
`g++-12`. Selecting a newer compiler is a deliberate deployment change and
requires loading/running the resulting worker in the executor image. A successful
build in the compiler image alone is insufficient.

## Prepare pinned source and notices

Supply these already obtained files in a dedicated archive directory:

- `TMB_1.9.25.tar.gz`
- `RcppEigen_0.3.4.0.2.tar.gz`
- `json.hpp` from nlohmann/json 3.12.0
- `nlohmann-LICENSE.MIT` from that same version

The maintained [preparation script](../tooling/prepare.py) checks their exact
SHA-256 values and retains the complete archives and required notices. It
extracts only bounded, validated regular files. Use a fresh SDK directory:

```sh
python tooling/prepare.py \
  --archives /prepared/archives \
  --destination /work/tmbad-sdk
```

Missing archives fail without a download. `--allow-download` is a separate,
explicit preparation option for an environment whose owner permits the pinned
HTTPS downloads. Opening a model or running a Spark task never downloads them.

## Build native and JVM artifacts

```sh
python tooling/build_native.py \
  --sdk /work/tmbad-sdk \
  --compiler g++-12 \
  --output /work/tmbad-native

python jvm/build.py \
  --spark-home /opt/spark \
  --output /work/spark-tmbad.jar
```

The native build reconstructs SDK content from pinned archives and checks the
source inventory before and after compilation. It records compiler identity,
flags, source/dependency hashes and the resulting binary hash. Its native math
checks and `--describe` must succeed. The JAR build uses the supplied Spark JARs
without resolving new dependencies and writes a companion compilation receipt.
Both commands refuse an existing destination.

For internal JVM acceptance that requires the package's test classes, deliberately
add `--include-tests` to the JAR build. That produces a different JAR digest.
Never replace a manifest's JAR hash with a test JAR hash by hand.

## Assemble a deployment directory

```sh
python tooling/assemble.py \
  --native-build /work/tmbad-native \
  --sdk /work/tmbad-sdk \
  --jar /work/spark-tmbad.jar \
  --output /work/tmbad-install \
  --runtime-root /opt/spark-tmbad
```

The output contains `artifact.json`, `tmbad-worker`, `spark-tmbad.jar`, build
receipts, corresponding source archives and notices. `--runtime-root` specifies
where those files will be deployed. Omit it when the assembly directory itself
is the final runtime location. Place the complete installation at that path in
the driver environment. Spark distributes the JAR supplied with `--jars`; the
adapter verifies and distributes its immutable native worker snapshot through
SparkFiles. Executors must provide matching Linux architecture and native ABI,
plus private writable/executable temporary storage. Preserve executable
permission on the prepared worker and read permission on the JAR and retained
source/notices.

Absolute paths may be relocated deliberately while retaining matching bytes
and content identities. Keep the matching prepared installation or image with
saved model JSON. Binary, architecture and JAR identities are part of the saved
model binding, so a rebuilt artifact or an ARM64-to-AMD64 change is not an
automatic migration. Mixed-architecture executors are not supported by one
manifest. A driver OS may differ only when the actual native executors match
the declared Linux artifact. The manifest is not a dependency-download URL or an environment installer.
The adapter checks the actual loaded JAR,
native binary and worker-reported model/build identity during execution.

## Install and verify the Python frontend

Build a wheel in the prepared packaging environment, then install it into the
driver environment. For example, with the standard `build` frontend already
installed:

```sh
python -m build --wheel --no-isolation python --outdir /work/python-dist
python -m pip install --no-deps /work/python-dist/ds60_spark_tmbad-0.1.0-py3-none-any.whl
```

The wheel has no numerical dependencies and contains no native binary or JAR.
Prepare PySpark separately, or explicitly install the `spark` extra during
environment preparation. Keep the same prepared Spark/Scala versions on both
frontends. A source-path import is not installed-wheel acceptance.

Within the final Linux executor-compatible image, run the native-only oracles:

```sh
python python/examples/validate_native_oracles.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --case all
```

This suite requires the registered Gaussian, Poisson random-intercept, AR(1)
combined AR(1)/random-intercept and Poisson random-slope models. `--case core`
selects the first three families explicitly; `--case combined` and `--case slope`
select the remaining complete-unit families. Results list
the exact checks executed. Missing models are errors, not successful skips.

The independent row-family gate replays verified exported constants without
installing SciPy in the runtime:

```sh
python python/examples/validate_row_references.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --references python/examples/row_reference_fixtures.json
```

The reference file records the SciPy version and generator source hash. Refreshing
it is an explicit authoring operation using an already prepared scientific
environment with SciPy:

```sh
python python/examples/build_row_references.py --output /work/new-row-references.json
```

The generator fails if SciPy is unavailable. It neither installs a dependency nor
silently skips a check. Review changed constants before updating the checked-in
reference file. The production frontend has no SciPy dependency.

Then run actual installed-wheel Spark acceptance:

```sh
spark-submit --master 'local[2]' \
  --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/validate_installed.py \
  --manifest /opt/spark-tmbad/artifact.json
```

The examples use synthetic fixtures, check actual native outputs against
independent formulas, and report their observed platform and build identity.
The Spark example verifies a non-editable installed frontend. A local two-thread
run does not establish multi-node scheduling, fault recovery at production scale,
performance, or acceptance of another architecture.

Retain preparation receipts, numerical reports and Spark reports separately.
Original package source is MIT-licensed; TMBad and other prepared dependencies
retain their own terms. Preserve their source archives and notices when
distributing the prepared installation.
