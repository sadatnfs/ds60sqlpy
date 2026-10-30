# spark-deploy-012: Budget memory, cores, PIDs and results

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-004`, `spark-039`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Budget the complete process tree

Executor heap is only one consumer. Java metaspace, direct buffers, Python workers, native libraries, thread stacks and filesystem cache also consume resources. A container memory limit below their combined requirement can kill an executor even when its configured heap appears modest. A notebook adds a kernel and server beside the driver.

The baseline topology limits each worker container to 1.5 GiB, one CPU and 512 PIDs, while the executor heap is 512 MiB and each worker advertises one core. Driver, master and History Server have separate limits. These are bounded teaching settings, not a recommendation for a production dataset. Inspect aggregate engine capacity and unrelated active workloads before starting the environment.

## Worked case A: compute a concurrency budget

```text
worker-a: one advertised core -> at most one one-core executor task at once
worker-b: one advertised core -> at most one one-core executor task at once
input: eight partitions
idealized minimum scheduling waves: eight / two = four
```

This arithmetic models available task slots, not measured timing. Empty partitions, scheduler delay, Python startup, skew and retries alter elapsed time. Increasing partitions can improve balance but also increases overhead and the number of returned summaries. Increasing executor cores changes concurrency, memory and native thread pressure together.

The live UI distinguishes executor tasks and scheduler stages. Compare the model with observed active tasks and recorded task durations. A CPU percentage alone cannot explain whether the job is computing, spilling, serializing or waiting for another process.

## Worked case B: diagnose three different failures

```text
OOMKilled / container exit 137: inspect container memory events and limits
unable to create native thread: inspect PID/thread limits and process counts
total serialized results exceed maxResultSize: inspect collection structure
```

These require different repairs. More driver heap does not fix an executor PID limit. More result budget may hide an accidental raw-data collection. A small heap can spill correctly without an OOM. Preserve the failed run and make one attributable configuration or code change before qualifying the repaired run.

The Kubernetes `resources.yaml` example supplies namespace quota and defaults. It is a teaching policy for a dedicated namespace. Spark-specific memory overhead, Python memory and ephemeral-storage requirements must fit those limits. A Pod Pending state due to quota or placement is not an application numerical failure.

## Diagnose and transfer

Bound native BLAS/OpenMP threads when numerical tasks run in parallel; two Spark tasks each spawning dozens of native threads can exceed the intended budget. Record both environment-wide caps and per-process controls. Repeatedly increasing limits without investigating can exceed the laptop's actual capacity and disturb unrelated work.

Keep one heavy local qualification environment active at a time when resources are constrained. Dynamic allocation, GPUs and autoscaling introduce additional scheduling mechanisms and are not established by this two-worker baseline. Their claims require their own measured topology and failure tests.

## Primary references

- [Spark resource configuration](https://spark.apache.org/docs/4.0.1/configuration.html)
- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
