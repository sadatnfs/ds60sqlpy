# Optional owned GPU Spark lab

The ordinary classroom supports reading and CPU semantic practice on every
supported host. This external lab is optional. It requires a separately owned
NVIDIA Linux execution environment with a compatible driver and a prepared
Spark/plugin installation. Nothing here runs automatically from a lesson pad.

## Prepare a release-specific compatibility record

Choose one plugin release from its official download/support page. Record the
following before installing or launching anything:

| Layer | Record and check |
| --- | --- |
| Spark | Exact upstream version or vendor distribution/patch line |
| Scala | Binary line used by Spark and matching plugin artifact suffix |
| Java | JDK compatible with the chosen Spark distribution |
| Python | Version supported by that Spark/PySpark release |
| Plugin | Release version, exact artifact/classifier, checksum and source |
| CUDA native libraries | The plugin's supported CUDA variant and dependencies |
| Host | Linux distribution, glibc and CPU architecture |
| Driver and GPU | Host driver, supported GPU model/architecture and visible device |
| Resource mode | Local bounded experiment or explicitly owned cluster, never ambient |

A Scala suffix, CUDA classifier and driver version solve different compatibility
questions. Do not choose a `SNAPSHOT` artifact simply because it appears in a
configuration example. Resolve exact release files from
[the plugin download page](https://nvidia.github.io/cudf-spark/docs/download.html)
and [Apache Spark documentation](https://spark.apache.org/documentation.html).
Preserve licenses and signatures/checksums where provided. This repository does
not redistribute a plugin jar or claim an untested universal version matrix.

## First establish the CPU result

In the classroom, run both variants of `cuda-127`. The expected sorted output
is product A revenue 60 cents and product B revenue 60 cents. Review why a
duplicate price key changes join multiplicity. Keep those expected values
independent from any GPU output.

The local external script below uses the same bounded objective and forces a
local Spark master. It does not create a Kubernetes cluster or connect to a
remote Spark service. The script prints a formatted plan and exact results,
but you must still inspect the executed SQL plan and device/operation evidence.
A tiny fixture is useful for semantics and startup, not for a meaningful speedup.

## Launch only after preparing the owned host

From the repository on that prepared NVIDIA host, set the path to the exact
already downloaded and verified jar. The variable intentionally has no default:

```sh
export CUDA_SPARK_PLUGIN_JAR=/absolute/path/to/your/verified-plugin.jar
test -f "${CUDA_SPARK_PLUGIN_JAR:?Set the verified plugin jar path first}"
DS60_GPU_SPARK_CONFIRMED=yes spark-submit \
  --master 'local[2]' \
  --jars "$CUDA_SPARK_PLUGIN_JAR" \
  --conf spark.plugins=com.nvidia.spark.SQLPlugin \
  --conf spark.rapids.sql.enabled=true \
  --conf spark.rapids.sql.explain=NOT_ON_GPU \
  --conf spark.sql.shuffle.partitions=2 \
  courses/cuda/spark/manual/gpu_query.py
```

This is a bounded local example, not a universal production cluster
configuration. Some release/hardware combinations need additional documented
resource or native-library setup. A missing device or incompatible jar is a
failed GPU setup; do not report it as operator fallback. Keep the ordinary CPU
classroom usable while resolving the optional environment.

The script refuses to proceed without the explicit environment acknowledgment,
requires the declared plugin setting, keeps the master local, uses synthetic
fixtures and stops its Spark session in `finally`. It neither installs packages
nor downloads data. It cannot establish the entire host's security or detect
all possible third-party startup behavior, so run it only in your owned prepared
environment with the reviewed jar.

## Observe before optimizing

Capture the executed query after its action, not just the initial logical plan.
Record which operations use GPU implementations, every fallback reason, and
row/columnar/device transitions. Compare the exact result first. Then record
resource assignment, actual device use, completed query time, memory and spill.
The plugin's supported-operator matrix is expression/type-specific and can
change with release; always match it to your chosen environment.

For a performance study, create a separate bounded representative fixture and
hold query semantics, input identity, output materialization, cache state,
warmup and timing boundaries constant. Keep raw observations and report
variation. Do not claim a speedup from an unexecuted qualification estimate or
from comparing a warm GPU run with a cold CPU run.

For cluster operation, follow `cuda-125` and prepare an exact owned target,
namespace, service account, images, GPU discovery and scoped cleanup. The local
command above is deliberately not an implicit cluster launcher. Never expose a
Spark driver or UI publicly just to make the lesson reachable.

Primary references: [supported operators](https://nvidia.github.io/cudf-spark/docs/supported_ops.html),
[configuration](https://nvidia.github.io/cudf-spark/docs/configs.html),
[tuning](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html),
[Spark SQL tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html),
[Spark Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html).
