# cuda-125: explained solutions

Compare with your [worksheet](../lessons/cuda-125.md) attempt.

## Exercise 1: Draw scheduler layers

Kubernetes allocates pods and Spark allocates tasks.

**Approach.** Draw scheduler layers: Kubernetes schedules driver and executor pods onto nodes based on resource requests such as `nvidia.com/gpu: 1`, and Spark then schedules tasks onto executors.

**Why it is correct here.** A GPU executor must first be placed on a node that advertises the GPU resource. Only after that does Spark's task scheduling apply.

**A plausible wrong approach.** Debugging Spark task settings when executors never started confuses the two layers, since the problem sits at pod placement.

**How to verify.** The reference finds `eligible == ['gpu-node']`. In a cluster, check node allocatable resources for the GPU resource name.

## Exercise 2: Name ownership boundaries

Use exact cluster namespace labels and job identity.

**Approach.** Name ownership boundaries: the exact cluster context, a dedicated namespace and labels identifying the job, so every created resource can be identified.

**Why it is correct here.** Shared clusters host other workloads. Explicit namespace and labels allow inspection and cleanup without touching unrelated resources.

**A plausible wrong approach.** Running in the default namespace without labels mixes lab resources with others, making safe cleanup impossible. It also makes the cluster context easy to get wrong, so commands meant for a lab cluster can reach a shared one.

**How to verify.** List resources with the job label and confirm they are all in the lab namespace. Print the current context before each command so the target cluster is visible in the session log.

## Exercise 3: Diagnose Pending executors

Read events and resource availability.

**Approach.** Diagnose Pending executors by reading pod events and comparing requested resources with node availability, such as a GPU request when no free GPU node exists.

**Why it is correct here.** Events state why the scheduler could not place the pod. A running driver with Pending executors proves submission worked but placement did not.

**A plausible wrong approach.** Changing Spark code or increasing memory without reading events addresses the wrong layer. Raising executor memory can even make placement harder, since larger requests fit on fewer nodes.

**How to verify.** Run `kubectl describe pod` on a Pending executor and act on the scheduling message. Messages such as insufficient GPU resources or an untolerated node taint each point to a different fix.

## Exercise 4: Verify device visibility

Run a bounded owned executor probe.

**Approach.** Verify device visibility with a bounded probe executor that lists GPUs inside its container and exits.

**Why it is correct here.** A pod scheduled on a GPU node still needs the device plugin and container runtime to expose the device.

**A plausible wrong approach.** Assuming visibility because the node has a GPU misses runtime misconfiguration that leaves the container without the device. The executor would then start and the plugin would fail at initialization, or the job would run entirely on CPU.

**How to verify.** Check the probe output for the expected device, then delete the probe pod. Also confirm the driver version reported inside the container meets the plugin release's minimum.

## Exercise 5: Design private networking

Keep internal services private.

**Approach.** Design private networking: keep the Spark UI, driver service and any internal endpoints private, reachable only through controlled port forwarding.

**Why it is correct here.** Spark services can expose job details and accept connections. Public exposure creates risk with no benefit for a lab.

**A plausible wrong approach.** Exposing the driver UI with a public load balancer for convenience makes job data reachable from outside. Query plans and configuration can include paths, table names and connection details.

**How to verify.** List services in the namespace and confirm none has a public external address. Use `kubectl port-forward` for temporary UI access and close it after inspection.

## Exercise 6: Write scoped cleanup

Delete only resources created for this named lab and preserve requested logs.

**Approach.** Write scoped cleanup that deletes only resources carrying the lab's labels in its namespace, after saving the logs requested for the record.

**Why it is correct here.** Label-scoped deletion protects other workloads, and preserving logs first keeps evidence.

**A plausible wrong approach.** Deleting by broad name patterns or whole namespaces you did not create can remove unrelated work. Deleting before saving logs also destroys the evidence needed to explain a failed run.

**How to verify.** List labeled resources before and after cleanup and confirm only those were removed and the logs remain saved.

## Self-check answers

1. **Does a pod's GPU resource limit prove the plugin can run?** No. The image, driver and native libraries must also support Spark GPU execution inside the container.

2. **Can Docker Desktop on a Mac provide an NVIDIA GPU to Kubernetes?** No. It is useful for the CPU classroom but does not create an NVIDIA GPU.

3. **What advertises GPU resources to the Kubernetes scheduler?** An installed and configured device plugin on the nodes that have GPUs.

## Reference observation

Only the illustrative GPU node is eligible; no cluster operation occurs.

Asserted by `courses/cuda/spark/references/cuda-125_cpu.py`.
