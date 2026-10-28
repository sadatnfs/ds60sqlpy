# Kafka workshop maintenance

Read the root/course guidance and preserve explicit source, runtime and lifecycle
evidence boundaries. This is one owned KRaft broker, not a high-availability cluster.
Keep the pinned upstream route separate from the explicit checksummed binary/JDK
route. Never disable TLS or silently switch provenance. Native architecture guards
must run before pulls/builds; ordinary workers never receive an engine socket.

The tiny noncompacted event/transaction topics have explicit delete-only infinite
time/byte retention. Validate effective policy and actual partition/replica metadata,
not only creation arguments. Initialization runs only when empty. Unexpected existing
policy, partial data or payloads must fail without resetting or altering them.
The regular event report binds exact source bytes and both partition end positions.

A compacted log need not retain all three historical updates. The pure validator
and real KafkaConsumer accept optional offset 0=acct-1/v1, require offsets 1/2 with
exact latest values, require source end 3 and preserve the exact latest-key map.
Read to actual end position, not a fixed physical-message count. Physical record
count and retained positions can change after compaction; source identity/end and
latest state remain the semantic lifecycle contract. Do not claim a forced cleaner
experiment from configured policy or a tiny log observation.

Transaction visibility stays exact at three committed/four uncommitted data records.
Its two distinct business send calls must not be compacted away. Producer retry
idempotence is not application-level business deduplication. Consumer groups use
manual assignment in this fixture and do not qualify rebalancing.

Use separate dedicated retention tests and coordinate common qualifier/schema
changes with its owner. Compile pure invariants without a broker first, then run
real native broker positive/negative/repeat/resume/replacement checks in one bounded
pack. Preserve earlier receipts and source/position identity. Cleanup only verified
owned resources, retain learner volumes unless deletion is explicitly authorized,
and never prune unrelated state. Follow the actual package/architecture ledger.
