# apache-055: Transactions, indexes and drivers

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-054`, `apache-051`.

## Conditional invariants and indexed access solve different problems

An ordinary upsert resolves stored versions under the database's write rules.
A lightweight transaction adds a conditional comparison, such as changing an
inventory value only if it still equals the value a caller observed. Cassandra
uses a consensus protocol for the relevant conditional state. That is more
coordination than a normal write and should be chosen for a specific invariant,
not enabled indiscriminately as a generic performance setting.

Serial consistency and ordinary read/write consistency describe different parts
of the operation. A successful conditional mutation does not automatically make
all later unrelated reads, tables or external effects one atomic workflow.
The application still needs to identify which partition and business transition
are protected. Decrementing stock, charging a payment system and sending an email
are separate effects unless another explicit design coordinates them.

An index instead creates an access path for a predicate. Cassandra 5's Storage
Attached Index can support useful indexed queries, but its presence does not make
every predicate selective or remove distributed query costs. A query that matches
most of a large dataset can still be expensive. The lesson keeps conditional
correctness and indexed lookup as separate worked cases.

## Worked case A: accept one conditional update and reject stale state

The project initializes a dedicated synthetic inventory row with availability 7.
A conditional update changes it to 6 only if it is still 7. A second request with
the same stale condition must fail and report the current value 6. The independent
oracle checks both applied flags and the stored state; a normal unconditional
update would not satisfy the contract.

The checker conditionally restores the known probe value to 7 after the comparison
so the same bounded experiment can run again. It first rejects unexpected retained
inventory state rather than overwriting it. This controlled restoration belongs
to the synthetic fixture and is not a general instruction to reset a real stock
counter after a failed request.

A client timeout during a conditional operation can leave an unknown outcome.
Repeating a business effect requires reconciliation and stable operation identity,
not merely an assumption that an exception means the server did nothing. The
example checks known responses and does not inject or qualify every ambiguous
network-failure history.

## Worked case B: query an actual Storage Attached Index

A separate small indexed table preserves the unindexed modeling fixture's negative
case. Its amount index is created through the real CQL interface, and the client
waits for the bounded indexed lookup to become queryable. Selecting amount 7 must
return exactly the expected order identity. This confirms the prepared server's
actual index capability instead of inferring it from a version label.

The predicate matches one of three synthetic rows. That is a correctness fixture,
not a benchmark demonstrating production speed or cardinality estimation. Real
selectivity, partition distribution, returned bytes and concurrency affect cost.
Compare an index with a dedicated query-specific table using representative data
and explicit write/maintenance tradeoffs.

The Python driver prepares fixed inserts and binds values under a declared native
protocol version. Connection settings and request deadlines are explicit, while
packages are prepared at image build. A Java or Scala client can use the same
CQL contract with its own compatible driver, but the Python run does not qualify
a separate language client's dependency graph or API behavior.

## Diagnosis and interview discussion

Inspect conditional response state, requested consistency, index metadata, actual
queryability and driver exceptions separately. Do not replace a rejected CAS with
an unconditional update or add ALLOW FILTERING to conceal a missing access path.
Preserve the invariant and diagnose the reason for rejection.

**Interview discussion: when would you use a lightweight transaction rather than
an ordinary write?** When a defined conditional state transition requires its
coordination semantics and the workload can afford the cost. An index answers a
different question about access shape. The two cases demonstrate those boundaries
with real conditions and an actual indexed lookup rather than treating either
feature as a universal transaction or query optimizer.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Conditional state and actual SAI

```bash
bash run.sh check
```

The CQL client performs a known compare-and-set, checks `[applied]`, rejects a
stale comparison and conditionally restores only the known probe value. It
creates a real Storage Attached Index, waits for its queryability and compares
exact selective-query order identities against the independent fixture.

A conditional mutation protects the stated partition transition, not an external
payment, email or second table. A successful three-row index query establishes
API and result correctness; production selection requires cardinality, update,
latency, disk and memory measurements.

## Primary references

- [Cassandra 5 CQL data definition](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html)
- [Cassandra data guarantees](https://cassandra.apache.org/doc/5.0/cassandra/architecture/guarantees.html)
- [Cassandra backups](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/backups.html)
- [Cassandra Storage Attached Indexing](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/indexing/sai/sai-overview.html)
