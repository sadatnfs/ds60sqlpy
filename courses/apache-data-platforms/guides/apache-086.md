# apache-086: Failure and recovery game day

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-038`, `apache-056`, `apache-062`.

## Key terms

- **Game day:** A planned exercise that injects one named failure and checks recovery against an independent observation.
- **Failure injection:** Deliberately causing a specific failure, such as a process restart, in an owned workshop only.
- **Ownership label:** A random marker the course launchers verify before acting, so experiments never touch unrelated containers or volumes.
- **Reconciliation:** Reading existing state after an unknown outcome to decide whether a further write is needed, instead of replaying blindly.

## A recovery exercise starts with a specific failure claim

A game day is useful when it names the failure being injected, the state expected
to survive and the independent observation that will establish recovery. Process
restart, container replacement, node outage, schema mismatch and physical disk
loss are different experiments. Passing one must not be reported as passing all
of them.

Choose one already qualified owned workshop and preserve its source/image/native
platform identity. Export needed receipts before any destructive action. The
course launchers verify random ownership labels and retain named state on down;
only their explicit confirmed destroy removes synthetic data. Original learner
volumes and unrelated resources are outside every experiment.

Unknown outcomes need reconciliation. A client can lose its response after an
operation completes, and a receipt save can fail after a successful restore or
publication. Replaying the action blindly can create a second effect or hide
the original result. Read existing state before deciding whether another write
is appropriate.

## Worked case A: compare exact resume and replacement

Capture actual container IDs, image identities, source-bound fixture identity
and read-only result. Stop and resume with the workshop launcher and require
the same containers and semantic state. Then use down/start to create replacement
containers over retained volumes and require new process identities with the
same intended source/image and retained data.

Cassandra's identity route, for example, compares host UUID, replication policy
and exact order keys/values without fixture initialization. Kafka compares
noncompacted source positions and compacted latest-key semantics separately.
Choose the product-specific oracle rather than assuming every physical log must
retain an identical record count across maintenance.

Do not call initialize, produce or apply while checking persistence. A regenerated
three-row fixture can make an empty volume look healthy. Read-only readback is
what distinguishes retained state from reconstruction. Record each lifecycle
boundary explicitly in the evidence instead of one undifferentiated success flag.

## Worked case B: break one owned configuration

Copy the accepted workshop or selected configuration into a separate disposable
owned experiment. Introduce one clear mismatch, such as an unreachable advertised
endpoint or incompatible schema version. Require the expected typed failure and
preserve the first diagnostic. An arbitrary process crash is not the intended
negative oracle.

Restore the known configuration bytes and verify the same retained state without
resetting it. Compare source hash, selected image, state identity and semantic
readback. If the service remains unavailable, stop and report that unresolved
condition rather than broadening cleanup to unrelated volumes or rebuilding
random images.

Classify the effect: temporary unavailability, duplicate work, lost data, stale
read or rejected startup. A configuration error can prevent service without
losing any bytes. Conversely, a healthy endpoint can conceal a missing partition
or changed dataset. The classification determines which recovery action and
acceptance evidence are relevant.

## Diagnosis and interview discussion

Write a concise incident record with trigger, expected contract, observed failure,
owned resources, recovery action and independent post-recovery comparison.
Separate local Docker-host evidence from a different-host backup restore and
from production acceptance. Keep failed observations immutable so the dossier
explains what was fixed rather than merely showing the final green check.

**Interview discussion: why is a successful restart weaker than a recovery test?**
It may check only process availability, regenerate the fixture or connect to a
different project. These cases require exact lifecycle identities, read-only
state comparison and a controlled typed configuration failure before declaring
the selected recovery boundary passed.

## Worked examples

### Diff two identity receipts

```python
before = {"container": "c1", "image": "sha256:aa", "rows": [1, 2, 3]}
after = {"container": "c2", "image": "sha256:aa", "rows": [1, 2, 3]}
print({key: (before[key], after[key]) for key in before if before[key] != after[key]})
```

```text
{'container': ('c1', 'c2')}
```

Only the container changed, which is the expected signature of a replacement over retained volumes. The same image and rows show that state and software survived. After a plain resume the dictionary should be empty. Any change in rows is the failure the exercise is looking for, so it should be written down before anything is reinitialized.

### Break one setting in a disposable copy

```bash
cp -R work/hive work/hive-broken
cd work/hive-broken
bash run.sh verify-schema
```

Change exactly one value in the copy, such as the metastore database name in conf/hive-site.xml, and record the typed failure that verify-schema or start produces. Changing several things at once makes the error impossible to attribute. The original project stays untouched, so recovery means deleting the copy, not repairing the reference.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-086 complete worked notebook

Select one already qualified owned workshop. Compare exact resume and retained-state replacement using read-only identity actions. Break one configuration only in a separate disposable copy and retain its typed failure.

## What this game day receipt must hold

- The selected workshop, its source hash and the image ID it ran.
- Container IDs before stop, after resume and after down/start replacement.
- The read-only check result at each boundary, run without any initialize step.
- The single configuration change made in the disposable copy, as a diff.
- The first typed diagnostic the broken copy produced.
- The restored check result and confirmation that the learner's volume was untouched.

Container IDs carry most of this oracle. After resume they must match the IDs
taken before stop. After down/start they must differ while the semantic check
still passes over the same volume. For Cassandra, that check compares host UUID,
replication settings and the exact order rows. For Kafka retention, it compares
end offsets and the latest value per key. Equal IDs after replacement mean down
never ran. The [shared receipt rules](../STUDY-GUIDE.md#evidence-receipts)
cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../cassandra/README.md
cat ../streaming/QUALIFICATION.md
```

The Cassandra README's lifecycle block runs `stop`, `resume`, `check`, then
`down`, `start` and `check`. Down removes owned containers and the network but
keeps the data volume. The Kafka qualification ledger records end offset 3 and
latest-key state preserved across repeat, resume and replacement, with physical
compaction not demonstrated. Use those recorded facts as the expected values.

## Primary references

- [Cassandra consistency and durability guarantees](https://cassandra.apache.org/doc/5.0/cassandra/architecture/guarantees.html)
- [Kafka broker operations and retention](https://kafka.apache.org/44/operations/)
- [Docker Compose networks for owned services](https://docs.docker.com/compose/how-tos/networking/)
