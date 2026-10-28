# Flink workshop maintenance

Follow the root/course guidance and Add a learning path skill. Keep Flink 2.3.0,
its reviewed archive size/SHA512 and the native Java 17 toolchain together.
Preparation is explicit; no package or connector download belongs to reading,
resume or job execution. Preserve source licenses and reject archive paths/links
before extraction. No implicit architecture emulation or TLS bypass.

The actual private pack has one JobManager and one TaskManager. Keep RPC/REST
addresses distinct from host browser URLs and retain private admin endpoints.
Custom configuration must preserve the selected release's Java 17 module options.
A listener alone does not prove TaskManager registration or useful slots.

TimelineSource is a real nonblocking Source API implementation with explicit
record timestamps, watermarks and bounded versioned split state. Keep late-window
behavior separate from the keyed function's explicitly selected late-record rule.
Managed totals, timer replacement and cleanup must match independent oracles.

Recovery needs actual completed checkpoint metadata and committed records before
interruption, then an actual restoration and exact final source/state/sink result.
Savepoint migration needs stable UIDs/state types/source/sink ownership. A changed
UID must fail specifically at state mapping without allowing dropped state.
A local file-sink result does not qualify a transactional Kafka connector or HA.

Keep versioned artifacts, failed/unknown request diagnostics and immutable receipts.
Never automatically replay an unknown submission. Readback does not submit work;
explicit reconcile may observe/finalize an existing known job only. Receipt-storage
failure must keep the actual result visible with a distinct warning. Preserve
existing completed/pending state and never reset a volume to make a check pass.

Use exact-container resume, retained-volume replacement and ownership-checked
confirmed deletion. Local ARM64 runtime evidence is separate from native AMD64 CI
and published descriptors. Record actual measured backpressure rather than inferring
it from artificial delay or slot configuration. Bound metrics/data/source counts.
