# apache-052: Writes, SSTables and reads

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-051`.

## Key terms

- **Commitlog:** An append-only log on each node that records a write before it is applied in memory, so it can be replayed after a restart.
- **Memtable:** The mutable in-memory structure that holds recent writes for a table until it is flushed to disk.
- **SSTable:** An immutable sorted string table file written when a memtable flushes. Reads may merge several SSTables and the memtable.
- **Write timestamp:** The timestamp attached to each written cell. When versions of the same cell conflict, the one with the highest timestamp wins.
- **Bloom filter:** A per-SSTable probabilistic structure that can prove a partition key is absent but can return false positives, so a possible match still needs a read.

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

## Worked examples

### Competing writes with explicit timestamps

```sql
INSERT INTO ds60_orders.clocked (key, value)
VALUES ('demo', 'initial')
USING TIMESTAMP 1700000000000000;

UPDATE ds60_orders.clocked USING TIMESTAMP 1700000000000010
SET value = 'newest'
WHERE key = 'demo';

UPDATE ds60_orders.clocked USING TIMESTAMP 1700000000000005
SET value = 'stale'
WHERE key = 'demo';

SELECT value
FROM ds60_orders.clocked
WHERE key = 'demo';
```

The final SELECT returns newest even though stale was written last, because Cassandra resolves each cell by its write timestamp in microseconds and not by arrival order. This is why client clock skew matters: a writer whose clock runs ahead can silently win against later, correct updates. The client in the project raises an AssertionError if this rule ever changes, which makes the check repeatable after restarts.

### A clustering range inside one partition

```sql
SELECT
  order_id,
  amount
FROM
  ds60_orders.by_customer
WHERE
  customer_id = 'c1'
  AND day_bucket = '2026-01-01'
  AND ordered_at >= '2026-01-01 00:00:02';
```

The illustrative customer and day values follow the shape of the by_customer table, whose partition key is customer_id plus day_bucket and whose rows are ordered by ordered_at descending. The partition key routes the read to one replica set, and the clustering range then reads a contiguous slice inside that partition. Remove the partition key and Cassandra refuses the query unless ALLOW FILTERING is added, which turns a targeted read into a scan; that refusal is a design signal, not an error to suppress.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Storage and timestamp observations

```bash
bash run.sh check
bash run.sh identity
bash run.sh logs
```

The checker writes known competing cell versions with explicit microsecond
timestamps and independently requires the greatest-timestamp value. Its clustering
range selects order 3, while a full selected partition returns orders 3 and 1.
`identity` performs read-only retained-order inspection without initializing data.

To extend this observation, record actual nodetool metrics and SSTable metadata
around a controlled flush. A successful row read alone does not identify the
physical file that supplied it. Do not delete individual files to change a result.

## Primary references

- [Cassandra 5 CQL data definition](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html)
- [Cassandra data guarantees](https://cassandra.apache.org/doc/5.0/cassandra/architecture/guarantees.html)
- [Cassandra backups](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/backups.html)
- [Cassandra Storage Attached Indexing](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/indexing/sai/sai-overview.html)
