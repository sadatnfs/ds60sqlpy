# dax-055: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-055_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Same data, same defined amount

The same fixed data and compatible semantics; no actual storage-mode execution.

| FixedFixtureRevenue | EquivalentSnapshotRevenue |
| --- | --- |
| 187 | 187 |

A release should compare actual model outputs after any storage-mode change rather than assuming the mode preserves every detail.

- Both expressions include the same eight line amounts.
- Each totals 187.
- This parity condition says nothing about refresh latency or external function support.

### Case B: A refresh boundary can explain a difference

Illustrative scenario: an additional valid 10 USD event arrives after the stored snapshot; it is not added to the checked-in Sales fixture.

| StoredSnapshot | HypotheticalLaterSource |
| --- | --- |
| 187 | 197 |

The additional event is scenario data, not evidence of a connected source or live DirectQuery result.

- The snapshot still contains 187.
- The hypothetical later source adds exactly 10 under the same metric policy.
- Its intended amount is 197; an observed difference would need provenance and freshness checks.

## Explained practice answers

### Exercise 1

State the observations needed to compare Import and DirectQuery fairly.

Record equivalent populations, source/snapshot versions, filters, roles, function support and actual query/refresh evidence.

### Exercise 2

Change the hypothetical later event to a correction of an existing line.

Recompute the metric from the corrected source identity; do not assume every change adds an amount.

### Exercise 3

Write a storage-mode capability review.

List measures versus calculated columns/RLS uses, supported functions, regular/limited relationships, security identity, source constraints and refresh/fallback behavior.

### Exercise 4

Diagnose saying DirectQuery guarantees real-time truth.

Define and measure an actual freshness/consistency requirement; the mode name alone does not satisfy it.

### Exercise 5

Explain why this course does not require a Fabric account for Direct Lake study.

The lesson provides model and scenario reasoning offline. Live Direct Lake configuration would be a separately authorized external workflow.

### Exercise 6

Transfer the freshness boundary to a cached feature table.

Attach observation/version metadata and compare like-for-like populations before blaming a transformation for a changed total.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
