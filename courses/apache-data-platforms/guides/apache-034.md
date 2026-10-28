# apache-034: Producer acknowledgements and idempotence

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-033`, `apache-006`.

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
