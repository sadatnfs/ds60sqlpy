# cuda-126: Operational diagnosis, metrics and recovery

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-120`, `cuda-122`, `cuda-125`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify failure layers**, **analyze retry side effects**, and **preserve an incident packet** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

GPU Spark failures can originate in query semantics, JVM integration, native library loading, device memory, host memory, spill disk, network or scheduler state. Preserve the first relevant error and correlate it with executor, task and SQL execution identity. A later generic task retry may hide the original native failure. Repeatedly increasing memory without a budget can move the problem between tiers.

Recovery should preserve input snapshots, output commit semantics and event logs. Retrying a task is safe only under the application's side-effect contract; external writes inside a UDF can be duplicated. A poisoned device context may require a fresh owned process, while device-wide reset is an administrator operation that can affect unrelated jobs. The classroom must never reset a shared GPU automatically.



## Worked examples

### Worked example 1

An executor fails with device OOM while JVM heap is below its limit. Increasing heap does not address the measured GPU live-set problem.

### Worked example 2

A task writes an external message then fails before Spark commits its output. Retrying may send the message twice unless an idempotency or transactional design handles it.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
events = [("task1", "write", "key-7"), ("task1-retry", "write", "key-7")]
raw = len(events)
idempotent = len({key for _, _, key in events})
assert raw == 2 and idempotent == 1
print("CPU retry model:", raw, "attempts;", idempotent, "logical keys")
```

**Expected observation:** Two attempts can target one logical output key.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Classify failure layers

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **classify failure layers** in the examples above.

### Exercise 2: Correlate job identities

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **correlate job identities** in the examples above.

### Exercise 3: Budget before changing settings

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **budget before changing settings** in the examples above.

### Exercise 4: Analyze retry side effects

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **analyze retry side effects** in the examples above.

### Exercise 5: Define process cleanup

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **define process cleanup** in the examples above.

### Exercise 6: Preserve an incident packet

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **preserve an incident packet** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Classify failure layers".
2. Change one assumption in worked example 2 while preserving the declared contract: correlate job identities.
3. Trace the CPU program's variables before adding hardware behavior: budget before changing settings.
4. Draw producers, consumers and the exact operation boundary for the task "Analyze retry side effects".
5. Separate what the small fixture establishes from what the real runtime must show: define process cleanup.
6. Write a counterexample to an overbroad claim before you preserve an incident packet.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Classify failure layers`. For the final claim use `Preserve an incident packet`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-126` using `courses/cuda/spark/guides/cuda-126.md` and `courses/cuda/spark/lessons/cuda-126.md`. Help me reason about Operational diagnosis, metrics and recovery. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
