# apache-048: Checkpoints and end-to-end guarantees

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-047`, `apache-036`.

## A checkpoint is a consistent recovery boundary

Flink checkpoints coordinated operator and source state so a job can recover from
a consistent point. A source must be able to restore its position, managed state
must use compatible serializers and the sink must participate in the intended
commit protocol. A completed checkpoint is therefore more than a copy of one
Java object's fields, but it is not a transaction over every external action a
function might perform.

Checkpoint barriers identify a consistent cut through the graph. Alignment and
unifying the relevant input positions can affect latency, buffering and backpressure.
Unaligned checkpoint modes trade different state and operational costs; enabling
a setting does not by itself prove a recovery guarantee. Begin with the actual
selected mode and inspect completed checkpoint metadata and retained files.

The workshop's recovery path uses a bounded, paced source, stable operator/state
identities and a prepared local file sink. Its acceptance ledger states whether
the checkpoint and interruption route was actually exercised. A configured directory
or a successful job without a completed checkpoint cannot satisfy that gate.

## Worked case A: recover source position and managed totals

The checkpoint case processes identified integer records with a managed running
sum and a checkpoint-aware sink. Its source and expected final record set are
finite, so the checker can require every identifier exactly once and reconcile
the final total independently. It observes a real completed checkpoint before
interrupting the owned TaskManager.

After the explicit TaskManager restart, the job's recovery evidence must identify
an actual restored checkpoint, not merely a new successful run. The final sink
readback must preserve the expected source population and total. A request ID,
job ID, checkpoint ID, source identity and output identity have different roles
and are recorded separately.

This topology can be unavailable during the sole TaskManager's interruption. Correct
state recovery does not imply continuous availability. Likewise, retaining an
application receipt does not prove JobManager high availability. The project uses
a single JobManager and does not hide that boundary behind the word cluster.

## Worked case B: distinguish a transactional sink from an external effect

The existing Kafka transaction workshop gives a real independent visibility
example: committed readers see three data records while uncommitted readers also
see an aborted fourth. That is evidence for its Kafka transaction boundary.
It is not proof that an arbitrary Flink function calling an HTTP endpoint has
exactly-once effects, nor that the Kafka fixture automatically participates in
this Flink checkpoint.

A proper Flink Kafka sink route needs a released compatible connector, transactional
identity policy, checkpoint integration, transaction timeout and actual recovery
readback at the destination. It is a separately prepared integration, not a JAR
silently fetched while reading this chapter. The project documents that boundary
and does not relabel a local file-sink result as Kafka-sink qualification.

A nontransactional side effect can occur before a task fails and be repeated after
recovery. An idempotent destination operation keyed by a stable business identifier
can make repeated attempts safe, but it is an application contract outside a
checkpoint's automatic coverage. State which source, state and sink effects are
included before using an exactly-once claim.

## Diagnosis and interview discussion

Inspect checkpoint completion, source position, operator state, sink commits and
actual restored metadata. Bound retry and recovery waits, preserve a failed or
unknown outcome, and do not silently resubmit an old job as a new one to make the
example appear successful. A retained checkpoint can become unusable if referenced
files or compatible code are removed.

**Interview discussion: does enabling checkpointing make every pipeline exactly
once?** No. The source, state and destination must support the required recovery
and commit behavior, while outside side effects need their own protection. These
cases connect a concrete recovery experiment to a separately observed Kafka
transaction and explain why the two guarantees cannot be combined by assumption.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Checkpoint recovery and bounded guarantee claims

```bash
bash run.sh checkpoint
bash run.sh readback
```

The checkpoint route must observe completion before interruption, identify an
actual restoration and reconcile all final IDs and state. Read the qualification
ledger for the precise exercised topology.

For the independent real Kafka transaction observation, use its separately copied
workshop after stopping this pack:

```bash
bash run.sh stop
```

The Kafka project's `check-transactions` result is not a Flink Kafka-sink receipt.
The compatible connector/sink preparation and recovery boundary are documented
separately; no package is fetched by opening this lesson.

## Primary references

- [Flink checkpointing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/fault-tolerance/checkpointing/)
- [Flink fault tolerance concepts](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/learn-flink/fault_tolerance/)
- [Kafka transaction design](https://kafka.apache.org/44/design/design/)
