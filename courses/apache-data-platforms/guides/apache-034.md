# apache-034: Producer acknowledgements and idempotence

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-033`, `apache-006`.

## Key terms

- **acks=all:** A producer setting under which the partition leader acknowledges a write after the in-sync replica requirement is met. On a one-broker topic it adds no redundancy.
- **In-sync replicas:** The replicas currently caught up with the partition leader. min.insync.replicas sets how many must acknowledge an acks=all write.
- **Idempotent producer:** A producer that uses a producer identifier and sequence numbers so brokers can suppress duplicates from its own supported retries. It does not deduplicate separate send calls.
- **Ambiguous outcome:** A send whose acknowledgement was lost, leaving the producer unable to know whether the record was appended.
- **Delivery timeout:** The bounded time a producer allows for a send, including retries, before reporting failure.

## An acknowledgement has a defined durability scope

A producer can wait for different acknowledgement conditions. With acks=all,
the partition leader waits for the in-sync replica requirement applicable to the
write. That requirement interacts with replication factor, current in-sync replicas
and min.insync.replicas. It does not mean every configured replica anywhere is
necessarily caught up, and it does not make a one-broker topic redundant.

An idempotent producer uses protocol-level producer identity and sequence tracking
to suppress duplicates caused by supported retries within that producer session
contract. It does not deduplicate arbitrary business requests forever. Two explicit
send calls are two records even when their keys and values are identical. A new
application request needs its own identity and destination-side semantics when
repeated business effects must be prevented.

The actual Java transaction probe configures idempotence, acks=all and bounded
request, delivery and blocking timeouts. It waits for real send futures and
transaction completion. This demonstrates the configured protocol path and its
observed results. It does not inject a dropped network acknowledgement or claim
to have measured retry deduplication under that failure.

## Worked case A: wait for a committed acknowledged write

The first transaction writes one synthetic order and commits. A read_committed
consumer later observes that order. The program waits for the send future before
committing, so a Java asynchronous call returning is not mistaken for durable
application completion. Errors remain errors and do not become a success message
merely because the producer object was created.

The probe's producer configuration states the delivery contract explicitly:

From [`projects/streaming/TransactionProbe.java`](../projects/streaming/TransactionProbe.java):

```java fragment
private static Properties producerProperties() {
  var properties = new Properties();
  properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
  properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
  properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
  properties.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
  properties.put(ProducerConfig.ACKS_CONFIG, "all");
  properties.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "ds60-workshop-transaction-writer");
  properties.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, "3000");
  properties.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "15000");
  properties.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, "10000");
  properties.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, "15000");
  return properties;
}
```

`acks=all` waits until every in-sync replica has the write; `enable.idempotence`
lets the broker discard a retried duplicate of the same producer sequence number;
and a `transactional.id` is required before the producer can use transactions.

The workshop has one broker and replication factor one. Therefore the observed
write and restart retention establish a local log boundary only. They do not
show that another broker can serve the data when this broker is unavailable.
To test replicated durability, a separate topology would need multiple native
brokers, an explicit in-sync policy and controlled failures with continued reads.

Producer buffering and batching also affect latency. A successful send future,
transaction commit and end-to-end consumer observation are different timing
boundaries. Any benchmark should name which one it measures. This fixture uses
small bounded messages for semantic checks, not a throughput competition.

## Worked case B: identical business data sent twice remains twice

The final transaction calls send twice with the same business key and payload.
Both writes commit and both are visible to a read_committed consumer. The oracle
expects two copies. Deleting one from the expected result would incorrectly teach
that idempotence is content-based business deduplication.

Contrast this with the earlier SQLite idempotency lesson. There, a stable operation
identifier and payload digest were stored atomically with a business mutation.
Kafka's producer-level mechanism covers a different boundary. Combining the two
can be useful, but neither automatically commits an unrelated database effect or
an outbound email with the Kafka transaction.

If a send times out, the caller may not know whether the broker accepted it.
Blindly creating a new business operation and sending it again can create another
record. A robust design captures operation identity, distinguishes known failure
from unknown outcome, and reconciles the source and destination state before
replaying an irreversible effect. Retry count and backoff alone do not solve
that semantic problem.

## Diagnosis and interview discussion

Inspect delivery timeout, request timeout, buffer limits, producer metrics and
broker error category. A DNS failure, authorization rejection, oversized record
and unavailable replica condition need different remedies. Keep the actual
exception and never turn every producer error into an instruction to delete the
local topic or rebuild the image.

**Interview discussion: does enable.idempotence=true mean a customer cannot be
charged twice?** No. It covers a defined producer retry mechanism, while charging
is a business effect with its own identity and transaction boundary. The two cases
show one actual acknowledged commit and two intentionally distinct send calls,
with no invented network-failure qualification or cross-system exactly-once claim.

## Worked examples

### Configure an idempotent transactional producer

```java fragment
var properties = new Properties();
properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
properties.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
properties.put(ProducerConfig.ACKS_CONFIG, "all");
properties.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "ds60-workshop-transaction-writer");
properties.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, "3000");
properties.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "15000");
```

These lines come from the streaming project TransactionProbe.java. Idempotence lets the broker drop a resend of the same producer sequence number, and acks set to all makes the acknowledgement wait for the in-sync replicas, which is one replica in this single-broker workshop. The delivery timeout bounds how long a send can retry before its future fails. None of these settings recognizes two separate send calls with the same business key as duplicates.

### Read committed and uncommitted views of the topic

```bash
cd work/streaming
bash run.sh start
bash run.sh check-transactions
```

In an owned workshop, the check prints a JSON line with committed_records 3, uncommitted_records 4 and aborted_hidden true. The read_committed consumer sees order-1 plus two identical same-business-id records, while read_uncommitted also sees the aborted order-2 value. The two identical records are correct Kafka behavior: they came from two awaited send calls, so deduplicating them is the consumer's business rule, not a broker guarantee.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Actual acknowledged writes and distinct application calls

From the copied streaming workshop using its explicit binary route:

```bash
bash run.sh start
bash run.sh check-transactions
bash run.sh check-transactions
```

The fixed probe initializes only an empty fixture topic. It must preserve three
committed records, including two equal business-key/value records from two
separate send calls. Repeating the checker does not append the fixture again.

Read `TransactionProbe.java`: compare `enable.idempotence`, `acks`, delivery and
request deadlines, awaited futures, and transaction completion. These are actual
settings and observations. The probe does not inject network retries or claim
business-level deduplication. Use the earlier local transaction lesson to compare
that different boundary.

## Primary references

- [Kafka design and delivery contracts](https://kafka.apache.org/44/design/design/)
- [Kafka operations](https://kafka.apache.org/44/operations/)
