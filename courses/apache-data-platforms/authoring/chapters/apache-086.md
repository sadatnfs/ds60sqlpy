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
