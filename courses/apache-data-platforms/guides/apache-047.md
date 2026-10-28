# apache-047: Keyed state and timers

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-046`, `apache-006`.

## Keyed state belongs to a key and an operator

A keyed operator partitions records by a declared key and exposes state scoped to
that key. A ValueState holding a running total for east is independent from the
value for west. The state also belongs to a particular operator identity, descriptor
name and serializer. A Java field containing a mutable map does not automatically
become managed Flink state or participate correctly in checkpoints and rescaling.

Event-time timers are scheduled against watermark progress. Processing-time timers
use the worker's clock. A timer can fire when its relevant clock passes its deadline;
merely sleeping in the client does not advance an event-time timer. Define whether
an inactivity rule means no recently observed event time or no wall-clock activity,
because those are different operational policies.

The project uses real ValueState and event-time TimerService calls in a keyed
process function. It retains a running total and the currently registered inactivity
deadline. Updating a key deletes its previous deadline and registers the new one.
This prevents an obsolete timer from reporting inactivity after a newer event
has extended the key's active interval.

## Worked case A: independent customer totals

The controlled source delivers two east amounts 4 and 7 and one west amount 9 before
advancing its watermark. The keyed operator reports east totals 4 then 11 and west
total 9, preserving record identifiers for traceability. The checker evaluates each
key's state separately rather than treating an interleaving of different keys as
one globally ordered account history.

The operator uses a stable state descriptor and explicit types. Flink can snapshot
that managed state and move key groups under a compatible rescale. A plain static
variable would instead belong to one JVM/classloader and could leak or disappear
across task attempts. Managed state is an execution contract, not a convenient
synonym for any mutable object in a function.

The fixture includes a late record after its declared progress boundary. This
stateful function rejects that old event explicitly before updating state. A
KeyedProcessFunction does not automatically apply the window operator's lateness
policy, so copying a window example's assumptions into a different operator would
be incorrect. The chosen behavior is visible in the source and separate output.

## Worked case B: replace a timer, then fire it through a watermark

An east event at 1000 registers an inactivity deadline 1500. A newer event at 1500
replaces it with 2000. The west event at 500 has its own deadline 1000. When the
source advances watermark 2000, the real timers report west total 9 and east total 11
under their own deadlines. The operator clears their totals after emitting the
inactivity observations.

A subsequent east event at 2500 therefore starts a fresh total 3, with deadline 3000.
Watermark4000 fires that timer. The checker expects the fresh total rather than 14,
which would reveal that the prior inactive state was accidentally retained. It
also ensures the obsolete east 1500 timer did not create an extra observation.

A processing-time timer would need an actual clock-based experiment and different
expectations. This chapter does not label deterministic watermark control as a
measurement of wall-clock idleness. In a real application, timestamp quality,
partition idleness and late corrections can all influence the business meaning
of an inactivity event.

## Diagnosis and interview discussion

Name the key, state descriptor, operator UID, timer clock and cleanup policy.
Inspect whether a missing timer is waiting for watermark progress or whether it
was deleted by a later record. Treat state retention and timer retention together:
clearing one without the other can create stale callbacks or unbounded state.
A snapshot of one tiny state fixture does not prove every serializer migration.

**Interview discussion: why store the active timer timestamp in managed state?**
It lets the operator replace or recognize the currently intended deadline for
that key and recover the same policy with its state. These two cases exercise
actual per-key totals, deadline replacement, watermark-triggered callbacks and
cleanup, exposing errors that a single final aggregate would miss.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Managed keyed state and actual event-time timers

```bash
bash run.sh state
bash run.sh readback
```

Compare running totals, inactivity deadlines, cleared state and late output against
the complete fixture oracle. The old east deadline is replaced; a later east
activity starts fresh after the timer cleared state. Ordering across different
keys is not assumed. The same explicit timeline is used to make event-time progress
observable without claiming a wall-clock inactivity experiment.

## Primary references

- [Flink managed state](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/fault-tolerance/state/)
- [Flink process functions and timers](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/operators/process_function/)
