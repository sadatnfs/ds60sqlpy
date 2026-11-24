# spark-deploy-003: Own an isolated Compose topology

Tutorial mode. Stage: beginner. Direct prerequisites: `spark-deploy-002`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Own the topology and its saved state

The Compose project has a master, two workers, a separate driver and a History Server. The notebook is optional. All Spark compute services join a private internal network. A narrow UI relay connects that network to a separate ingress network and publishes only fixed HTTP destinations on host loopback with dynamically chosen ports. No service receives the Docker socket, host credentials or a learner volume. Spark application code is trusted local code in this single-user lab.

`lab.py` records a random project identity and checks ownership labels before operating on containers. State is a separate host directory containing event logs, bounded results, notebooks and a private login token. Container replacement and state deletion are different actions. The wrapper provides no state-destruction command.

## Key terms

- **Compose project:** The owned topology of master, two workers, a separate driver, a History Server and an optional notebook.
- **Internal network:** A private Docker network shared by the Spark compute services with no direct host access.
- **UI relay:** A narrow service that connects the internal network to an ingress network and publishes only fixed HTTP destinations on host loopback.
- **Ownership label:** A container label carrying the recorded project identity, checked before the wrapper operates on any container.
- **State directory:** The host directory holding event logs, results, notebooks and the login token, which survives container replacement.

## Worked case A: bring up the owned services

After initialization in the preceding chapter:

The two workers share one YAML anchor and differ only in name, command and limits:

From [`projects/cluster-lab/compose.yaml`](../projects/cluster-lab/compose.yaml):

```yaml
worker-a:
  <<: *runtime
  hostname: worker-a
  environment:
    <<: *spark-environment
    SPARK_LOCAL_IP: worker-a
  command: [worker, worker-a]
  mem_limit: 1536m
  cpus: 1
  pids_limit: 512
  depends_on: [master]
```

`<<: *runtime` merges the shared settings: the read-only root filesystem, the
dropped capabilities and the private `lab` network. `SPARK_LOCAL_IP` is the name
the worker advertises, and `mem_limit`, `cpus` and `pids_limit` are the container
bounds that chapter 12 turns into a concurrency budget.

```sh
python3 lab.py up
python3 lab.py status
python3 lab.py urls
```

`up` explicitly disables builds and pulls. Compose creation order is not readiness: each worker waits for the master socket, while the application separately waits for its required executors. A listening master alone does not prove correct data processing. Expect the five Spark services plus their UI relay, two registered workers in the master UI and dynamic loopback URLs. Do not assume that the host's port is the container's port.

Each worker advertises one core and one GiB to the master. The container limit includes more than executor heap. The combined environment needs headroom for the driver, master, History Server, Java/Python processes, native memory and other active work. The declared limits are small teaching budgets, not production sizing guidance.

## Worked case B: stop, resume and replace without deleting evidence

```sh
python3 lab.py stop
python3 lab.py resume
python3 lab.py down
python3 lab.py up
```

Stop and resume use existing containers. Down removes only this project's containers and network, preserving the saved files. A subsequent up recreates containers using the saved image IDs. Event logs and JSON results should remain byte-identical if no new application has written to them. Container IDs may change after replacement and must not be used as persistent data identity.

Before a lifecycle comparison, record the filenames and hashes you intend to preserve. Afterward, compare those same files and read a completed report without submitting its application again. A fresh successful run is different evidence from retained-result readback.

## Worked example: summing the declared container budgets in compose.yaml

```python
services = {
    "master": ("512m", 0.2, 128),
    "worker-a": ("1536m", 1.0, 512),
    "worker-b": ("1536m", 1.0, 512),
    "driver": ("1536m", 1.0, 512),
    "history": ("768m", 0.2, 256),
    "ui": ("96m", 0.1, 96),
}
mib = {name: int(limit.rstrip("m")) for name, (limit, _, _) in services.items()}
print(f"memory limits total {sum(mib.values())} MiB = {sum(mib.values()) / 1024:.2f} GiB")
print(f"cpu quota total {sum(c for _, c, _ in services.values()):.1f}")
print(f"pids total {sum(p for *_, p in services.values())}")
worker_advertised = 1024
print(
    f"per worker: {mib['worker-a'] - worker_advertised} MiB of container limit above the 1 GiB advertised to the master"
)
```

Output from running the block above:

```text
memory limits total 5984 MiB = 5.84 GiB
cpu quota total 3.5
pids total 2016
per worker: 512 MiB of container limit above the 1 GiB advertised to the master
```

These six services and their limits are copied from compose.yaml, and the totals are plain arithmetic over them. Together the limits allow 5984 MiB of memory, 3.5 CPUs of quota and 2016 process IDs, so a laptop with 8 GiB of memory and other applications open is already close to its ceiling before the optional notebook adds another 1536 MiB. Each worker advertises 1 GiB to the master but its container may use 1536 MiB, and the 512 MiB difference is what the worker JVM, the executor JVM overhead and Python task processes share. Shrinking the container limit to exactly the advertised value would look tidy and then fail under load with an OOM kill that Spark reports only as a lost executor. Treat these totals as the budget for one owned lab, not as sizing advice for a production cluster.

## Worked example: hashing retained state before and after replacement

```python
import hashlib
from pathlib import Path

state = Path("demo-state")
(state / "events").mkdir(parents=True, exist_ok=True)
(state / "results").mkdir(exist_ok=True)
(state / "events" / "app-20260101000000-0000").write_text(
    '{"Event":"SparkListenerApplicationEnd"}\n'
)
(state / "results" / "app-20260101000000-0000.json").write_text('{"slope": 2.0}\n')


def manifest(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


before = manifest(state)
container_id_before, container_id_after = "3b9f0c2a", "c71e55d4"
after = manifest(state)
print("files:", len(before), "| identical after down/up:", before == after)
print("container id changed:", container_id_before != container_id_after)
for path, digest in before.items():
    print(digest, path)
for p in sorted(state.rglob("*"), reverse=True):
    p.unlink() if p.is_file() else p.rmdir()
state.rmdir()
```

Output from running the block above:

```text
files: 2 | identical after down/up: True
container id changed: True
a0895cdcd25d6cae events/app-20260101000000-0000
10ec9d3b5a05814a results/app-20260101000000-0000.json
```

The script builds a tiny state directory, computes a manifest of SHA-256 prefixes for every retained file, and compares two manifests. Both manifests are computed in the same process, so they match trivially; in the real lifecycle check the second manifest comes after lab.py down and lab.py up, and that comparison is the evidence. The printed container IDs are placeholders that illustrate why IDs cannot be data identity: replacement assigns new ones while the event log and result file keep the same bytes. A changed hash after replacement means something wrote to state, perhaps a new application or a History Server compaction setting, and should be explained before the old result is used. The example deletes its own scratch directory at the end, which mirrors the lab rule that cleanup touches only paths the workshop created.

## Diagnose and transfer

If an unrelated container shares the project label but lacks the workshop owner label, the wrapper refuses the operation. Investigate ownership rather than deleting it. If the saved image was removed, prepare the exact intended image deliberately or start a new owned lab; a silent tag substitution would invalidate the original receipt.

An internal Compose network prevents ordinary outbound routing but is not a sandbox for hostile code or a replacement for application authentication. Keep the lab on a trusted engine. The security chapters explain what changes when peers, machines or users cease to be trusted.

## Primary references

- [Compose networking and service names](https://docs.docker.com/compose/how-tos/networking/)
- [Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/)
