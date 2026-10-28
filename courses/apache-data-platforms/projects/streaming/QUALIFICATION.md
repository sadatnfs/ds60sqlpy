# Kafka retention and lifecycle acceptance

The explicitly selected checksum-verified Kafka 4.4.0 binary/JDK route passed
actual native Linux ARM64 acceptance on 2026-10-27. The upstream image has verified
AMD64/ARM64 descriptors but its layers were not runtime-qualified here after a
verified TLS download failure. TLS checking was not disabled.

The maintained owned-workshop qualifier passed exact event payloads, actual two-
partition/RF1 metadata, effective delete-only infinite time/byte retention, exact
source-file SHA256 and per-partition end positions. Repeat initialization,
exact retained-container resume and replacement preserved the source and positions.

The real Java transaction probe retained exact read_committed 3/read_uncommitted 4
semantics, including the distinct identical business send calls, through replacement.
Its actual delete-only infinite time/byte retention was verified before use.
The consumer probe retains its manual-assignment and temporary-group boundaries;
no rebalance or injected network-retry claim is added.

The updated compacted-log probe verified actual policy/topology and read to the
actual end position. It preserved source SHA256, end offset 3 and latest-key state
across repeat, exact resume and replacement. Its Java invariant validator also
accepts a legitimate history with obsolete offset 0 absent, while rejecting partial,
duplicate, unknown payloads and changed ends. Raw historical count/offset 0 presence
are not the stable lifecycle identity. No forced physical-cleaner experiment was
performed, and physical_compaction_demonstrated remains false.

Unexpected retained policy/data is rejected without topic reset or silent
configuration mutation. The tiny fixtures are bounded by initialization and strict
oracles; infinite retention is not an unbounded production-stream recommendation.
The native Java/API compilation, pure semantic/policy tests and actual broker
observations are separate evidence categories. Local execution is ARM64 only;
AMD64 execution belongs to native GitHub runners without local emulation.

The qualifier removed only its newly owned synthetic broker containers, network
and volume after retaining evidence outside maintained source. Original learner
volumes and unrelated resources were preserved.
