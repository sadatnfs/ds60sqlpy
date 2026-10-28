# apache-060: Time boundaries, hybrid tables and upserts

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-059`, `apache-057`.

## Historical and fresh data need an explicit boundary

A hybrid Pinot table combines OFFLINE and REALTIME tables under a shared logical
name. The broker uses a time boundary to divide which side contributes to a query.
This avoids simply summing all historical and fresh data when their time ranges
overlap. The timestamp column, bucket granularity, ingestion schedule and selected
boundary are therefore part of the result contract.

A boundary is not a general deduplication algorithm. An event with the same
business identity can still appear twice within one side, or fall outside the
assumptions used to divide historical and live coverage. Backfills and late
corrections require an explicit strategy for replacing or updating data while
preserving the intended historical meaning.

Upsert tables solve a different problem: choosing the current record for a
primary key according to a comparison column and configured behavior. They need
a declared primary key, ordering semantics and appropriate partitioning. The
standalone offline workshop does not demonstrate hybrid routing or upsert. The
following are prepared real-product experiments requiring their own owned data,
configuration and native receipts.

## Worked case A: divide an overlapping historical interval

Suppose the offline side contains orders through the end of day 1, while the
real-time side includes day 1 and day 2. A naive union would count overlapping
day-1 events twice. Configure and inspect the actual broker time boundary, then
query day 1, day 2 and the combined range against an independent identity ledger.
Use timestamp values whose unit and timezone are stated explicitly.

The oracle needs more than a combined total. Keep ID-to-time assignments and
expected contribution from each side. Verify that an event exactly at the
boundary contributes once under the actual inclusive/exclusive rules of the
pinned release. An off-by-one millisecond can hide when tests use only noon
values far from the dividing point.

If a backfill ends earlier than expected, moving the boundary without complete
coverage can omit data. If it advances into a region with uncommitted offline
segments, the broker may exclude valid real-time contributions before their
replacement is queryable. Treat boundary progression as a controlled publication
step with completeness and availability evidence.

## Worked case B: a later version changes current state

Use a separate prepared upsert table with order ID as primary key and an explicit
monotonic version column. Send ID 1 at version 1 with amount 4, then version 2
with amount 6, then a delayed version 1. The current-state oracle expects amount 6.
Record how the chosen configuration handles equal comparison values rather than
assuming arrival order resolves every tie.

An append-only analytical table would legitimately retain multiple events for
that sequence. Its sum answers a different question from the current-state upsert
table. Decide whether the application needs a changelog, a current snapshot or
both. Replacing events with current state can remove information required for
auditing historical changes or computing a time-dependent metric.

Primary-key partitioning matters because competing versions must meet the
required upsert consistency boundary. Configuring an upsert mode does not repair
a producer that routes the same key inconsistently. Deletes and partial updates
also have their own semantics. Test stale updates, ties, null fields and restart
readback before relying on those behaviors in a data product.

## Diagnosis and interview discussion

For hybrid queries, inspect offline coverage, the selected time boundary,
real-time consumption and event timestamps. For upserts, inspect key definition,
comparison values, partitioning and active record state. Keep those diagnostic
paths separate because changing a time boundary cannot fix a stale version choice.

**Interview discussion: is a hybrid table equivalent to an upsert table?** No.
Hybrid routing divides historical and fresh coverage, while upsert chooses a
current record for a key. The two cases show why overlap prevention and version
resolution need different fixtures, independent oracles and lifecycle tests.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Pinot apache-060 command notebook

Use these commands only from the copied owned Pinot project described in its README.
The classroom Markdown pad does not execute Docker commands.

```bash
cat realtime-table.json
cat schema.json
```

This displays a prepared real-time table, not a hybrid/upsert acceptance test. Create separately named hybrid and upsert experiments with explicit time boundaries, primary keys, comparison columns and source identities as described in the guide.

Native service acceptance and each advanced extension have distinct entries in
`QUALIFICATION.md`. Source/configuration presence is not an observed service result.

## Primary references

- [Hybrid tables](https://github.com/pinot-contrib/pinot-docs/blob/latest/basics/components/table/logical-table.md)
- [Upsert](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/ingestion/upsert-and-dedup/upsert.md)
- [Table configuration](https://github.com/pinot-contrib/pinot-docs/blob/latest/reference/configuration-reference/table.md)
