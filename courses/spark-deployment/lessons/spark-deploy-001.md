# spark-deploy-001: Processes, deploy modes and ports

Tutorial mode. Stage: beginner. Direct prerequisites: `spark-030`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Separate the process from the machine

The beginner stage here refers to deployment experience. The chapter assumes the driver, executor and cluster-manager vocabulary from the advanced `spark-030` architecture lesson, and it starts from that vocabulary rather than teaching Spark itself.

A Spark application has one driver, which creates its session and schedules work, and executors, which run tasks. A cluster manager allocates those executors. In Standalone, the master knows available workers; a worker launches executor processes. A worker is therefore not an executor and a container is not a physical machine. Two worker containers on this laptop share its CPU, memory, storage and failure domain.

The word client describes driver placement. In client deploy mode, the submitting process contains the driver. In cluster deploy mode, the manager starts a driver elsewhere. A separate Docker driver container still uses client mode. A notebook kernel usually contains a client-mode driver. Spark Connect is a different client/server API boundary and is not the execution path in this workshop.

Read a port as a destination belonging to one process. The master listens on 7077 for Spark traffic and its own UI on 8080. An application driver uses 4040 for its UI by default. Driver RPC and block transfers are separate channels; this project fixes its driver RPC at 39000 and driver block manager at 39001. A browser port does not substitute for either.

The workshop's own submit call in `lab.py` runs `spark-submit` inside the driver container through the saved Compose command (`cmd`) and spells out the master URL, the client deploy mode and both fixed driver ports:

From [`projects/cluster-lab/lab.py`](../projects/cluster-lab/lab.py):

```python fragment
options = [
    "--hold-seconds",
    str(args.hold_seconds),
    "--partition-seconds",
    str(args.partition_seconds),
]
if args.allow_one_worker:
    options.append("--allow-one-worker")
run(
    [
        *cmd,
        "exec",
        "-T",
        "driver",
        "/opt/spark/bin/spark-submit",
        "--master",
        "spark://master:7077",
        "--deploy-mode",
        "client",
        "--conf",
        "spark.driver.host=driver",
        "--conf",
        "spark.driver.bindAddress=0.0.0.0",
        "--conf",
        "spark.driver.port=39000",
        "--conf",
        "spark.driver.blockManager.port=39001",
        "/lab/app/bounded_job.py",
        *options,
    ],
    env=env,
    timeout=360,
)
```

## Key terms

- **Driver:** The process that creates the Spark session and schedules work for one application.
- **Worker:** A Standalone process that launches executor processes on its host; it is not itself an executor.
- **Deploy mode:** Where the driver runs: inside the submitting process in client mode, or started by the manager elsewhere in cluster mode.
- **Master URL:** The cluster manager address, here the Standalone master listening on port 7077 for Spark traffic.
- **Driver RPC port:** The fixed port, 39000 in this project, on which executors reach the driver; a browser UI port such as 4040 cannot substitute for it.

## Worked case A: trace a separate driver

```text
submit command -> driver container -> master:7077
worker-a -> executor JVM -> Python task process
worker-b -> executor JVM -> Python task process
executors -> driver:39000 and driver:39001
browser -> loopback-published driver UI -> driver:4040
```

The expected observation is a driver hostname of `driver`, partition hosts from both workers and two non-driver executor records. Worker host plus process identity distinguishes processes even when container PID namespaces reuse the same numeric PID. The receipt in `app/bounded_job.py` records Python worker PIDs and separately queries the JVM executor inventory. Neither record alone proves separate physical hosts.

## Worked case B: move the driver, then change the address

```text
Before: driver.host=driver, driver.bindAddress=0.0.0.0
After moving to notebook: driver.host=notebook, bindAddress unchanged
Wrong advertisement: driver.host=127.0.0.1
```

Binding chooses interfaces on the driver's own container. Advertising tells executors where to call back. Advertising loopback tells each executor to contact itself, so master registration may succeed while tasks cannot communicate with the real driver. Publishing 4040 on the host does not repair the RPC route. The changed condition is driver placement, not a changed algorithm.

## Worked example: classifying every port in the lab submit command

