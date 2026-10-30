# Preparing a native artifact

These tools prepare the separate experimental package. They do not modify the
classroom, publish images, or make the current classroom release depend on it.
The Python frontend can run on a driver with another operating system. Native
workers run on Linux, with one matched ARM64 or AMD64 build per executor platform.
Do not use cross-architecture emulation as qualification.

Use a Linux environment with Python3.11+, GCC12, OpenSSL development headers,
and the exact Spark4.0.1/Scala2.13 jars plus JDK17 or21. The package Dockerfile
prepares these tools from public Python and Apache Spark images. Its build
context is this package alone, so copying it into a fresh project is supported.
The explicit GCC12 selection
matches Debian12 Spark's libstdc++ ABI. A newer compiler's binary may compile
successfully yet fail to load in an older executor image. Always run the native
worker inside the final executor environment before claiming compatibility.

From the package directory, choose fresh destinations for every build:

```bash
python3 tooling/prepare.py --destination /tmp/tmbad-sdk --allow-download
python3 tooling/build_native.py --sdk /tmp/tmbad-sdk --output /tmp/tmbad-native --compiler g++-12
python3 jvm/build.py --spark-home /opt/spark --output /tmp/spark-tmbad.jar
python3 tooling/assemble.py --sdk /tmp/tmbad-sdk --native-build /tmp/tmbad-native \
  --jar /tmp/spark-tmbad.jar --output /opt/spark-tmbad
python3 -m pip install ./python
```

Preparation downloads pinned sources only when `--allow-download` is given.
For offline builds, put the four exact files named in `tooling/prepare.py` in a
local directory and use `--archives /path/to/files` instead. No runtime action
downloads, compiles, or executes a model supplied through a DataFrame.
Original native model source is trusted build-time input. Review custom C++
before building; process resource controls are not an untrusted-code sandbox.

The SDK retains complete source archives and license notices. The build verifies
all extracted dependency files against reconstruction from pinned archives,
records native source and build-script hashes, compiler identity and flags, and
checks that sources did not change during compilation. Its `build_id` and final
binary hash bind model descriptors to those bytes. Assembly checks the native
and JVM receipts and emits `artifact.json`. Relocation may update absolute paths
but cannot change file hashes or scientific model identity.

For Spark, place the complete prepared installation on the driver and load its
exact JAR at session creation with `--jars /opt/spark-tmbad/spark-tmbad.jar`.
The JVM verifies and distributes an immutable native-worker snapshot through
SparkFiles. Executors need matching native libraries, architecture and executable
temporary storage. The Python API does not silently add a JAR to a running
session. Mixed architectures require separate qualified builds and are not
admitted by a single-platform artifact manifest.

Compilation and the native C++ numerical checks are only the first tier. Run
`python/examples/validate_native_oracles.py` against the installed manifest,
then the JVM and actual Spark integration checks. Source and ABI checks cannot
substitute for fit, conditional prediction, forecasting, task failure and
retained-model round-trip observations.

The current package is under development. Follow its evidence ledger for the
operations that have actually passed. Neither a build receipt nor a test count
is a performance or multi-node qualification.
