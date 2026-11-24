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

**Why it fits this model:** Two modes can only be compared when they read the same population at the same observation time. Case A matches at 187 because the data and definition are fixed.

**Tempting mistake:** Comparing yesterday's Import snapshot with a DirectQuery result taken now and calling case B's 10 USD gap (187 against 197) a formula difference.

**How to confirm:** Record source version, snapshot time, filters and role for both runs; with those equal, NetRevenue should agree, as case A's 187 and 187 do.

### Exercise 2

Change the hypothetical later event to a correction of an existing line.

Recompute the metric from the corrected source identity; do not assume every change adds an amount.

**Why it fits this model:** A correction replaces a value in an existing line instead of adding a new one. The change is whatever the corrected line differs by.

**Tempting mistake:** Assuming every source change adds an amount, so the later total must be 197. If S8 were corrected from 36 to 30, the total would fall.

**How to confirm:** Recompute from the corrected source: 187 - 36 + 30 = 181 for that illustrative correction, not 197.

### Exercise 3

Write a storage-mode capability review.

List measures versus calculated columns/RLS uses, supported functions, regular/limited relationships, security identity, source constraints and refresh/fallback behavior.

**Why it fits this model:** Capability depends on each object and the relationship it uses, so the review lists every measure, calculated column and RLS rule in the model.

**Tempting mistake:** Checking only that NetRevenue (a plain SUM) works and assuming GrossRevenue's row-level SUMX, the cost lookup through RELATED and the region role all behave the same.

**How to confirm:** For each object, record the target mode, relationship type, documented support and an observed test result, and mark anything untested as open.

### Exercise 4

Diagnose saying DirectQuery guarantees real-time truth.

Define and measure an actual freshness/consistency requirement; the mode name alone does not satisfy it.

**Why it fits this model:** Freshness is a requirement with a number attached, such as visible within 15 minutes. A storage mode is one input to meeting it.

**Tempting mistake:** Treating the DirectQuery number, such as case B's 197, as live truth while result caches, source replication lag or uncommitted transactions are still possible.

**How to confirm:** State the freshness target, insert a known test event like the 10 USD line, and time when it appears in the report.

### Exercise 5

Explain why this course does not require a Fabric account for Direct Lake study.

The lesson provides model and scenario reasoning offline. Live Direct Lake configuration would be a separately authorized external workflow.

**Why it fits this model:** The lesson's numbers, 187 and 197, come from checked-in fixtures and stated assumptions, so the reasoning can be done offline.

**Tempting mistake:** Provisioning a trial capacity to "verify" 187. A live Direct Lake model adds account, permission and data questions that this lesson does not need to answer.

**How to confirm:** Reproduce 187 from the fixture query; treat any live Direct Lake configuration as a separately authorized task with its own evidence.

### Exercise 6

Transfer the freshness boundary to a cached feature table.

Attach observation/version metadata and compare like-for-like populations before blaming a transformation for a changed total.

**Why it fits this model:** A cached feature table is a snapshot, like the stored model in case B. Its total reflects the version it was built from.

**Tempting mistake:** Blaming a transformation step when the feature table and source differ, when the cache was simply built before the late event.

**How to confirm:** Store build time and source version with the feature table; a gap that equals the late events, here exactly 10 USD, points to freshness.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