```python
argv = [
    "spark-submit",
    "--master",
    "spark://master:7077",
    "--deploy-mode",
    "client",
    "--conf",
    "spark.driver.host=driver",
    "--conf",
    "spark.driver.bindAddress=0.0.0.0",
    "--conf",
    "spark.driver.port=39000",
    "--conf",
    "spark.driver.blockManager.port=39001",
    "/lab/app/bounded_job.py",
]
conf = dict(argv[i + 1].split("=", 1) for i, a in enumerate(argv) if a == "--conf")
master = argv[argv.index("--master") + 1]
owners = {
    int(master.rsplit(":", 1)[1]): ("master", "Spark RPC from drivers and workers"),
    8080: ("master", "browser UI"),
    int(conf["spark.driver.port"]): ("driver", "executor callbacks (RPC)"),
    int(conf["spark.driver.blockManager.port"]): ("driver", "block transfers"),
    4040: ("driver", "browser UI, from spark-defaults.conf"),
}
print(
    "deploy mode:",
    argv[argv.index("--deploy-mode") + 1],
    "| advertised as:",
    conf["spark.driver.host"],
)
for port in sorted(owners):
    process, purpose = owners[port]
    print(f"{port:>5}  {process:<7} {purpose}")
```

Output from running the block above:

```text
deploy mode: client | advertised as: driver
 4040  driver  browser UI, from spark-defaults.conf
 7077  master  Spark RPC from drivers and workers
 8080  master  browser UI
39000  driver  executor callbacks (RPC)
39001  driver  block transfers
```

The script reads the same argument list that lab.py passes to spark-submit and assigns each port to the process that owns it. Two of the five numbers belong to the master: 7077 accepts Spark RPC from drivers and workers, and 8080 serves its own status page. The other three belong to the driver, and only one of those, 4040, is meant for a browser. Ports 39000 and 39001 carry executor callbacks and block transfers, which is why they are pinned instead of left random: the Compose network and any later firewall or Kubernetes Service must route exactly those two numbers to the process advertised as driver. The printed deploy mode is client even though the driver runs in its own container, because placement is decided by where spark-submit starts the driver, not by which box it lives in. Keep a table like this in the receipt so a reviewer can tell an unreachable UI apart from an unreachable RPC route.

## Worked example: recording driver and task placement from inside the application

```python external
import os
import socket

from pyspark import TaskContext
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("placement-trace").getOrCreate()


def where(rows):
    context = TaskContext.get()
    yield (context.partitionId(), socket.gethostname(), os.getpid(), sum(1 for _ in rows))


try:
    placement = spark.range(0, 800, numPartitions=8).rdd.mapPartitions(where).collect()
    print("driver host:", socket.gethostname())
    for partition, host, pid, count in sorted(placement):
        print(partition, host, pid, count)
finally:
    spark.stop()
```

This PySpark block is shown without output because it must run on the workshop's Standalone cluster, and host names or PIDs copied from any other machine would mislead. On the workshop driver, expect the first line to report driver and the partition rows to name worker-a and worker-b, each with Python worker PIDs that may repeat across containers because every container has its own PID namespace. That repetition is why the bounded job records host and PID together. Eight partitions of 800 rows should each report a count of 100. If every partition reports the same host, either one worker failed to register or the executors were placed on one worker by the resource request; compare the executor inventory from the driver UI before blaming the network. A placement trace like this establishes which container ran which partition, which is narrower than proving separate physical hosts, since both workers share one laptop.

## Diagnose and transfer

If the master lists a worker but the application has no executors, inspect requested resources and worker launch logs. If executors appear but tasks fail to register or fetch blocks, inspect advertised driver DNS and the two data/control ports. Record whether a number is a worker count, executor count, task count or input partition count. These can differ without contradiction.

Explain the same trace for Kubernetes: the Kubernetes API replaces the Standalone master for allocation, while driver and executor communication still matters. The later Kubernetes chapters provide the process-specific configuration rather than treating a cluster-manager URL as a complete deployment.

## Primary references

- [Spark application submission](https://spark.apache.org/docs/4.0.1/submitting-applications.html)
- [Spark Standalone roles](https://spark.apache.org/docs/4.0.1/spark-standalone.html)
