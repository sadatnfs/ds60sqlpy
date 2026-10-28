## A consistency level counts replicas in a topology

Replication factor states how many replicas store a partition under the configured
placement strategy. A consistency level states how many relevant replica responses
a read or write requires. They are related, but not interchangeable. ONE requires
one replica response; QUORUM requires a majority of the applicable replica set.
For replication factor \(N\), a simple quorum size is
\(\lfloor N/2\rfloor+1\). Datacenter-aware levels add a placement scope that
must be understood explicitly.

A one-node, one-replica example can execute both ONE and QUORUM, but both require
one response in that topology. Calling this a demonstration of replicated fault
tolerance would be misleading. The basic project therefore reports its RF1 limit
and requires failure for a read that asks for two replicas. The separately selected
three-node workshop is needed to observe actual replica availability tradeoffs.

The familiar overlap condition \(R+W>N\) explains why read and write replica
sets can intersect under a stated placement and failure model. It does not by
itself make every concurrent update linearizable, repair clock skew or turn a
collection of independent operations into a transaction. Timestamp resolution,
read repair, transient failures and the application's invariant still matter.

## Worked case A: identify the RF1 boundary honestly

The single-node fixture uses NetworkTopologyStrategy with one replica in its
known datacenter. Reads at ONE and QUORUM return the same two alpha orders.
The TWO-level read must fail with the actual insufficient-replica condition;
the client checks the required and available replica counts. An unrelated driver
exception does not count as the intended negative observation.

This is useful preparation for understanding consistency without requiring a
large local machine. It establishes the API and arithmetic boundary while
explicitly excluding replication. A stopped single node makes its service unavailable.
Retained data can support restart recovery, but cannot serve requests while its
only process is stopped.

The datacenter name is checked against system metadata rather than assumed from
a user's external cluster. This prevents a typo in a replication map from creating
a misleading fixture. The workshop is private and owned; none of these commands
should be redirected to a valuable shared Cassandra deployment.

## Worked case B: distinguish one surviving replica from a quorum

The optional replicated topology has three actual owned nodes and a separate
RF3 keyspace. A fixture write is completed while all replicas are available.
Two selected nodes are then stopped deliberately. A ONE read can still return
the known value from the surviving replica, while QUORUM cannot obtain the two
responses it requires. After the exact nodes resume, the quorum read is checked
again against the original value.

This test observes availability for one retained value under a controlled outage.
It does not establish every possible concurrent-write history, cross-datacenter
failure, network partition or hinted-handoff timing. The nodes share one Docker
engine and therefore one physical host failure domain. Three containers are not
three independent racks or regions.

The comparison is meaningful only if the first write's consistency and completion
are recorded. Writing weakly immediately before stopping a node can produce a
different experiment with ambiguous replica contents. The fixture must keep
source identity, response requirements, stopped node identities and recovered
readback in one evidence record.

## Diagnosis and interview discussion

Inspect replication placement, datacenter labels, live replicas, coordinator
errors and the requested level before changing a client's retry policy. A retry
cannot manufacture a missing quorum. Lowering consistency changes the contract
and needs a deliberate application decision rather than an automatic way to hide
a service failure.

**Interview discussion: when does QUORUM improve a design, and what does it cost?**
It requires more replica responses and useful overlap properties under a defined
model, while reducing availability when too few replicas can answer and potentially
increasing latency. These two cases separate the accessible RF1 arithmetic from
the actual optional multi-node outage observation instead of treating a successful
local read as a universal consistency proof.
