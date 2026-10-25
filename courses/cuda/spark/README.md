# GPU Spark, RAPIDS and the cuDF plugin

This specialization contains `cuda-113` through `cuda-128`. Start after shared
GPU foundations and the existing Spark DataFrame/SQL lesson `spark-013`.
You do not need to finish the entire CUDA Python or C++ route first.

RAPIDS is a GPU data-science ecosystem. NVIDIA's current documentation calls its
Spark SQL/DataFrame integration the **cuDF plugin for Apache Spark**, formerly
**RAPIDS Accelerator for Apache Spark**. Artifact and configuration names can
retain `rapids`. It uses GPU algorithms for supported physical operators. It
does not automatically translate arbitrary Python or Scala UDFs into GPU kernels.
See the [official release guide](https://nvidia.github.io/cudf-spark/docs/download.html).

Every chapter includes detailed reading, two worked examples, six targeted
exercises, hints, separate explained answers and a standard-library CPU model.
Four chapters additionally offer equivalent executable Scala and PySpark labs
through the existing ordinary CPU Spark workers:

| Chapter | Executable objective |
| --- | --- |
| `cuda-113` | Grouped totals and declarative plan |
| `cuda-117` | Row count, non-null count, sum and all-null semantics |
| `cuda-121` | Duplicate-key join multiplicity |
| `cuda-127` | Exact-cent ETL join and grouped revenue capstone |

The complete route covers compatibility, Catalyst/AQE plans, supported
operators and fallback, null/decimal/time semantics, Arrow/columnar boundaries,
GPU resources and executor ownership, concurrency, memory pools, spills, joins,
skew, broadcast decisions, shuffle/networking, fair benchmarks, UDF/ML
boundaries, owned Kubernetes operation, recovery and architecture decisions.

**CPU-only is a complete learning route.** Run ordinary Spark with the GPU
plugin absent or disabled. A working GPU plugin can fall back for unsupported
operators; this does not mean the plugin can necessarily initialize without a
compatible GPU. The course distinguishes these conditions explicitly.

GPU Spark execution is a separately prepared external workflow. The browser
workers do not receive cluster credentials, an engine socket or arbitrary
endpoints. Read [the external lab contract](external-gpu-lab.md) before choosing
an NVIDIA Linux host. A CPU pass or a printed planned diagram does not establish
GPU execution, throughput, multi-node operation or Kubernetes acceptance.
