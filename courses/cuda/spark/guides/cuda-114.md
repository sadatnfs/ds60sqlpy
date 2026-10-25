# cuda-114: Compatibility is a tested matrix, not a jar name

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-113`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **list matrix axes**, **record artifact provenance**, and **define compatibility acceptance** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A working GPU Spark installation matches Spark patch line, Scala binary version, Java runtime, plugin release, CUDA native-library variant, host CPU architecture, Linux userspace, NVIDIA driver and GPU architecture. Spark distributions can carry vendor patches, so a nominal Spark version alone may not establish binary compatibility. The published support matrix and release notes must be checked for the exact selected release.

Record artifacts by version and checksum and keep a known CPU baseline. Do not copy a development SNAPSHOT from a documentation example into a beginner setup. The Scala suffix selects a binary ecosystem; the CUDA classifier selects native-library packaging and is not a substitute for a compatible host driver. A local ARM Mac image architecture and an NVIDIA Linux host architecture are separate concerns. This lesson's compatibility worksheet deliberately does not invent a universally supported version combination.



## Worked examples

### Worked example 1

A jar built for Scala 2.12 should not be assumed compatible with a Scala 2.13 Spark distribution. A NoSuchMethodError can indicate binary integration trouble before useful GPU work starts.

### Worked example 2

A package can load on one Linux host but fail to initialize native libraries on another architecture. Version ledger completeness and actual smoke execution are both required.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def compatible(spark_scala, jar_scala, host_arch, jar_arch):
    return spark_scala == jar_scala and host_arch == jar_arch


assert compatible("2.13", "2.13", "x86_64", "x86_64")
assert not compatible("2.13", "2.12", "x86_64", "x86_64")
print("CPU compatibility worksheet: mismatched Scala binary line rejected")
```

**Expected observation:** Illustrative Scala/host-architecture predicate rejects mismatch; not a full compatibility probe.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: List matrix axes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **list matrix axes** in the examples above.

### Exercise 2: Identify a Scala mismatch

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **identify a Scala mismatch** in the examples above.

### Exercise 3: Distinguish toolkit and driver

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **distinguish toolkit and driver** in the examples above.

### Exercise 4: Record artifact provenance

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **record artifact provenance** in the examples above.

### Exercise 5: Design a CPU rollback

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a CPU rollback** in the examples above.

### Exercise 6: Define compatibility acceptance

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **define compatibility acceptance** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "List matrix axes".
2. Change one assumption in worked example 2 while preserving the declared contract: identify a Scala mismatch.
3. Trace the CPU program's variables before adding hardware behavior: distinguish toolkit and driver.
4. Draw producers, consumers and the exact operation boundary for the task "Record artifact provenance".
5. Separate what the small fixture establishes from what the real runtime must show: design a CPU rollback.
6. Write a counterexample to an overbroad claim before you define compatibility acceptance.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `List matrix axes`. For the final claim use `Define compatibility acceptance`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-114` using `courses/cuda/spark/guides/cuda-114.md` and `courses/cuda/spark/lessons/cuda-114.md`. Help me reason about Compatibility is a tested matrix, not a jar name. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
