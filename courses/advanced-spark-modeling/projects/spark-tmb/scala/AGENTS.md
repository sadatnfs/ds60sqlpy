# Scala prepared-likelihood adapter

This subtree owns only the Scala/JVM adapter, its runnable example and compiler
runner. The parent project's registry, CLI, R/C++ models, Python DataFrame API,
Dockerfile and workshop launcher have a separate integration owner. Coordinate
protocol changes before editing either side.

Use the fixed `spark_tmb.cli` versioned JSON interface. Do not copy the registry,
reimplement native-artifact validation, accept source/compiler flags or silently
batch a complete latent group as independent rows. Keep explicit DataFrame
projection, parameter identity, bounded payloads/summaries, immutable-input
ledger, caller-cache ownership and process cleanup.

Compile with the prepared Spark 4.0.1 / Scala 2.13 / JDK 21 jars. No dependency
downloads happen during run. Qualify native ARM64 locally with at most 3 GiB and
two CPUs in the coordinated slot. Preserve exact Scala/CLI source hashes and
image identity. A tiny numerical oracle is not cluster-performance evidence.
No em dashes.
