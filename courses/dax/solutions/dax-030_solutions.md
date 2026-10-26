# dax-030: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-030_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Newsletter's two customers

Analytics model; Audience=Newsletter; single-direction relationships into GroupMembership.

| RawRevenue | AudienceRevenue |
| --- | --- |
| 187 | 131 |

The explicit result follows a documented mapping. Enabling broad bidirectional filtering would affect other queries as well, so it is a model decision rather than a cosmetic fix.

- Newsletter leaves membership keys 10 and 20.
- Without explicit mapping the bridge does not filter Customer, so RawRevenue stays 187.
- TREATAS selects Ada 51 and Bo 80, totaling 131.

### Case B: Prospects overlaps the first audience

Analytics model; Audience=Prospects; selected membership keys 20 and 30.

| RawRevenue | AudienceRevenue |
| --- | --- |
| 187 | 136 |

Overlap is legitimate membership information. The error is treating overlapping audience results as disjoint partitions.

- Prospects selects Bo and Cy through the explicit mapping.
- Their revenues are 80 and 56, totaling 136.
- Bo is shared with Newsletter, so summing the two audience totals would count 80 twice.

## Explained practice answers

### Exercise 1

Predict the revenue for both audiences selected together.

The keys are 10,20,30, and the unique population totals 187 rather than 267.

### Exercise 2

Add Di to Newsletter without adding a sale.

The selected customer population increases, but Newsletter revenue remains 131 because Di has no sales.

### Exercise 3

Write a reconciliation for the two audience totals.

131 +136 -80 =187 for the union of these two audiences.

### Exercise 4

Diagnose a membership table with duplicate group/customer pairs.

Reject or repair duplicate membership rows. VALUES may hide them for this measure, but other counts or iterators could still overcount.

### Exercise 5

Explain why this mapping is not proof of row-level security.

A real security rule must be enforced by the engine under tested identities and relationship behavior; this is an analytical selection only.

### Exercise 6

Transfer the design to patients enrolled in multiple programs.

Model membership at program/patient grain, report overlap explicitly and choose unique-patient versus membership-weighted denominators deliberately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
