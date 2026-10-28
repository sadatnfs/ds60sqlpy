## Design the access pattern before choosing a primary key

Cassandra is a distributed wide-column database whose useful query shapes follow
its partition and clustering keys. CQL resembles SQL, but that resemblance does
not give it arbitrary joins or the cost model of a relational analytical engine.
Start with a concrete question, expected result size, update pattern and latency
requirement. Then choose a table that can answer that question with bounded work.
It is common to maintain more than one denormalized table for different questions.

The example asks for one customer's orders within one UTC day, newest first.
Its primary key is `((customer_id, day_bucket), ordered_at, order_id)`. The inner
parentheses identify the composite partition key. The remaining columns are
clustering columns that order rows within that partition. The order identifier
breaks ties between orders with the same timestamp; two real purchases must not
collapse into one row merely because their timestamps happen to match.

A day bucket is a deliberate application value, not automatically inferred from
a timestamp. Its timezone and boundary rule must agree between writers and
readers. For this fixture, event timestamps and bucket dates use UTC. A customer's
local business calendar could require a different rule. Changing the rule without
migrating existing data creates a different partition identity and can make old
orders appear missing.

## Worked case A: a bounded customer-and-day lookup

The real project creates a keyspace using NetworkTopologyStrategy with one replica
in the known local datacenter. It inserts three synthetic orders only when the
fixture is empty. Two belong to alpha on the same day and one belongs to beta.
The query supplies both partition-key fields and returns alpha's orders in
clustering order: order 3 before order 1, with amounts 7 and 4.

This result is local to that selected partition. It is not a global ordering of
every customer's orders. Asking for a month may require up to the month's daily
buckets and an application-level merge or a different table design. Query fanout
is therefore part of the access contract, even when every individual partition
lookup is efficient.

A rough sizing model is \(B\approx\lambda Hs\), with arrival rate
\(\lambda\), bucket duration \(H\) and average stored bytes per event \(s\).
It helps compare bucket choices, but average rate can hide a hot customer and
variable-width payloads. Measure large and unusually active partitions rather
than choosing a bucket size solely from the overall table average.

The checker verifies exact retained row identities and values before proceeding.
It never overwrites unexpected existing orders to make the example pass. Stable
primary-key upserts are useful, but blindly applying them could hide a learner's
changed fixture or a partially completed previous run.

## Worked case B: an unindexed ad hoc filter is rejected

A query selecting amount 7 without the required partition key has a different
access shape. The unindexed fixture rejects that request rather than pretending
it is a cheap point lookup. The client checks the actual filtering diagnostic,
so an unrelated network or syntax failure cannot satisfy this negative case.

Adding ALLOW FILTERING is not a general performance fix. It can authorize work
whose cost depends on how much data must be examined instead of the small number
of rows returned. On a three-row fixture that cost is invisible; on a large
cluster it can create substantial fanout and load. An index or a separate query
specific table should be evaluated against actual selectivity and workload.

Denormalization moves responsibility to writers. If the same business operation
updates a customer view and a day view, the application needs explicit failure,
idempotency and reconciliation behavior. Cassandra does not turn those independent
writes into a relational transaction just because both tables describe orders.
Choose the consistency boundary that the business actually needs.

## Diagnosis and interview discussion

Inspect the complete primary-key definition, supplied partition fields, clustering
restrictions and estimated fanout before changing concurrency. A missing day
bucket is a routing mismatch, not evidence that the row was deleted. Keep time
units, key encoding and tie rules consistent across language clients.

**Interview discussion: why might a normalized relational schema be a poor direct
translation into Cassandra?** Efficient access depends on the partition/query
relationship, and arbitrary joins are not the intended lookup mechanism. These
cases demonstrate a real bounded partition read and a real rejection of an
unapproved access shape, while explaining the write-side obligations that a
query-first design introduces.
