## Orchestration intervals and event time describe different clocks

Airflow schedules and tracks workflow runs over defined logical intervals. A
stream processor reasons about event timestamps, watermarks and continuously
arriving records. A historical backfill and a live stream can therefore operate
on overlapping business dates while following different execution clocks.
Naming both a daily job does not make their boundaries equivalent.

The actual Airflow workshop teaches explicit interval behavior and idempotent
publication. Kafka/Flink examples teach retained positions and event-time state.
Combining them requires an explicit output ownership and cutover policy. A
backfill must not silently overwrite the live producer's current output or
consume its state as though both writers were one atomic operation.

Use half-open intervals such as \([a,b)\) when defining a batch's intended
coverage, and state timezone and timestamp unit. Events exactly at a boundary
must belong to one selected interval. Wall-clock task start, logical data interval
and the latest event timestamp are different fields in a reproducible receipt.

## Worked case A: correct one historical partition

Choose a known historical UTC day and a bounded three-order input snapshot.
Trigger the actual owned Airflow workflow with the intended interval and source
identity. Write its candidate output to a separate owned location, compare exact
IDs and regional totals, then use an explicit publication step for that day.
Keep the previous accepted output recoverable until the new result is verified.

A retry should reconcile a known candidate or published identity rather than
blindly appending the same batch again. Capture workflow/run/task identity,
source revision, logical interval, attempt and output identity. A task can fail
after publishing its output but before saving a receipt, so a failed status alone
is not proof that no external effect occurred.

The course's actual Airflow timetable correction demonstrates why interval
readback matters: a shorthand schedule assumption can differ from the intended
coverage. Always inspect the actual selected interval in the running release.
Do not manufacture an expected date range from the trigger timestamp after the
workflow has already produced data.

## Worked case B: keep the live path independently owned

While the historical correction is prepared, the live path continues to consume
new events under its own source positions and state. Use separate candidate
outputs or an explicit table commit protocol so the backfill does not reset
consumer offsets, checkpoint directories or serving segments. Record which writer
owns each publication boundary.

A late event for the corrected day can arrive after backfill acceptance. Decide
whether it creates a later correction, enters a late-data queue or is excluded
by a closed-period policy. That is a business completeness decision, not something
Airflow's schedule or Flink's watermark can determine universally.

If a serving table combines historical and fresh data, define the actual time
boundary and verify no gap or overlap around the cutover. Test an event exactly
at the boundary and a delayed correction. Equal aggregate totals can hide a
missing event canceled by a duplicate, so keep identity-level reconciliation.

## Diagnosis and interview discussion

Compare logical interval, input snapshot, event timestamps, writer ownership,
publication identity and live source positions. Distinguish task retry from event
replay and distinguish both from an intentional correction. Preserve unknown
publication outcomes for read-only reconciliation instead of immediately rerunning
a writer.

**Interview discussion: why is a backfill not simply restarting the live stream
from yesterday?** It can use different bounded inputs, publication rules and
business correction semantics, while the live stream retains independent state.
These cases correct one historical partition and keep continuous processing
separate until an explicit reconciled cutover joins their outputs.
