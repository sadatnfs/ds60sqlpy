# apache-035: Consumers, offsets and rebalances

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-033`, `apache-006`.

## A consumer position and a committed offset are different state

A consumer advances its current position while fetching records. Its committed
offset records where a later consumer instance in that group should resume.
Committing offset n conventionally means the next record to read is n, not that
record n has just been processed. Every topic partition has its own offset space,
so one integer cannot describe progress through a multi-partition topic.

The order of effect and commit determines failure behavior. Processing a record
then committing can replay the effect if the process crashes between them.
Committing first can skip an effect if the process crashes afterward. At-least-once
processing therefore normally commits after a successful effect and makes that
effect idempotent or transactional within its intended boundary.

The real Java probe disables automatic commits, manually assigns the two known
fixture partitions and uses explicit bounded reads. This isolates offset behavior
without a timing-dependent membership experiment. Automatic subscription and
rebalancing are explained here as an additional mechanism, with no claim that
manual assignment exercises the coordinator's assignment transitions.

## Worked case A: close before committing and observe replay

Group A reads all three fixture records and closes without committing. A new
consumer with the same group ID reads them again. The oracle compares exact
key/value lists, rather than merely finding at least one row. The log retained
the records and the group had no committed progress that advanced past them.

Each read in the probe uses these consumer settings and this bounded loop:

From [`projects/streaming/ConsumerProbe.java`](../projects/streaming/ConsumerProbe.java):

```java
private static Properties settings(String group) {
  var p = new Properties();
  p.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
  p.put(ConsumerConfig.GROUP_ID_CONFIG, group);
  p.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
  p.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
  p.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
  p.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
  p.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG, "5000");
  p.put(ConsumerConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, "10000");
  p.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "10");
  p.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, "65536");
  p.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, "65536");
  return p;
}

private static List<String> read(String group, boolean commit) {
  var rows = new ArrayList<String>();
  try (var consumer = new KafkaConsumer<String, String>(settings(group))) {
    consumer.assign(PARTITIONS);
    var end = consumer.endOffsets(PARTITIONS, Duration.ofSeconds(10));
    long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
    while (true) {
      boolean complete = true;
      for (var partition : PARTITIONS) {
        complete &= consumer.position(partition, Duration.ofSeconds(5)) >= end.get(partition);
      }
      if (complete) {
        break;
      }
      if (System.nanoTime() >= deadline) {
        throw new IllegalStateException("Read deadline");
      }
      for (var record : consumer.poll(Duration.ofMillis(250))) {
        rows.add(record.key() + "|" + record.value());
        if (rows.size() > 3) {
          throw new IllegalStateException("Unexpected source records");
        }
      }
    }
    if (commit) {
      var offsets = new HashMap<TopicPartition, OffsetAndMetadata>();
      for (var partition : PARTITIONS) {
        offsets.put(partition, new OffsetAndMetadata(consumer.position(partition)));
      }
      consumer.commitSync(offsets, Duration.ofSeconds(10));
    }
  }
  Collections.sort(rows);
  return rows;
}
```

`enable.auto.commit=false` means that progress is recorded only by the explicit
`commitSync` call, and `auto.offset.reset=earliest` decides where a group with no
committed position starts. The committed value is the next position to read, not
the offset of the last record processed.

This resembles a process interruption before its commit, but the probe uses an
orderly close with auto-commit disabled to make the boundary deterministic. It
does not claim an injected kernel crash or a filesystem durability test. A real
application can use this semantic observation to predict which side effects need
deduplication when a less orderly interruption happens.

The fixture's topic retention is long enough for the replay. A lagging consumer
cannot assume every historical offset remains readable forever. If retention or
compaction removed required records, an offset-reset policy could change behavior.
A recovery runbook must distinguish available replay from a source gap.

## Worked case B: commit next positions and reopen

A third read in group A commits the final next position for each partition. A
new consumer in that group now returns zero fixture records. An independent group
B still receives all three, proving that the commit changed group progress rather
than destructively consuming the source. The probe then removes only its uniquely
created temporary group metadata.

In a subscription-based group, a rebalance can move partition ownership to another
member. A handler must stop applying effects for revoked partitions, complete or
abort in-flight work according to its design, and commit only offsets that
correspond to completed work. Cooperative protocols and newer group coordination
change details, but do not remove the need to track per-partition completion.

Parallel record handling makes the boundary subtler. If offsets 5 and 7 finish
while 6 is still running, committing 8 can skip unfinished work after a crash.
Track the contiguous completed prefix for each partition rather than the largest
observed completion. The tiny probe processes synchronously; it does not pretend
to test every concurrent worker scheduling condition.

## Diagnosis and interview discussion

Inspect assigned partitions, current positions, committed offsets, source end
offsets and retention bounds. Lag is an offset-distance signal with workload and
record-size caveats; it is not automatically a wall-clock delay in seconds.
Distinguish a stuck application from an idle partition and compare logs with
actual progress rather than resetting offsets as the first response.

**Interview discussion: when should a consumer commit?** After the intended effect
has succeeded under a defined idempotency or transaction contract, and only through
the contiguous completed positions. These two actual reads show replay before
commit and no replay after commit, while the text identifies the additional
membership and concurrency behavior that this bounded manual-assignment probe
has not qualified.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Replay and committed next offsets

```bash
bash run.sh check
bash run.sh check-consumers
```

Inspect `ConsumerProbe.java`: automatic commit is disabled; the first two consumer
instances read without committing; a later instance commits each partition's next
position; the following instance reads zero rows. A different group reads all
three rows. The code closes consumers before deleting only its unique probe group
IDs. The source topic and records remain.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh check-consumers
```

This is real Kafka offset behavior with manual assignment. It does not claim an
actual rebalance, broker replication, process-kill injection or external database
atomicity. Keep those evidence boundaries when writing a recovery report.

## Primary references

- [Kafka design and delivery contracts](https://kafka.apache.org/44/design/design/)
- [Kafka operations](https://kafka.apache.org/44/operations/)
