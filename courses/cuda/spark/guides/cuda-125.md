# cuda-125: GPU Spark on an explicitly owned Kubernetes cluster

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-114`, `cuda-119`, `cuda-122`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **draw scheduler layers**, **verify device visibility**, and **write scoped cleanup** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Kubernetes schedules pods onto nodes; an installed and configured device plugin advertises GPU resources to that scheduler. Spark's driver requests executors, and Spark's own resource discovery must agree with what each executor container can access. These are different layers. A pod resource limit alone does not prove the selected image, driver and native libraries can execute the Spark GPU plugin.

This is a manual external lab for a named disposable cluster and namespace. Never use ambient kubeconfig or expose a driver service publicly by convenience. Define service accounts, image provenance, node selection, resource limits, storage and cleanup before creating workloads. Docker Desktop on a Mac is useful for the CPU classroom, but it does not manufacture an NVIDIA GPU for Kubernetes. Observe pod placement and actual device visibility before a bounded query.



### Key terms

- **Pod:** The smallest Kubernetes scheduling unit, holding one or more containers.
- **Device plugin:** A Kubernetes component that advertises node GPUs as schedulable resources.
- **Resource discovery script:** A script Spark runs in each executor to report the GPU addresses that container can access.
- **Namespace:** A Kubernetes scope that isolates names and permissions for a named, owned environment.

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `eligible` | `['gpu-node']` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Draw scheduler layers

**Trap to avoid:** Debugging Spark task settings when executors never started confuses the two layers, since the problem sits at pod placement.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Name ownership boundaries

**Trap to avoid:** Running in the default namespace without labels mixes lab resources with others, making safe cleanup impossible. It also makes the cluster context easy to get wrong, so commands meant for a lab cluster can reach a shared one.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Diagnose Pending executors

**Trap to avoid:** Changing Spark code or increasing memory without reading events addresses the wrong layer. Raising executor memory can even make placement harder, since larger requests fit on fewer nodes.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Verify device visibility

**Trap to avoid:** Assuming visibility because the node has a GPU misses runtime misconfiguration that leaves the container without the device. The executor would then start and the plugin would fail at initialization, or the job would run entirely on CPU.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design private networking

**Trap to avoid:** Exposing the driver UI with a public load balancer for convenience makes job data reachable from outside. Query plans and configuration can include paths, table names and connection details.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Write scoped cleanup

**Trap to avoid:** Deleting by broad name patterns or whole namespaces you did not create can remove unrelated work. Deleting before saving logs also destroys the evidence needed to explain a failed run.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

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

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-125: GPU Spark on an explicitly owned Kubernetes cluster.
Read courses/cuda/spark/guides/cuda-125.md and courses/cuda/spark/lessons/cuda-125.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
