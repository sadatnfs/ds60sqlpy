# spark-deploy-012: Budget memory, cores, PIDs and results

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-004`, `spark-039`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Budget the complete process tree

Executor heap is only one consumer. Java metaspace, direct buffers, Python workers, native libraries, thread stacks and filesystem cache also consume resources. A container memory limit below their combined requirement can kill an executor even when its configured heap appears modest. A notebook adds a kernel and server beside the driver.

The baseline topology limits each worker container to 1.5 GiB, one CPU and 512 PIDs, while the executor heap is 512 MiB and each worker advertises one core. Driver, master and History Server have separate limits. These are bounded teaching settings, not a recommendation for a production dataset. Inspect aggregate engine capacity and unrelated active workloads before starting the environment.

## Key terms

- **Process tree budget:** The combined memory of heap, metaspace, direct buffers, Python workers, native libraries, threads and cache in one container.
- **Container memory limit:** The hard ceiling, 1.5 GiB per worker here, above which the container is killed regardless of the configured heap.
- **Executor heap:** The JVM heap set for each executor, 512 MiB in this lab, which is only one memory consumer.
- **PID limit:** The cap on processes and threads in a container, 512 per worker in this lab.
- **Maximum result size:** The spark.driver.maxResultSize limit that makes an oversized collect fail instead of exhausting driver memory.

## Worked case A: compute a concurrency budget

```text
worker-a: one advertised core -> at most one one-core executor task at once
worker-b: one advertised core -> at most one one-core executor task at once
input: eight partitions
idealized minimum scheduling waves: eight / two = four
```

The application side of the budget is set in `conf/spark-defaults.conf`:

From [`projects/cluster-lab/conf/spark-defaults.conf`](../projects/cluster-lab/conf/spark-defaults.conf):

```properties
spark.driver.memory                  1g
spark.driver.maxResultSize           1m
spark.executor.memory                512m
spark.executor.cores                 1
spark.cores.max                      2
```

`spark.cores.max 2` caps the application at two cores across the cluster, and
`spark.driver.maxResultSize 1m` makes an oversized collect fail instead of
exhausting driver memory. The container limits in `compose.yaml` are a separate,
outer bound.

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

## Worked example: a worker container memory ledger and scheduling waves

```python
import math

limit = 1536
consumers = {
    "worker daemon (SPARK_DAEMON_MEMORY)": 256,
    "executor heap (spark.executor.memory)": 512,
    "executor JVM non-heap, estimate": 384,
    "Python worker for one task, estimate": 150,
}
used = sum(consumers.values())
for name, mib in consumers.items():
    print(f"{mib:5} MiB  {name}")
print(f"{used:5} MiB  total, headroom {limit - used} MiB of {limit}")
slots = 2 * 1
for partitions in (8, 9, 16):
    print(f"{partitions} partitions over {slots} slots -> {math.ceil(partitions / slots)} waves")
```

Output from running the block above:

```text
  256 MiB  worker daemon (SPARK_DAEMON_MEMORY)
  512 MiB  executor heap (spark.executor.memory)
  384 MiB  executor JVM non-heap, estimate
  150 MiB  Python worker for one task, estimate
 1302 MiB  total, headroom 234 MiB of 1536
8 partitions over 2 slots -> 4 waves
9 partitions over 2 slots -> 5 waves
16 partitions over 2 slots -> 8 waves
```

The ledger adds the long-lived processes in one worker container. `SPARK_DAEMON_MEMORY` is 256m in `compose.yaml` and `spark.executor.memory` is 512m in the defaults; those two numbers are configured. The 384 MiB non-heap figure borrows the minimum overhead that Spark uses for resource managers, and the 150 MiB Python worker is a rough estimate, so both should be replaced by measured resident sizes from `docker stats` or `/proc` during a run. Even with these estimates, 1302 MiB of the 1536 MiB limit is committed, leaving 234 MiB for thread stacks, native libraries and page cache. The second half restates Worked case A: with two one-core slots, eight partitions need four waves, nine need five because one straggler partition gets a wave to itself, and sixteen need eight. These counts are scheduling arithmetic, not timings, and adding partitions to improve balance also adds per-task startup cost and more summaries returned to the driver.

## Worked example: routing a failure message to the right budget

```python
import re

RULES = [
    (
        r"[Ee]xit code (is )?137|OOMKilled",
        "container memory: compare limit with the whole process tree",
    ),
    (r"unable to create native thread|Resource temporarily unavailable", "PID or thread limit"),
    (r"bigger than spark\.driver\.maxResultSize", "result size: inspect what is being collected"),
    (r"java\.lang\.OutOfMemoryError: Java heap space", "JVM heap of the reporting process"),
]
messages = [
    "Container killed on request. Exit code is 137",
    "java.lang.OutOfMemoryError: unable to create native thread: possibly out of memory or process/resource limits reached",
    "Total size of serialized results of 9 tasks (1100.3 KiB) is bigger than spark.driver.maxResultSize (1024.0 KiB)",
    "java.lang.OutOfMemoryError: Java heap space",
]
for message in messages:
    match = next((label for pattern, label in RULES if re.search(pattern, message)), "unclassified")
    print(f"{match:58} <- {message[:48]}")
```

Output from running the block above:

```text
container memory: compare limit with the whole process tree <- Container killed on request. Exit code is 137
PID or thread limit                                        <- java.lang.OutOfMemoryError: unable to create nat
result size: inspect what is being collected               <- Total size of serialized results of 9 tasks (110
JVM heap of the reporting process                          <- java.lang.OutOfMemoryError: Java heap space
```

Each message is a realistic form of the three failures in Worked case B plus a heap exhaustion, and each routes to a different budget. Exit 137 means the kernel or runtime killed the container, so the comparison is the container limit against the whole process tree, not the JVM heap setting. The native thread message names an OutOfMemoryError but is actually a PID or thread limit, here 512 per worker, and raising `spark.executor.memory` would not help. The `maxResultSize` text, with 1100.3 KiB from nine tasks against a 1024 KiB bound, says the driver refused a collection, so the right question is what the job returns, not how big the driver heap is. Only the last line points at heap size, and even then it names the process that reported it. Order matters in the rule list because the thread message also contains OutOfMemoryError; checking the specific pattern first keeps it from being filed as a heap problem.

## Diagnose and transfer

Bound native BLAS/OpenMP threads when numerical tasks run in parallel; two Spark tasks each spawning dozens of native threads can exceed the intended budget. Record both environment-wide caps and per-process controls. Repeatedly increasing limits without investigating can exceed the laptop's actual capacity and disturb unrelated work.

Keep one heavy local qualification environment active at a time when resources are constrained. Dynamic allocation, GPUs and autoscaling introduce additional scheduling mechanisms and are not established by this two-worker baseline. Their claims require their own measured topology and failure tests.

## Primary references

- [Spark resource configuration](https://spark.apache.org/docs/4.0.1/configuration.html)
- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
