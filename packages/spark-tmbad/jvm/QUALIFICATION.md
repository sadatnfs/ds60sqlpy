# JVM qualification record

The source-bound ARM64 baseline passed its prepared native and Spark acceptance.
The machine-readable [receipt](qualification.json) records the exact source,
compiler-script, JAR, native binary and retained evidence hashes. Rebuild and
requalify after changing those inputs; do not silently carry this receipt forward.

| Check | Observed result |
| --- | --- |
| Offline JVM compilation | Spark 4.0.1, Scala 2.13, JDK 17; separate production and test JARs |
| Strict parser and original solver | Duplicate/unsafe JSON refusal, bounded BFGS, candidate versus infrastructure handling, memory accounting, launch retry controls |
| [Spark contracts](src/test/scala/io/ds60/spark/tmbad/SparkChecks.scala) | 14 checks, including weighted objectives, complete-unit mass, cache ownership, saved independent models and Unicode name resolution |
| [Numerical trial recovery](src/test/scala/io/ds60/spark/tmbad/CandidateChecks.scala) | Exact and Laplace Gaussian fits agree; mixed partial sums are discarded; valid smaller steps recover; invalid initial points remain fatal |
| [Native resource lifecycle](src/test/scala/io/ds60/spark/tmbad/ResourceChecks.scala) | 32 sequential lexical sessions without listener growth, shared deadline expiry, child reaping, cache cap/no eviction, failed-deletion retry and missed-end cleanup |
| [Fault protocol controls](src/test/scala/io/ds60/spark/tmbad/LifecycleChecks.scala) | 11 controls covering exit status, identity/hash mismatch, trailing output, resource error, timeout and cancellation |
| [Direct Scala gallery](src/main/scala/io/ds60/spark/tmbad/examples/ModelGallery.scala) | 14 fits and 39 declared prediction/forecast operations; convergence, finite outputs and exact target identity coverage |
| [Separate executor JVMs](src/test/scala/io/ds60/spark/tmbad/ExecutorChecks.scala) | Two distinct JVMs on one host completed native fitting, prediction and forecasting |

The two-executor run used a 3 GiB container, 2 CPUs and a 1024-PID limit. The
observed peak was 546 processes/threads, with zero PID-limit events, no OOM and
no fatal diagnostics. A lower 512-PID attempt returned correct numbers but lost
executors following thread-allocation failures; it was not accepted as a clean
run. The [README](README.md) preserves the exact setup requirements.

The lifetime fault controls use explicitly test-only Python protocol emitters.
Actual fitting and forecasting use the prepared C++ worker. The independent
one-group Gaussian variance-component example verifies numerical recovery at a
boundary; it does not establish identifiable interior variance estimation from a
single group. A convergence result reports first-order stationarity, not a global
optimum or model suitability.

This record covers native ARM64 and same-host execution using an existing prepared
Spark image with read-only assembled artifacts. It does not claim AMD64 runtime,
a sealed build of the complete package Dockerfile, separate worker containers,
a multi-machine cluster or production scale. The separate-container integration
harness is an additional qualification stage. Python and native independent
formula checks remain separate from the Scala gallery's finite/cardinality checks.
