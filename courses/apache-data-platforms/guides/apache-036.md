# apache-036: Transactions and isolation

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-034`, `apache-035`.

## A transaction groups specific Kafka operations

Kafka transactions let a producer write records across partitions and make their
committed visibility depend on one transaction outcome. A transactional producer
initializes its identity, begins a transaction, sends records, then commits or
aborts. Consumers choose an isolation level. A read_committed consumer excludes
aborted transactional data; a read_uncommitted consumer can observe records from
aborted transactions.

This guarantee has a defined scope. It does not automatically include a write to
an unrelated SQL database, an HTTP side effect, a file in a separate store or a
human's interpretation of a duplicate business operation. A consume-transform-produce
workflow can include consumer offsets in the Kafka transaction when implemented
with the appropriate APIs, but that is different from simply calling commitSync
on a separate consumer.

The project compiles and runs a real Java transactional client against the actual
owned broker. It uses one bounded topic, persistent transaction metadata and
independent readers with different isolation settings. The fixture's three
transaction outcomes are retained across checker invocations rather than recreated
by deleting the topic.

## Worked case A: commit one record and abort another

The first transaction writes committed-a and commits. The next writes aborted-b
and aborts. The read_committed reader must include the first and exclude the
second; the read_uncommitted reader must include both. The program compares exact
key/value lists, so an accidental empty topic cannot pass the visibility check.

Control records occupy log positions without being ordinary application records.
Therefore an end offset need not equal the number of data records a consumer
returns. The Java reader advances through the actual partition positions with a
deadline rather than assuming that reading a fixed offset range yields the same
number of visible payloads under every isolation level.

An open transaction can constrain how far a read_committed consumer safely reads.
This means observed lag or delayed visibility can involve transaction state, not
just slow network transfer. Diagnose producer transaction completion and broker
state before increasing consumer concurrency as a generic remedy.

## Worked case B: committed duplicates remain distinct operations

The third transaction contains two identical business-key/value send calls and
commits them both. The committed reader now sees three total records: committed-a
and both copies. The uncommitted reader sees four because it also includes the
aborted-b payload. These expected counts are derived from transaction outcomes,
not from a claim that identical content is automatically deduplicated.

The checker first inspects the retained topic's end offset. It initializes only
an empty fixture and otherwise validates existing evidence. An interrupted partial
initialization is rejected rather than silently overwritten. That design makes an
unexpected state visible, although a production transactional workflow would need
a more complete recovery and reconciliation procedure than this fixed fixture.

A stable transactional ID lets the broker coordinate producer epochs and fence
older conflicting instances under the protocol. It is not a license to have
unrelated applications share an ID casually. Define transactional identity and
ownership so one deployment does not accidentally fence another legitimate writer.
This single-client test does not inject and qualify a competing-epoch scenario.

## Diagnosis and interview discussion

Record transaction identity, outcome, isolation mode and the selected source
partitions. Keep visible data counts separate from physical offsets and control
records. Inspect actual exceptions and timeouts; do not interpret a failed client
invocation as an intentionally aborted transaction unless the broker and readback
support that conclusion.

**Interview discussion: what does Kafka exactly-once processing exclude?** It
excludes effects outside the transaction boundary unless another explicit design
coordinates them. These cases demonstrate real committed versus aborted visibility
and show why two independent business calls can remain twice even inside one
valid transaction. That evidence is strong enough to teach the mechanism without
claiming universal end-to-end atomicity.

The exact transaction fixture has explicit delete-only infinite time/byte retention,
validated through the actual Admin API before use. It cannot be compacted, because
its two distinct committed business send calls must remain two records. Log end
positions also include transaction-control records, so an end offset is not the
same quantity as the three/four data-record visibility counts.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Real transactional visibility

The prepared Java compile path uses the explicit binary workshop route.

```bash
bash run.sh check-transactions
```

Expected actual result: `committed_records:3`, `uncommitted_records:4`,
`aborted_hidden:true`, and two retained distinct duplicate business send calls.
The implementation checks exact payloads in addition to these counts.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check-transactions
```

The checker validates retained transaction evidence and does not append again.
Read the complete `TransactionProbe.java` source before modifying transaction
identity, isolation mode or offset handling. A different workload requires a
separately identified fixture, not deletion of unexpected retained data.

## Primary references

- [Kafka design and delivery contracts](https://kafka.apache.org/44/design/design/)
- [Kafka operations](https://kafka.apache.org/44/operations/)
