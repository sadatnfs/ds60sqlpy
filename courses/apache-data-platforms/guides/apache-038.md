# apache-038: KRaft, networking and operations

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-033`, `apache-035`, `apache-036`.

## Metadata and data listeners have operational responsibilities

KRaft uses Kafka's own metadata quorum mechanism instead of requiring ZooKeeper.
Controller roles manage cluster metadata, while broker roles serve partition data.
A production topology needs deliberate role placement, quorum membership, failure
domains and capacity. The teaching project combines one controller and one broker
in one process to make the mechanism accessible within a bounded local machine.
It does not provide high availability.

A bootstrap address is only the first connection. The client receives metadata
that identifies partition leaders and their advertised endpoints. If the broker
advertises localhost to a client in another container, that client may connect
to itself after a successful initial bootstrap. Internal service names and any
host-facing listener must therefore be configured consistently for their intended
network namespaces.

The workshop advertises kafka:9092 inside its owned private Compose network and
publishes no host ports. Its saved cluster identity is separate from container
identity and image identity. Kafka's retained metadata and log volume must agree
with that cluster identity; the startup script refuses a mismatched existing
volume rather than automatically formatting it.

## Worked case A: inspect a bounded single-node cluster

Start the copied owned workshop and run status, logs and check. The official CLI
creates a valid two-partition, one-replica topic and verifies exact keyed records.
It also attempts a topic with replication factor two. The real broker rejects it
because only one broker is available, and the checker inspects the intended
InvalidReplicationFactor diagnostic rather than accepting any nonzero exit.

A separate missing-topic request must also fail with its expected diagnostic.
These checks distinguish broker policy from a failed executable, broken DNS or
an unreachable listener. A test that passes whenever a command fails would be
weak evidence because almost any installation problem could satisfy it.

The service has a 1 GiB container memory limit and 512 MiB JVM heap, plus a bounded
process count and CPU allocation. Heap size does not equal total process memory:
native buffers, threads, page cache and runtime overhead remain relevant. These
settings make the local fixture manageable, not a sizing recommendation for a
production event pipeline.

## Worked case B: resume a process, then replace its container

Stop and resume must reuse the exact retained broker container and local image.
The launcher does not pull or build during resume. After readback, down removes
the owned container and network while retaining its named volume. Start creates
a different container over the same volume, checks the saved cluster identity and
reads the same committed records.

The qualified result distinguishes same-container resume from retained-volume
replacement. Neither proves service availability during the stop, broker replication,
controller failover or survival of a destroyed Docker volume. A single-node outage
is expected to interrupt requests. The project preserves data for recovery rather
than hiding that interruption behind an unsupported availability claim.

Images contain software, the named volume contains Kafka state, and the copied
.env identifies the workshop and its chosen image provenance. Moving just the
source directory to a different engine does not move the volume. Backup and
migration require a separate data-transfer procedure with consistency and restore
checks. Never run a global prune while expecting old state to remain.

## Diagnosis and interview discussion

Check engine health, resource pressure, volume identity, controller/broker logs,
listener metadata, topic state and consumer lag in a useful order. A Docker storage
snapshot error before the service starts is an engine-state problem, not evidence
that the lesson's Kafka code failed. Preserve the real diagnostic and source state
before changing layers.

**Interview discussion: what survives a container replacement?** Only data placed
in retained external state and configuration that correctly reconnects to it.
The two cases prove actual broker policy and local state recovery, while explicitly
excluding replication and high availability from this one-process topology.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Actual local operations and retained log state

```bash
bash run.sh status
bash run.sh logs
bash run.sh check
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
```

Resume must reuse the retained container. Replacement after down/start must keep
the three source records and saved cluster identity. The startup path refuses
mismatched persisted metadata rather than automatically formatting it.

```bash
bash run.sh down
```

This retains data. Only after deciding that this owned fixture is no longer needed:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

The launcher validates resource ownership and never runs global prune. A retained
volume is not replicated storage or a backup on another machine.

## Primary references

- [Kafka design and delivery contracts](https://kafka.apache.org/44/design/design/)
- [Kafka operations](https://kafka.apache.org/44/operations/)
