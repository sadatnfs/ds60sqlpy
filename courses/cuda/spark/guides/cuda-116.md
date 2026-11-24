# cuda-116: Supported operations, fallback and semantic boundaries

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-115`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify fallback versus unavailable device**, **rewrite an opaque function declaratively**, and **design a mixed-plan report** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Support depends on operator, expression, dtype and configuration. A supported aggregate on one type may fall back on another expression or precision requirement. CPU fallback means a compatible plugin environment selects CPU execution for an unsupported part of a query. It does not mean a missing NVIDIA GPU can always initialize the enabled plugin and run normally.

For CPU-only study, use ordinary Spark with the GPU plugin disabled or absent. For GPU study, inspect supported-operator documentation for the chosen release and capture reasons such as NOT_ON_GPU diagnostics. A mixed plan may pay row/columnar conversions and device transfers repeatedly. Do not force an incompatible operator merely to increase GPU coverage; preserve semantics and measure the whole query.

## Four states that should never share one success label

**CPU baseline** means ordinary Spark runs with the GPU plugin absent or disabled. It should work on a supported CPU-only host and is the rollback and semantic comparison. **Plugin initialization failure** means the requested accelerated environment could not start correctly, perhaps because device exposure or native libraries are unavailable. That is a failure, not a successful fallback.

**Operator fallback** means a functioning plugin environment keeps an unsupported operator or expression on CPU while other supported work may use the GPU. **GPU execution** means the intended compatible operator actually ran on the device and produced an accepted result. These states require different troubleshooting and should be recorded separately in the learning notebook.

Suppose a query filters, invokes a Python UDF, then aggregates. The UDF may create a boundary even when the surrounding operators are supported. Replacing it with built-in expressions can expose the algebra to Catalyst, but only if the replacement matches null behavior, input types, overflow, timestamps and any error semantics. A mathematically similar expression can still differ under SQL's type rules.

Use the release's supported-operator list and `spark.rapids.sql.explain=NOT_ON_GPU` diagnostics as aids, not universal truths detached from versions. The published table may be generated against a particular Spark release; inspect the matching plugin and distribution notes. An explicit CPU/GPU parity test over adversarial tiny fixtures is the final semantic guard before measuring a larger workload.


### Key terms

- **CPU fallback:** Running an unsupported part of a query on the CPU inside a working GPU plugin environment.
- **Unsupported expression:** An expression or dtype the plugin release cannot execute on the GPU under the current configuration.
- **Explain diagnostics:** Plugin output that reports which operators will not run on the GPU and why.
- **CPU-only baseline:** An ordinary Spark run with the GPU plugin disabled or absent, used as the semantic reference.

## Worked examples

### Worked example 1

GPU aggregate -> CPU UDF -> GPU projection crosses the boundary twice around the UDF. Replacing the UDF with an equivalent supported expression might reduce transitions after parity tests.

### Worked example 2

A machine with no GPU should use the CPU baseline configuration. This differs from a GPU machine where one unsupported expression falls back inside an otherwise valid plugin job.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
states = [
    {"gpu_visible": False, "plugin_enabled": False},
    {"gpu_visible": True, "plugin_enabled": True, "cpu_operator": True},
]
assert states[0]["plugin_enabled"] is False
assert states[1]["cpu_operator"] is True
print("CPU configuration worksheet: CPU baseline and GPU mixed plan are distinct")
```

**Expected observation:** CPU-only baseline and per-operator fallback are modeled separately.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Classify fallback versus unavailable device

**Trap to avoid:** Calling a GPU-less run a fallback suggests the plugin was active and made per-operator choices, when actually it never started.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Find an unsupported expression

**Trap to avoid:** Assuming support from the operator name alone misses expression-level and type-level restrictions, which are the usual cause of fallback.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Count boundary costs

**Trap to avoid:** Assuming only the UDF runs slower and the rest stays fast ignores that the transitions stall the GPU sections on both sides.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Rewrite an opaque function declaratively

**Trap to avoid:** Rewriting with a built-in that differs on edge cases, such as whitespace or null handling, changes results while appearing equivalent.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Preserve edge semantics

**Trap to avoid:** Testing only typical values passes implementations that disagree exactly where production data is unusual.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Design a mixed-plan report

**Trap to avoid:** Reporting only the percentage of GPU operators hides which fallback is expensive. One fallback on a small lookup table may be harmless, while one on the widest projection can dominate the job.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Classify fallback versus unavailable device".
2. Change one assumption in worked example 2 while preserving the declared contract: find an unsupported expression.
3. Trace the CPU program's variables before adding hardware behavior: count boundary costs.
4. Draw producers, consumers and the exact operation boundary for the task "Rewrite an opaque function declaratively".
5. Separate what the small fixture establishes from what the real runtime must show: preserve edge semantics.
6. Write a counterexample to an overbroad claim before you design a mixed-plan report.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Classify fallback versus unavailable device`. For the final claim use `Design a mixed-plan report`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-116: Supported operations, fallback and semantic boundaries.
Read courses/cuda/spark/guides/cuda-116.md and courses/cuda/spark/lessons/cuda-116.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
