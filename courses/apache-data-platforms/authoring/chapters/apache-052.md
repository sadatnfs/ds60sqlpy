## Follow the write path and the read path separately

Cassandra's storage engine combines a commitlog, mutable memory structures and
immutable sorted storage files called SSTables. A write can be recorded in the
commitlog and applied to a memtable before later flush produces SSTables.
Compaction merges selected immutable files and resolves versions according to
the storage engine's rules. It is a storage maintenance process, not a business
transaction or a promise that every old byte disappears immediately.

Reads can combine information from memtables and several SSTables. Bloom filters,
partition indexes, caches and clustering bounds reduce unnecessary work, but
none replaces a correct data model. A Bloom filter can rule out a file that does
not contain a key with a controlled false-positive possibility; a possible match
still needs verification. Do not describe it as an exact list of present rows.

An acknowledged write's durability also depends on the configured commitlog sync
policy and storage behavior. A successful application request, process restart,
VM failure and physical disk loss are different boundaries. The local fixture
checks observable state and retained-volume recovery; it does not claim that a
container memory limit or a zero exit code establishes power-loss durability.

## Worked case A: write timestamps determine a visible value

The project writes an initial value, then a newer value with an explicitly larger
microsecond write timestamp, then a later-arriving request with an intermediate
timestamp. The read still returns newest. This is actual CQL storage behavior;
the program does not sort a Python list and call it Cassandra conflict resolution.
Its independent oracle expects the value associated with the greatest supplied
timestamp in this controlled fixture.

Arrival order and write-timestamp order are therefore different concepts. Giving
a stale business event a large current timestamp can overwrite a logically newer
fact. Conversely, a client with a far-future clock can make subsequent valid
updates appear older for a long time. Use consistent timestamp ownership and
understand how the driver and server assign defaults before overriding them.

A last-write rule is not an application-level causal model. Two concurrent updates
can need conflict detection, a conditional invariant or a business reconciliation
policy. Do not assume that choosing the numerically greatest timestamp proves the
selected value reflects the latest real-world decision. The fixture makes the
mechanism visible without endorsing arbitrary client clock values.

## Worked case B: a clustering range narrows a known partition

The customer/day table stores ordered_at and order_id as clustering columns.
Supplying the full partition key locates the relevant partition; a compatible
timestamp range can then narrow which ordered rows are returned. The worked
fixture's later interval selects order 3 while the full selected partition returns
orders 3 and 1. The source checks both identities, not just a final amount total.

A query across many customers or day buckets changes the work pattern. A small
result does not imply a small scan, especially when an application fans out over
many partitions and filters after reading. The checker uses one bounded full-table
read only to validate its three-row synthetic fixture, and does not present that
validation convenience as a production serving query.

Physical storage state can change after flush or compaction while the logical
query result remains the same. To study those transitions, inspect actual node
metrics and SSTable metadata around a controlled operation. A row read alone does
not prove which file served it, and an SSTable count alone does not measure
application latency or correctness.

## Diagnosis and interview discussion

Record write timestamps, supplied consistency, partition identity, read bounds
and the node's commitlog/flush/compaction observations. Distinguish stale data from
a wrong partition key or timezone. Avoid broad cache or file deletion as a first
response to a surprising value; it can erase the evidence needed to explain it.

**Interview discussion: why can an older-arriving update remain invisible?** Its
write timestamp can lose to a later version already stored for the same cell.
That is different from a network failure or a missing partition. The two cases
connect actual timestamp resolution and bounded clustering access to the LSM
storage mechanisms, while keeping physical-file and failure-durability claims
separate from the observed logical results.
