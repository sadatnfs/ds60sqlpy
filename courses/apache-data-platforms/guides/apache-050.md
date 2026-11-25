# apache-050: Savepoints and schema evolution

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-048`, `apache-049`.

## Key terms

- **Savepoint:** An operator-triggered, explicitly managed snapshot of job state used for planned stops, upgrades and restores.
- **Operator UID:** A stable identifier assigned to a stateful operator so a savepoint's state maps to the same operator after the job graph changes.
- **Serializer compatibility:** Whether a new job version can read state written by an earlier serializer. An incompatible change prevents restoring that state.
- **Restore mode:** Whether a job restored from a savepoint claims ownership of its files or only reads them, which decides who may delete them.
- **Rollback:** Restoring the previous application version from a retained savepoint after a failed upgrade.

## A savepoint is an explicit state migration input

A savepoint captures application state for an operator-controlled stop, restore
or upgrade. Its usefulness depends on stable operator identity, compatible state
names and serializers, source position and the availability of referenced files.
Keeping a directory named savepoint is not enough to prove the application can
restore from it.

Checkpoints primarily support automated recovery under a selected job/runtime
policy, while savepoints provide an explicitly managed state point for planned
operations. Their ownership and retention rules can differ by format and restore
mode. A production upgrade plan must state who may dispose of them and whether
a restored job claims or merely reads the prior state.

The project gives its stateful operators stable UIDs and retains source, sink,
state metadata and observations in separately named owned locations. Its CLI
accepts only the known fixture route and validates any returned savepoint path
inside the owned state namespace. It does not pass arbitrary host paths or user
shell expressions through a manifest.

## Worked case A: stop and restore compatible state

The savepoint route starts a paced finite job, observes actual progress and
requests an explicit stop with a savepoint. The client records the completed
savepoint path and job identity. The compatible restore uses the same stateful
operator UID and state contract, optionally changing the declared parallelism
within the prepared allocation.

The final checker requires the complete expected source-ID set and independent
final total. A source starting again at zero could duplicate records, while a
counter restoring without its source position could produce inconsistent totals.
The sink's retained files and commit state must be interpreted together with the
source and managed state, not inspected as unrelated artifacts.

A stopped job can leave in-progress sink files that are part of its recovery
contract. Deleting them as apparently temporary cleanup can invalidate a savepoint.
Only the project's explicit state-aware cleanup path should remove owned files
after the experiment is complete. A restart of Docker containers is not an
instruction to discard those bytes.

## Worked case B: reject an incompatible operator identity

The negative restore case changes the stateful counter's UID while retaining the
same saved state and leaves non-restored-state permission disabled. The actual
restore must report an operator/state mapping failure. The checker inspects that
specific diagnostic and verifies that prior retained output was not reset or
replaced just to make the new job run.

The only source difference between the compatible and incompatible restore is the
operator UID chosen in the job's final branch:

From [`projects/flink/src/WorkshopJobs.java`](../projects/flink/src/WorkshopJobs.java):

```java fragment
.map(new ManagedTotal())
.name("checkpointed-total")
.uid(mode.equals("changed-uid") ? "counter-v2" : "counter-v1");
```

Savepoint state is mapped to operators by UID, so state saved under `counter-v1`
has no destination when the restored job names the operator `counter-v2`.

An unknown or failed restore is not automatically retried as a fresh empty-state
job. Doing so would turn a migration failure into data loss that looks like
success. The operator must decide whether the change is a deliberate state reset,
a supported migration or an error, then record the choice and its consequences.
This tutorial's negative case is an error demonstration, not permission to drop
state.

Schema evolution can be subtler than changing a UID. A field type, serializer,
key definition or maximum-parallelism change can affect compatibility even when
class names remain the same. The small long-valued state fixture establishes its
own compatible and incompatible paths. It does not qualify every custom serializer
or arbitrary version upgrade.

## Diagnosis and interview discussion

Record old/new code identity, runtime versions, operator UIDs, state descriptors,
serializer assumptions, source/sink capabilities and the exact retained state point.
Plan rollback before changing the only usable state. Preserve an independent
copy or appropriate ownership mode when a restore can alter referenced files,
and never delete unrelated volumes to free space for an upgrade.

**Interview discussion: why is an upgrade a state migration rather than just a
new JAR?** Stateful behavior depends on how old bytes map to the new graph and
its source/sink contracts. These two cases make a compatible restore and a deliberate
mapping rejection observable, then define which additional evidence would be
needed for a different serializer, runtime release or production topology.

## Worked examples

### Stop with a savepoint into owned storage

```bash
flink stop -p file:///state/savepoints "$JOB_ID"
```

This is the command workshop.py issues inside the JobManager container, with JOB_ID holding the running job's ID. A successful stop prints a path such as /state/savepoints/savepoint-<id>, and the workshop refuses to continue unless that directory exists, sits directly under the owned savepoints folder and is not a symlink. Stop differs from cancel: stop drains the sources and writes a consistent state point before the job ends, while cancel leaves only whatever checkpoint happened to complete last. If the log shows a timeout instead of a path, the job keeps running and no state point exists, so do not delete anything or resubmit yet.

### Why a changed operator UID cannot restore

```java fragment
.keyBy(value -> "all")
.map(new ManagedTotal())
.name("checkpointed-total")
.uid("checkpointed-total");
```

Savepoint state is stored by operator UID, not by class name or position in the graph. The changed-uid mode in the project submits the same logic under a different UID, and Flink then reports that it cannot map checkpoint or savepoint state to any operator. The workshop treats that failure as the expected result and does not pass allowNonRestoredState, because that flag would let the job start with an empty running total. Set explicit UIDs on every stateful operator before the first production savepoint; adding them later is itself a breaking change for existing state.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Explicit state points and a negative mapping case

```bash
bash run.sh savepoint
bash run.sh readback
```

The route records an actual completed state point, checks the deliberately changed
UID failure without allowing dropped state, and restores the compatible program.
Only a verified owned savepoint path can be selected. Prior outputs and source
identities are retained during diagnosis.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh readback
```

Container resume and savepoint restore are different operations. Readback never
silently starts a job. See the complete project ledger for what was actually
qualified and which external transactional-sink or HA routes remain separate.

## Primary references

- [Flink savepoints](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/state/savepoints/)
- [Flink state schema evolution](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/fault-tolerance/serialization/schema_evolution/)
