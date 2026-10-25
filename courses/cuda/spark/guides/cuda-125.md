# cuda-125: GPU Spark on an explicitly owned Kubernetes cluster

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-114`, `cuda-119`, `cuda-122`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **draw scheduler layers**, **verify device visibility**, and **write scoped cleanup** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Kubernetes schedules pods onto nodes; an installed and configured device plugin advertises GPU resources to that scheduler. Spark's driver requests executors, and Spark's own resource discovery must agree with what each executor container can access. These are different layers. A pod resource limit alone does not prove the selected image, driver and native libraries can execute the Spark GPU plugin.

This is a manual external lab for a named disposable cluster and namespace. Never use ambient kubeconfig or expose a driver service publicly by convenience. Define service accounts, image provenance, node selection, resource limits, storage and cleanup before creating workloads. Docker Desktop on a Mac is useful for the CPU classroom, but it does not manufacture an NVIDIA GPU for Kubernetes. Observe pod placement and actual device visibility before a bounded query.



## Worked examples

### Worked example 1

A cluster can have three nodes but only one advertising a compatible GPU. A GPU executor must land on the eligible node and see the assigned resource inside its container.

### Worked example 2

A driver pod running successfully while executors remain Pending proves control-plane submission only. Inspect resource requests, events and image/runtime constraints before changing code.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
nodes = [{"name": "cpu-node", "gpu": 0}, {"name": "gpu-node", "gpu": 1}]
eligible = [node["name"] for node in nodes if node["gpu"] >= 1]
assert eligible == ["gpu-node"]
print("CPU scheduling worksheet:", eligible)
```

**Expected observation:** Only the illustrative GPU node is eligible; no cluster operation occurs.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Draw scheduler layers

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **draw scheduler layers** in the examples above.

### Exercise 2: Name ownership boundaries

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **name ownership boundaries** in the examples above.

### Exercise 3: Diagnose Pending executors

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **diagnose Pending executors** in the examples above.

### Exercise 4: Verify device visibility

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **verify device visibility** in the examples above.

### Exercise 5: Design private networking

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design private networking** in the examples above.

### Exercise 6: Write scoped cleanup

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **write scoped cleanup** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Draw scheduler layers".
2. Change one assumption in worked example 2 while preserving the declared contract: name ownership boundaries.
3. Trace the CPU program's variables before adding hardware behavior: diagnose Pending executors.
4. Draw producers, consumers and the exact operation boundary for the task "Verify device visibility".
5. Separate what the small fixture establishes from what the real runtime must show: design private networking.
6. Write a counterexample to an overbroad claim before you write scoped cleanup.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Draw scheduler layers`. For the final claim use `Write scoped cleanup`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-125` using `courses/cuda/spark/guides/cuda-125.md` and `courses/cuda/spark/lessons/cuda-125.md`. Help me reason about GPU Spark on an explicitly owned Kubernetes cluster. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
