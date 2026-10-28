# apache-033: The log, topics and partitions

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-005`, `apache-004`.

## A log retains records independently from a reader

Kafka stores records in topic partitions. A partition is an ordered append-only
log whose offsets identify positions within that partition. There is no general
global order across every partition of a topic. A consumer reads positions and
can retain progress without destructively removing a record from the source.
That is why independent applications can replay the same topic for different
purposes.

A record can include a key, value, timestamp and headers. A producer's partition
selection determines where the record is appended. Using the same key often aims
to keep related events together, but that property depends on the actual producer
partitioning configuration and partition-count history. Do not substitute the
course's SHA256 placement model for Kafka's released partitioner implementation.
The real workshop checks resulting partition-local behavior and exact payloads.

The provided one-node KRaft topology has two data partitions and replication
factor one. It is a real broker and controller process with a persistent log,
but it has no redundant broker or controller quorum. The binary fallback uses
an official checksummed Kafka release on a prepared native Java image; it is
explicitly labeled as a locally built alternative to the upstream image.

## Worked case A: append and independently verify keyed records

Run the workshop's check command. It creates classroom-events only when absent
and writes three keyed synthetic orders only when the topic is empty. The client
reads through the official Kafka CLI and compares the exact key/value multiset
with a separate fixture file. It also checks that the sum of partition end offsets
is three for this nontransactional fixture.

Comparing a multiset is deliberate: partition-local order does not promise the
original interleaving across two partitions. Sorting only for the oracle does
not reorder the broker's log or create a global sequence. An application needing
business order should include a meaningful ordering key and define what happens
when related events arrive late or share a timestamp.

Running the check again must retain the same three records. This is idempotent
fixture initialization, not a test that Kafka discards two distinct application
send calls. Unexpected existing rows cause failure rather than an automatic topic
delete or reset. Preserving evidence makes an accidental duplicate visible instead
of hiding it behind a fresh empty topic.

## Worked case B: two independent consumer progress records

The explicit binary route includes a prepared JDK for compiling the real Java
consumer probe. That probe creates two uniquely named temporary consumer groups,
reads the same existing log, and compares their results. Group A can commit its
positions without removing records or advancing group B. The actual observation
is three source records available to both groups, with group A later resuming at
its committed end.

This probe uses manual assignment to the two known partitions. It therefore
establishes offset and independent-group behavior, not automatic partition
assignment or a rebalance experiment. Subscription-based consumer groups add a
coordinator and assignment protocol; their failure and membership transitions
require separate observations. A program should not claim it tested rebalancing
merely because its configuration contains a group ID.

The temporary group IDs are deleted after consumers close, while the source topic
and its records remain. The project launcher validates ownership before touching
containers, networks or volumes. No host SDK, cloud account or external Kafka
cluster is involved. All operations stay inside the copied owned local workshop.

## Diagnosis and interview discussion

Check bootstrap connectivity, advertised listeners, topic existence, partition
metadata and consumer positions separately. A successful bootstrap connection is
not enough if the broker advertises an unreachable address for later requests.
The workshop uses kafka:9092 inside its private Compose network and publishes no
host listener.

**Interview discussion: how does Kafka differ from a destructive queue?** Reading
and committing one group's progress does not remove a log record for another
group. Retention and compaction determine source availability independently from
a particular group's progress. The two cases demonstrate real keyed storage and
independent consumption while keeping partition ordering and single-node durability
claims precise.

The bounded reference topic explicitly retains its three source records without
time or byte expiration. The checker verifies the effective delete-only policy,
actual two-partition/RF1 metadata, source SHA256 and both partition end positions.
These positions total three and remain separate from ordering across partitions.
This prevents default retention from invalidating valid saved study state; it
does not justify infinite retention for an unbounded production source.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Real topic, keyed records and independent readers

Copy `projects/streaming` to a fresh owned directory and follow its README to
prepare either the pinned upstream image or explicit verified-binary route.

```bash
bash run.sh start --binary
bash run.sh check
bash run.sh check
bash run.sh check-consumers
```

The first two checks must retain exactly three keyed records across two partitions.
The Java probe must report uncommitted replay, zero records after group A's
committed resume, and three records for an independent group. It uses manual
assignment and makes no rebalance claim.

```bash
bash run.sh status
bash run.sh logs
```

`--binary` is only needed to select that route initially. A saved upstream route
cannot silently switch provenance. Consumer compilation needs the binary route's
prepared JDK; the ordinary CLI check also supports the official-image route.

## Primary references

- [Kafka design and delivery contracts](https://kafka.apache.org/44/design/design/)
- [Kafka operations](https://kafka.apache.org/44/operations/)
