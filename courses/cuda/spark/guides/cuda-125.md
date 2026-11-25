# cuda-125: GPU Spark on an explicitly owned Kubernetes cluster

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-114`, `cuda-119`, `cuda-122`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Draw scheduler layers.
- Name ownership boundaries.
- Diagnose Pending executors.
- Verify device visibility.
- Design private networking.
- Write scoped cleanup.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-125_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-125_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-125.md) before opening hints.

### Exercise 1: Draw scheduler layers

**Trap to avoid:** Debugging Spark task settings when executors never started confuses the two layers, since the problem sits at pod placement.

### Exercise 2: Name ownership boundaries

**Trap to avoid:** Running in the default namespace without labels mixes lab resources with others, making safe cleanup impossible. It also makes the cluster context easy to get wrong, so commands meant for a lab cluster can reach a shared one.

### Exercise 3: Diagnose Pending executors

**Trap to avoid:** Changing Spark code or increasing memory without reading events addresses the wrong layer. Raising executor memory can even make placement harder, since larger requests fit on fewer nodes.

### Exercise 4: Verify device visibility

**Trap to avoid:** Assuming visibility because the node has a GPU misses runtime misconfiguration that leaves the container without the device. The executor would then start and the plugin would fail at initialization, or the job would run entirely on CPU.

### Exercise 5: Design private networking

**Trap to avoid:** Exposing the driver UI with a public load balancer for convenience makes job data reachable from outside. Query plans and configuration can include paths, table names and connection details.

### Exercise 6: Write scoped cleanup

**Trap to avoid:** Deleting by broad name patterns or whole namespaces you did not create can remove unrelated work. Deleting before saving logs also destroys the evidence needed to explain a failed run.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Draw Kubernetes placing pods on nodes and Spark placing tasks on executors as two separate layers.
2. Name the exact cluster, namespace, labels and job identity that this lab may touch.
3. Read the pod events and compare the requested resources with what eligible nodes advertise.
4. Run a small probe inside an owned executor container to see which devices it can actually access.
5. Ask which services must stay internal and how you would reach them without exposing them publicly.
6. List only the resources this lab created and delete those, keeping any logs you were asked to preserve.

## Common mistakes and self-check

A common mistake is treating a running driver pod as proof that GPU Spark works. If executors stay Pending, only submission succeeded. Another is using an ambient kubeconfig or exposing the driver service publicly for convenience. Fix both by working only in a named disposable cluster and namespace, reading events and resource requests for Pending pods, confirming device visibility inside an executor and cleaning up only resources this lab created.

**Misconception:** If Spark requests a GPU for each executor, Kubernetes will find a GPU node automatically. **Correction:** The scheduler can place the pod only on a node whose device plugin advertises enough GPUs and whose taints, selectors and other resource limits allow it. Spark must also be given a discovery script or an equivalent so the executor reports the device address it received. Check node capacity, pod events and the executor's discovered address.

**Evidence limit:** The reference marks the single illustrative GPU node as eligible and performs no cluster operation. Device plugins, image provenance, scheduling and real device visibility can only be checked in an explicitly owned Kubernetes cluster.

1. Does a pod's GPU resource limit prove the plugin can run?
2. Can Docker Desktop on a Mac provide an NVIDIA GPU to Kubernetes?
3. What advertises GPU resources to the Kubernetes scheduler?

Answers: [self-check answers](../solutions/cuda-125_solutions.md#self-check-answers).

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-125: GPU Spark on an explicitly owned Kubernetes cluster.
Read courses/cuda/spark/guides/cuda-125.md and courses/cuda/spark/lessons/cuda-125.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
