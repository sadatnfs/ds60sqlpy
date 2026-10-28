# apache-058: Kafka ingestion and real-time segments

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-057`.

## A consuming segment connects a log to an analytical table

Real-time Pinot ingestion reads a supported stream, decodes records and builds
consuming segments. Those segments later become completed segments according to
the configured flush and commit rules. Kafka partition positions, decoded rows,
indexed documents and query results are related observations, but they need not
advance at the same instant. A small query result does not establish that the
consumer has caught up to the source.

The prepared `realtime-table.json` uses the actual Kafka connector configuration
keys for the pinned Pinot release. It declares a topic, broker address, low-level
consumer, JSON decoder and flush thresholds. Those settings are a prepared route,
not evidence that the standalone offline workshop has exercised Kafka ingestion.
Connect only an explicitly owned private Kafka project with matching networking
and record a separate live qualification before asserting this path passed.

A schema describes how decoded values become typed columns. A malformed JSON
record, a missing optional field and an incompatible numeric value can take
different paths depending on decoder and ingestion configuration. Decide whether
to reject, skip, transform or quarantine each condition. Do not assume that an
increasing Kafka offset proves every source record became a valid document.

## Worked case A: reconcile a known Kafka event set

Use the shared order contract with IDs 1, 2 and 3 and amounts 4, 9 and 7. Produce
it once to a fresh owned topic and capture each partition's end position. Configure
the Pinot table before sending the bounded batch, or deliberately choose the
starting-offset policy and document it. Starting at latest after production can
correctly skip earlier records while appearing healthy.

Poll the broker under a deadline until the exact IDs and values are visible.
Compare total 20, regional totals 11 and 9, and source identities independently.
Also inspect consumer positions and ingestion errors. Query equality establishes
that this finite event set is visible; it does not prove that arbitrary future
traffic, retries or failures meet an end-to-end exactly-once claim.

The lag for a partition can be written as \(L_p=E_p-C_p\), where \(E_p\) is a
stated source end position and \(C_p\) is the comparable consumer position.
Specify whether each number is the next offset or last processed offset before
subtracting. Summing lag across partitions can conceal one stuck or unusually
hot partition, so retain the per-partition observations.

## Worked case B: a malformed event changes reconciliation

Append one intentionally malformed fixture after the three valid orders. Record
its source position and expected handling. If the configured decoder skips it,
source consumption can advance while the table remains at three valid documents.
That difference is explainable only when a decoder error or explicit skip counter
supports it. An unexplained count mismatch remains a failed acceptance check.

A dead-letter route is a separate output with its own identity and delivery
contract. Naming a topic does not prove that Pinot or the surrounding pipeline
actually wrote the rejected payload there. If the selected connector cannot
provide the desired quarantine semantics directly, place an explicit validated
transformation before Pinot and test that route rather than describing a fictional
built-in guarantee.

Changing the flush threshold affects when consuming segments commit, not whether
a malformed business event becomes valid. Very small thresholds create many
segments and coordination overhead; very large thresholds retain more consuming
state and delay completion. Measure source rate, segment size, query behavior and
recovery before selecting thresholds for a real workload.

## Diagnosis and interview discussion

Check broker connectivity, topic/partition discovery, offset-reset policy,
decoder/schema configuration, consumer exceptions and server metrics. Separate
no new source records from a stalled consumer and separate decoded-row loss from
query filtering. A healthy HTTP endpoint is weaker than reconciled source and
serving identities.

**Interview discussion: can zero consumer lag prove correct ingestion?** No. It
can coexist with rejected records, schema coercion or incorrect business filtering.
The first case checks a finite valid event set, and the second explains why an
explicit malformed-record observation is needed to reconcile source progress
with analytical document counts.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Pinot apache-058 command notebook

Use these commands only from the copied owned Pinot project described in its README.
The classroom Markdown pad does not execute Docker commands.

```bash
cat realtime-table.json
cat schema.json
```

This displays the released connector configuration only. Prepare a separately owned Kafka route, reconcile partition positions and exact decoded IDs, and record malformed-event handling before calling the streaming route qualified.

Native service acceptance and each advanced extension have distinct entries in
`QUALIFICATION.md`. Source/configuration presence is not an observed service result.

## Primary references

- [Stream ingestion](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/ingestion/stream-ingestion.md)
- [Kafka connector](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/ingestion/stream-ingestion/import-from-apache-kafka.md)
- [Table configuration](https://github.com/pinot-contrib/pinot-docs/blob/latest/reference/configuration-reference/table.md)
