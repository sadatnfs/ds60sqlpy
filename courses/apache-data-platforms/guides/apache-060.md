# apache-060: Time boundaries, hybrid tables and upserts

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-059`, `apache-057`.

## Key terms

- **Hybrid table:** A logical Pinot table backed by an OFFLINE table for historical data and a REALTIME table for fresh data.
- **Time boundary:** The timestamp the broker uses to split a hybrid query, reading older data from the offline side and newer data from the real-time side.
- **Upsert:** A real-time table mode that keeps only the latest record for each primary key.
- **Comparison column:** The column an upsert table uses to decide which record for a primary key is newest.

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

## Worked case A: divide an overlapping historical interval (design exercise)

The workshop has no real-time route, so neither case in this chapter is executed.
Each case states the configuration it would use and its written answer.

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

In Pinot 1.5.1 the broker derives the boundary from the latest offline segment end
time minus one day (minus one hour when the offline ingestion frequency is hourly).
It sends the offline table the query with `event_ts <= boundary` added and the
real-time table the query with `event_ts > boundary` added, then merges the results.
The written answer for this fixture: if the latest offline event is
2026-01-01T12:00:00Z, the boundary is 2025-12-31T12:00:00Z. The offline side then
answers no rows, and the real-time side answers every day-1 and day-2 row, so each
day-1 event is counted once, from its real-time copy. A controller call,
`POST /tables/{tableName}/timeBoundary`, pins the boundary to the latest offline end
time instead; it must be repeated after every newer offline upload.

If a backfill ends earlier than expected, moving the boundary without complete
coverage can omit data. If it advances into a region with uncommitted offline
segments, the broker may exclude valid real-time contributions before their
replacement is queryable. Treat boundary progression as a controlled publication
step with completeness and availability evidence.

## Worked case B: a later version changes current state (design exercise)

Use a separate prepared upsert table with order ID as primary key and an explicit
monotonic version column. The schema adds `"primaryKeyColumns": ["id"]`, and the
real-time table configuration adds:

```json
{
  "upsertConfig": {
    "mode": "FULL",
    "comparisonColumns": ["version"]
  },
  "routing": {
    "instanceSelectorType": "strictReplicaGroup"
  }
}
```

`FULL` replaces the whole stored row when a record for the same key arrives with a
larger comparison value, and `strictReplicaGroup` routing keeps every segment of a
partition on one server, which upsert requires. Send ID 1 at version 1 with amount 4, then version 2
with amount 6, then a delayed version 1. The current-state oracle expects amount 6:
the delayed record has a smaller comparison value than version 2, so it does not
replace the stored row. Pinot documents that two records with the same key and the
same comparison value have no determined order, so a tie needs its own rule rather
than an assumption about arrival order.

An append-only analytical table would legitimately retain multiple events for
that sequence. Its sum answers a different question from the current-state upsert
table. Decide whether the application needs a changelog, a current snapshot or
both. Replacing events with current state can remove information required for
auditing historical changes or computing a time-dependent metric.

Primary-key partitioning matters because competing versions must meet the
required upsert consistency boundary: the Kafka producer must use the order ID as
the message key so that every version of a key reaches the same partition. Configuring an upsert mode does not repair
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
