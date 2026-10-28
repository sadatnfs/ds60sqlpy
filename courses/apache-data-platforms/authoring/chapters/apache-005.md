## Partitioning is a placement rule

A partition assigns each record to one subset of a dataset. The assignment might
use a range of dates, a hash of a customer identifier, or an explicit routing
value. A partition is not automatically a CPU thread, an Arrow chunk, a Parquet
row group or a machine. Those objects can be related by an execution plan, but
they have different ownership and lifetime. Always name which partitioning layer
you mean when explaining performance or ordering.

For a stable key, a hash partitioner computes a bucket using
\(p(k)=h(k)\bmod P\), where \(P\) is the partition count. The same key reaches
the same bucket only while the hash function, key encoding and partition count
remain unchanged. Python's built-in string hash is deliberately process-dependent;
this example therefore uses a documented SHA256 byte encoding. That choice is a
teaching fixture, not a claim to reproduce Kafka's producer partitioner or a
particular engine's internal hash implementation.

Ordering is generally local to a stream or partition. An aggregation can merge
partial sums without recovering source order, while an ordered sequence analysis
needs an explicit ordering key and tie rule. A shuffle redistributes records to
make records with the same grouping key available together. Its costs include
serialization, network transfer, buffering, file writes and scheduling barriers,
not merely the arithmetic performed after grouping.

## Worked case A: balanced independent keys

The first case creates 200 distinct customer keys and assigns them to four buckets.
The program reports the observed bucket sizes, checks that all records were placed
exactly once and verifies that repeating the function yields the same assignment.
It does not demand exactly 50 records per bucket: a hash distributes finite samples
with variation. An assertion of perfect balance would confuse an expectation
with a deterministic guarantee.

A grouped total is computed both from the original records and by merging the
per-partition totals. Equality provides a correctness oracle for this associative
operation. If the computation were an average, each partition would need to send
both its sum and its count. Averaging partition means with equal weights is wrong
when partition sizes differ. For a median, the mergeable state is more complicated
still; the choice of aggregate changes the exchange contract.

The useful observation is the actual count distribution, together with exact
record conservation. A tiny workload cannot establish throughput scaling. Four
logical buckets in one Python process demonstrate placement and merge semantics,
not a four-node cluster or parallel execution.

## Worked case B: a single hot customer

The second case sends 180 events for one customer and another 20 events for distinct
customers. Every event for the hot customer reaches one bucket. Increasing the
number of buckets does not split that key under an ordinary key partitioner. The
largest bucket therefore contains at least 180 events, even if the other events
are otherwise well distributed.

A simplified parallel lower bound is \(T\geq\max_i W_i/r_i\), with work
\(W_i\) and processing rate \(r_i\) for partition \(i\). This explains why
idle workers do not eliminate one oversized stateful group. It is a model of
work allocation, not a measured execution time. Real runtimes add network and
coordination costs and can change the physical plan.

Salting splits a hot key into temporary subkeys for a mergeable aggregate, then
combines its partial results. The program demonstrates this with integer sums.
It cannot be applied blindly to order-dependent state or distinct-user counts.
Changing key identity without the second aggregation would change the question
and produce several customer totals instead of one.

## Diagnosis and interview discussion

Measure rows, bytes, state size and task time, because equal row counts can hide
large variable-width payloads. Inspect a heavy-hitter distribution before selecting
a mitigation. Range partitioning, broadcast joins, preaggregation and salting solve
different problems and each carries its own limits. More partitions also produce
more metadata and scheduling work, so they are not a universal improvement.

**Interview discussion: why does doubling workers sometimes leave a query almost
unchanged?** A hot key, serial stage, shared I/O limit or coordination overhead can
dominate elapsed time. This program isolates the hot-key explanation, proves exact
sum conservation, and reports partition sizes. A real performance diagnosis must
then inspect the engine's actual task metrics rather than infer its bottleneck
from this placement model alone.
