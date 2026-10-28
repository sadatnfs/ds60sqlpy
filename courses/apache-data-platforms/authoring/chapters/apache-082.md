## End-to-end streaming guarantees cross multiple boundaries

A Kafka-to-Flink-to-Pinot path combines a retained source log, stateful processing
and analytical serving. Each stage can have a strong local mechanism while the
whole path still duplicates, loses or temporarily hides business events. State
the guarantee at every source, checkpoint, sink and serving-publication boundary
before using the phrase exactly-once.

The individual course workshops have distinct owned projects and qualification
ledgers. Their separate success does not qualify a combined topology. The
integration path is a prepared extension until actual compatible connectors,
private networking, source positions and serving identities are exercised
together. Never present a Python list transformation as a running Kafka/Flink/Pinot
system.

A finite identity ledger makes a streaming experiment explainable. Assign stable
event IDs, business keys, event timestamps and version/correction semantics.
Transport offsets identify log positions; business IDs identify logical events.
They answer different questions and must not be substituted for each other when
reconciling a restart or retry.

## Worked case A: move one bounded event contract

Create a fresh explicitly owned integration topic and record its partition end
positions after producing the three known orders once. Submit the actual Flink
job with stated parallelism, timestamp/watermark policy, keyed state and sink
connector. Configure the actual Pinot real-time table with matching decoder,
schema and starting-position policy.

Poll under a deadline until the exact order identities and amounts are queryable
through the Pinot broker. Compare source positions, Flink operator/checkpoint
observations and Pinot consumption/query results. A healthy process count or zero
lag alone is insufficient. The expected business total is20 with regional totals
11and9 for this finite fixture.

Record which output is append-only and which represents current state. A stream
of changes can correctly retain several versions of a key while a current-state
serving table should select one. That distinction determines the oracle and
whether an apparent duplicate is a defect or an intended historical record.

## Worked case B: duplicate delivery and a late correction

Send a separate duplicate business event with the same stable ID, then a
correction with an explicit later business version and an older event timestamp.
Kafka can legitimately retain both sends. A processing deduplication policy may
suppress the repeated ID, while correction semantics may require the new version
to update the intended state. Define both rules before running the experiment.

A watermark can classify the correction as late without deciding whether the
business should discard it. Use an actual supported late-data route, correction
stream or backfill policy and reconcile its effect in serving. If the selected
connector path cannot implement the intended behavior, record that limitation
rather than modifying expected counts to fit an accidental result.

Restart one owned component after a completed checkpoint and compare retained
source/state/sink identities without replaying initialization. An external HTTP
side effect or nontransactional sink may duplicate work even when Flink state
restores consistently. Require actual sink participation before extending a
checkpoint guarantee into an end-to-end claim.

## Diagnosis and interview discussion

Build an incident table of source identity, source offset, processing state,
sink acknowledgment and query visibility. Classify missing, duplicated, stale
and unavailable results separately. Preserve the first failed connector or
schema diagnostic and never delete unrelated workshop volumes to reset the
experiment.

**Interview discussion: why can exactly-once state recovery coexist with duplicate
business output?** An external effect may not participate in the checkpoint/commit
protocol, or separate sends may be distinct transport records. These cases
require a combined actual topology and an independent event/version ledger before
claiming a system-level guarantee.
