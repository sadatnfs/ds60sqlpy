# apache-086: Failure and recovery game day

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-038`, `apache-056`, `apache-062`.

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

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Integration apache-086 complete worked notebook

Select one already qualified owned workshop. Compare exact resume and retained-state replacement using read-only identity actions. Break one configuration only in a separate disposable copy and retain its typed failure.

## Receipt fields and independent oracle

- Source revision/hashes and exact declared input IDs, values, schema and time units.
- Actual native platform, package/image identities and owned resource namespace.
- Selected table snapshot/version, source positions or process/lineage identity as appropriate.
- Positive result against an independent oracle and a typed negative observation.
- Read-only retained-state comparison after the selected lifecycle transition.
- Cleanup/evidence-storage result and any separate prepared or unavailable feature.

For the common three-order fixture, require IDs 1/2/3 with amounts 4/9/7, total 20,
east 11 and west 9. A later fourth west order of2changes current total to22 and west
to11while an earlier pinned snapshot remains unchanged. Do not use this simple
oracle to claim correctness for a different pipeline without defining its
deduplication, correction and visibility semantics.

Read the selected project README and qualification ledger before commands. The
classroom does not execute Docker commands in this Markdown pad. Prepared
configuration, unit policy fixtures, successful compilation and actual service
acceptance remain different observations. Never include credentials or signed URLs.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../cassandra/README.md
cat ../streaming/QUALIFICATION.md
```

These inspections do not start or qualify a service. Execute only the chosen
project's complete documented owned route and retain its actual receipt.

## Primary references

- [Iceberg reliability and table state](https://iceberg.apache.org/docs/latest/reliability/)
- [Arrow data format](https://arrow.apache.org/docs/format/Columnar.html)
- [Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
- [Kafka delivery/transaction design](https://kafka.apache.org/44/design/design/)
- [Atlas API and metadata boundaries](https://atlas.apache.org/api/v2/index.html)
- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
