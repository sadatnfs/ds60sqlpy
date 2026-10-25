# cuda-122: Shuffle, transport and network bottlenecks

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-118`, `cuda-119`, `cuda-120`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute transfer lower bound**, **list transport qualification**, and **design a bounded shuffle comparison** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A shuffle redistributes records between tasks, often crossing executor and host boundaries. Its cost includes serialization or columnar handling, buffering, transport, disk and downstream processing. A GPU can accelerate supported local operators while the job remains limited by network or storage. Specialized shuffle managers and transports have their own compatibility, startup configuration and failure behavior.

Do not infer RDMA, peer-to-peer or GPUDirect capability from an installed library. Those paths require actual hardware, topology and runtime support. Establish an ordinary supported shuffle baseline, then qualify an optional accelerated path. Record bytes, partitions, transfer time, retries and spill. Preserve query semantics and avoid exposing network services or changing cluster-wide settings from an ordinary lesson pad.



## Worked examples

### Worked example 1

Moving 10 GiB over an effective 1 GiB/s path has a 10-second payload lower bound before other costs. Halving a 100 ms local kernel cannot remove that bottleneck.

### Worked example 2

Reducing shuffle volume through an equivalent pre-aggregation may help more than changing transport. The rewrite must preserve aggregate semantics, especially for nonassociative or stateful operations.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
gib = 1024**3
payload = 10 * gib
bandwidth = gib
seconds = payload / bandwidth
assert seconds == 10
kernel_saving = 0.05
assert kernel_saving / seconds < 0.01
print("CPU shuffle bound:", seconds, "seconds before additional overhead")
```

**Expected observation:** Ten-second payload lower bound;50 ms kernel saving is below 1 percent of it.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute transfer lower bound

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute transfer lower bound** in the examples above.

### Exercise 2: Identify local versus network time

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **identify local versus network time** in the examples above.

### Exercise 3: Explain pre-aggregation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **explain pre-aggregation** in the examples above.

### Exercise 4: List transport qualification

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **list transport qualification** in the examples above.

### Exercise 5: Separate startup settings

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **separate startup settings** in the examples above.

### Exercise 6: Design a bounded shuffle comparison

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design a bounded shuffle comparison** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute transfer lower bound".
2. Change one assumption in worked example 2 while preserving the declared contract: identify local versus network time.
3. Trace the CPU program's variables before adding hardware behavior: explain pre-aggregation.
4. Draw producers, consumers and the exact operation boundary for the task "List transport qualification".
5. Separate what the small fixture establishes from what the real runtime must show: separate startup settings.
6. Write a counterexample to an overbroad claim before you design a bounded shuffle comparison.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute transfer lower bound`. For the final claim use `Design a bounded shuffle comparison`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-122` using `courses/cuda/spark/guides/cuda-122.md` and `courses/cuda/spark/lessons/cuda-122.md`. Help me reason about Shuffle, transport and network bottlenecks. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
