# apache-083: Orchestrated backfills and live data

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-032`, `apache-050`, `apache-081`.

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

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Integration apache-083 complete worked notebook

Use the actual Airflow project for one explicit historical interval. Publish a validated candidate separately from the live stream. Reconcile unknown publication outcomes before retrying any writer.

## Receipt fields and independent oracle

- Source revision/hashes and exact declared input IDs, values, schema and time units.
- Actual native platform, package/image identities and owned resource namespace.
- Selected table snapshot/version, source positions or process/lineage identity as appropriate.
- Positive result against an independent oracle and a typed negative observation.
- Read-only retained-state comparison after the selected lifecycle transition.
- Cleanup/evidence-storage result and any separate prepared or unavailable feature.

For the common three-order fixture, require IDs 1/2/3 with amounts 4/9/7, total 20,
east 11 and west 9. A later fourth west order of2changes current total to22 and west
to11while an earlier pinned snapshot remains unchanged. Do not use this simple
oracle to claim correctness for a different pipeline without defining its
deduplication, correction and visibility semantics.

Read the selected project README and qualification ledger before commands. The
classroom does not execute Docker commands in this Markdown pad. Prepared
configuration, unit policy fixtures, successful compilation and actual service
acceptance remain different observations. Never include credentials or signed URLs.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../airflow/README.md
cat ../airflow/dags/classroom_workflows.py
```

These inspections do not start or qualify a service. Execute only the chosen
project's complete documented owned route and retain its actual receipt.

## Primary references

- [Iceberg reliability and table state](https://iceberg.apache.org/docs/latest/reliability/)
- [Arrow data format](https://arrow.apache.org/docs/format/Columnar.html)
- [Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
- [Kafka delivery/transaction design](https://kafka.apache.org/44/design/design/)
- [Atlas API and metadata boundaries](https://atlas.apache.org/api/v2/index.html)
- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
