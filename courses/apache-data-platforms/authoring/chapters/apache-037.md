## Retention policies decide which history remains available

Deletion retention removes old log segments according to configured size or time
policies. Compaction retains the latest value for each key as older eligible log
segments are cleaned, with tombstones expressing keyed deletion under their own
retention conditions. Compaction is asynchronous and does not promise that every
old value disappears immediately after a newer record is acknowledged.

A compacted topic can therefore contain several versions of a key when a consumer
reads it. An application rebuilding state should apply the ordered keyed updates
rather than assume exactly one physical record per key. Null values and null keys
have different meanings, and an empty string is not a tombstone. The workshop
uses ordinary string updates for the actual compacted-policy check and discusses
tombstones without claiming an unimplemented physical-cleaner experiment.

Payload schema is another contract. Kafka transports bytes and does not infer
that amount must be an integer merely because one producer intended it. A schema
registry is a separate service and compatibility policy. This project includes
a small local application validator, explicitly labeled as such, with no claim
that a registry was deployed or that the broker enforces its rules.

## Worked case A: observe policy and reconstruct current state

The check-retention action creates one owned fixture topic with cleanup.policy=compact
and validates actual one-partition/RF1 metadata and effective policy through the
Kafka Admin API. It writes acct-1=v1, acct-1=v2 and acct-2=v3 only when the source
end offset is zero. A bounded KafkaConsumer then reads to the actual end position,
not to a requested physical-message count.

Offset 0 may be absent after valid compaction. Offsets 1 and 2 with exact latest
payloads must remain, source end offset stays 3, and the latest map must contain
acct-1=v2 and acct-2=v3. The reported source SHA256 binds the observation to the
exact fixture bytes. Both a three-record history and a compacted two-record
history are valid; duplicates, other positions or missing latest values fail
without resetting the topic.

That result is a state reconstruction, not proof of physical compaction. The
returned JSON deliberately reports physical_compaction_demonstrated=false. A real
cleaner qualification would need eligible closed segments, controlled configuration,
bounded observation of cleanup, offset-gap-aware reads and restart checks. The
active tiny fixture does not supply that evidence.

Compaction preserves offsets as positions rather than renumbering retained records
into a new contiguous sequence. Consumers must tolerate gaps. A long-lived
consumer can still need a full bootstrap or a retained state snapshot if required
history has disappeared. Decide whether a topic represents a replayable event
history or a changelog for current state before selecting its cleanup policy.

## Worked case B: additive evolution versus incompatible values

The check-schema action runs the checked-in local validator on actual JSON bytes.
An event with id and integer amount is accepted. Adding region is also accepted
because this reader deliberately ignores unknown fields. A string amount, Boolean
amount or missing required amount is rejected. Python's bool/int relationship is
handled explicitly so true is not silently accepted as one unit of money.

This defines one reader policy, not universal backward or forward compatibility.
Another reader might reject unknown fields, use a different default or require a
new field. Compatibility is relative to writer and reader schemas, serialization
format and policy. A registry can centralize checks but cannot choose the business
meaning of a field or repair a semantically wrong unit.

A schema migration should keep representative old and new payload fixtures and
exercise every important consumer. Removing a field because the newest producer
no longer needs it can still break an old reader. For money, timestamps and IDs,
record units, timezone and precision as well as machine types.

## Diagnosis and interview discussion

Inspect effective topic configuration, segment eligibility, cleaner progress,
consumer offsets and payload validation separately. Do not call a topic corrupted
because multiple versions of a key remain before cleaning. Do not fix a schema
error by dropping every unrecognized field without confirming that the reader's
business contract permits it.

**Interview discussion: is compaction a replacement for a database table?** It
provides a retained keyed log useful for rebuilding state, but query indexes,
transactions, serving latency and erasure policies still need explicit design.
The two cases show real broker policy and log observations alongside a distinctly
local reader-validation example, without inventing a deployed schema registry or
claiming that physical deletion has already happened.
