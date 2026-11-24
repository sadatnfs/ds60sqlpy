# spark-deploy-011: Separate scratch, checkpoints and published state

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-010`, `k8s-022`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Name which state must survive which failure

Executor scratch, a streaming checkpoint, a final model artifact and an event log serve different purposes. Scratch supports shuffle and spill and may be recreated. A checkpoint records progress/state needed by a compatible streaming query. A final result needs a publication contract. Event logs support investigation. Keeping one does not automatically preserve the others.

The teaching Compose lab uses tmpfs for scratch and owned host directories for reports/events/notebooks. No classroom learner volume is mounted. Its bounded batch fit regenerates deterministic inputs, so a task retry does not need a persistent training-data file. A real external source needs its own immutable input identity.

## Key terms

- **Executor scratch:** Disposable local storage for shuffle and spill that is lost with its container and can be recomputed.
- **Streaming checkpoint:** Recorded progress and state that a compatible streaming query needs to resume.
- **Persistent volume claim (PVC):** A Kubernetes storage request with its own access mode, topology, reclaim policy and permissions.
- **Publication contract:** The rules that make a final result durable, identifiable and safe to read back.
- **Input identity:** An immutable identifier for external source data so a task retry reads the same records.

## Worked case A: distinguish durable output from scratch

```text
/tmp/spark-local: executor-local, disposable, lost with container
/events: owned shared host directory, retained for history
/results: bounded JSON receipts, retained for readback
/notebooks: saved authored analysis, retained separately
```

Stopping a worker can lose cached partitions and shuffle files. Spark may recompute them from available lineage. Deleting `/results` would instead destroy the accepted evidence, and the launcher deliberately offers no command to do that. Compare a saved report before and after container replacement without rerunning the job.

For a copied package acceptance, do not use a shared source directory as an artifact-distribution shortcut if the package promises verified Spark file distribution. Observe the actual executor-local artifact path and identity under the package's contract.

## Worked case B: transfer the design to Kubernetes

```yaml
volumes:
  - name: scratch
    emptyDir:
      sizeLimit: 1Gi
containers:
  - name: example
    volumeMounts:
      - name: scratch
        mountPath: /var/data/spark-local
```

This Pod fragment describes bounded disposable scratch, not a complete Spark Pod template. It does not provide a persistent checkpoint or shared object storage. `emptyDir` lifetime follows the Pod. A PVC adds a storage claim with its own access mode, topology, reclaim policy and permissions. A ReadWriteOnce volume may not be mountable across the worker placement you selected. Consult the actual storage class before assuming shared access.

## Worked example: which paths survive which lab failure

```python
paths = {
    "/tmp/spark-local": "tmpfs in container",
    "/events": "host state dir",
    "/results": "host state dir",
    "/notebooks": "host state dir",
}
failures = {
    "executor JVM exits": {"tmpfs in container"},
    "worker container stopped": {"tmpfs in container"},
    "lab.py down then up": {"tmpfs in container"},
    "host state dir deleted": {"host state dir"},
}
for failure, destroyed in failures.items():
    lost = [p for p, kind in paths.items() if kind in destroyed]
    print(f"{failure:26} loses {lost}")
```

Output from running the block above:

```text
executor JVM exits         loses ['/tmp/spark-local']
worker container stopped   loses ['/tmp/spark-local']
lab.py down then up        loses ['/tmp/spark-local']
host state dir deleted     loses ['/events', '/results', '/notebooks']
```

The table restates the chapter's storage map as an executable check. Every failure that stays inside containers, an executor JVM crash, a stopped worker or a full `lab.py down` then `up`, destroys only `/tmp/spark-local`, the tmpfs scratch where shuffle and spill files live. Spark can rebuild that content from lineage because the bounded job regenerates its range input deterministically. The final row shows the only event that touches `/events`, `/results` and `/notebooks` together: deleting the host state directory, which the launcher intentionally provides no command for. The same model transfers to Kubernetes by replacing tmpfs with `emptyDir` and host directories with a PVC or object store, but then a node loss can also remove an `emptyDir`, and a ReadWriteOnce claim may follow a different lifecycle. Writing the mapping down before a failure rehearsal makes it obvious which before and after comparisons count as evidence and which are just regenerated scratch.

## Worked example: publishing a result directory so readers never see half of it

```python
import json
import os
import shutil
from pathlib import Path

root = Path("publish-demo")
final, staging = root / "fit-v1", root / ".fit-v1.staging"
staging.mkdir(parents=True)
for part in range(3):
    (staging / f"part-{part:05d}.json").write_text(json.dumps({"partition": part}) + "\n")
(staging / "_SUCCESS").write_text("")


def readable(path):
    return path.is_dir() and (path / "_SUCCESS").exists()


print("before rename, reader sees final:", readable(final))
os.rename(staging, final)
print("after rename, reader sees final:", readable(final), sorted(p.name for p in final.iterdir()))
retry = root / ".fit-v1.retry"
retry.mkdir()
(retry / "part-00000.json").write_text("{}\n")
try:
    os.rename(retry, final)
except OSError as error:
    print("retry onto the published directory refused:", type(error).__name__)
shutil.rmtree(root)
```

Output from running the block above:

```text
before rename, reader sees final: False
after rename, reader sees final: True ['_SUCCESS', 'part-00000.json', 'part-00001.json', 'part-00002.json']
retry onto the published directory refused: OSError
```

Readers of a result directory need a single moment when it switches from absent to complete. The script writes three part files and a `_SUCCESS` marker into a hidden staging directory, so a reader polling `fit-v1` sees nothing during the writes; then one `os.rename` makes the whole set visible at once. A retry that tries to rename a second staging directory onto the published one is refused with `OSError`, because POSIX rename will not replace a non-empty directory, which protects the accepted output from a late duplicate attempt. All of this happens in a scratch folder that is removed afterward. The guarantee depends on the filesystem: on a local disk or a POSIX shared mount the rename is atomic, while most object stores implement rename as copy then delete, so a reader can observe a partial set. For those stores use a committer or a manifest written last, and verify how readers decide that output is complete.

## Diagnose and transfer

When a resumed streaming query fails, compare source identity, query plan/state schema, checkpoint path and package version. Starting with an empty checkpoint can silently change processing semantics and is not a harmless repair. Keep an incompatible-change rehearsal in a new owned namespace while preserving the original state.

For object stores, separate authorization to read inputs, write outputs and read history. Use role/workload identity or reviewed secret mounts rather than embedding credentials in a URI. Define how readers distinguish complete output from a partially written set. A directory listing or zero process exit is not necessarily an atomic publication guarantee.

## Primary references

- [Spark Kubernetes storage and local directories](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#using-kubernetes-volumes)
- [Kubernetes volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
