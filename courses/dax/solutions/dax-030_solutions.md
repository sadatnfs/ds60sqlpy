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

The keys are 10, 20, 30, and the unique population totals 187 rather than 267.

**Why it fits this model:** VALUES over GroupMembership[CustomerKey] returns each customer once. Selecting both audiences yields {10, 20, 30}, and TREATAS sends that set to Customer: 51 + 80 + 56 = 187.

**Tempting mistake:** Adding the two audience totals, 131 + 136, gives 267 and counts Bo's 80 twice, even though only 187 USD exists.

**How to confirm:** With both audiences selected AudienceRevenue is 187, and COUNTROWS(VALUES(GroupMembership[CustomerKey])) is 3 while the bridge has 4 rows.

### Exercise 2

Add Di to Newsletter without adding a sale.

The selected customer population increases, but Newsletter revenue remains 131 because Di has no sales.

**Why it fits this model:** Membership and revenue are separate measures. Adding Di (key 40) gives Newsletter three members, while revenue stays 131 because Di has no sales.

**Tempting mistake:** Treating revenue as a check on membership loads. Unchanged revenue looks like the load failed, and revenue per member silently falls from 65.5 to about 43.67.

**How to confirm:** Under Newsletter, distinct members read 3 and AudienceRevenue 131.

### Exercise 3

Write a reconciliation for the two audience totals.

131 + 136 - 80 = 187 for the union of these two audiences.

**Why it fits this model:** Inclusion and exclusion: Newsletter 131 plus Prospects 136, minus the overlap, which is Bo alone at 80, equals the union, 187.

**Tempting mistake:** Subtracting the overlap count, 1, instead of the overlap revenue leaves 266, which mixes customers with USD.

**How to confirm:** `CALCULATE ( [NetRevenue], Customer[CustomerKey] = 20 )` returns 80, and 131 + 136 - 80 equals the both-audience result, 187.

### Exercise 4

Diagnose a membership table with duplicate group/customer pairs.

Reject or repair duplicate membership rows. VALUES may hide them for this measure, but other counts or iterators could still overcount.

**Why it fits this model:** The bridge's grain is one row per group and customer. A second (1, 10) row breaks that grain. VALUES hides it here, so Newsletter revenue still reads 131.

**Tempting mistake:** Accepting the duplicate because the revenue test passes. COUNTROWS(GroupMembership) under Newsletter becomes 3 instead of 2, and a SUMX over bridge rows gives 51 + 51 + 80 = 182.

**How to confirm:** Compare COUNTROWS(GroupMembership) with `COUNTROWS ( SUMMARIZE ( GroupMembership, GroupMembership[GroupKey], GroupMembership[CustomerKey] ) )`; any difference is a load defect.

### Exercise 5

Explain why this mapping is not proof of row-level security.

A real security rule must be enforced by the engine under tested identities and relationship behavior; this is an analytical selection only.

**Why it fits this model:** The audience mapping is a CALCULATE argument in a query. RawRevenue stays 187 under each audience because Audience filters only the bridge.

**Tempting mistake:** Calling the TREATAS measure a security rule. A user who drops the Audience filter or writes another measure on Sales sees 187, all customers.

**How to confirm:** Without the audience filter AudienceRevenue is 187. Real protection needs an engine role, tested under each identity.

### Exercise 6

Transfer the design to patients enrolled in multiple programs.

Model membership at program/patient grain, report overlap explicitly and choose unique-patient versus membership-weighted denominators deliberately.

**Why it fits this model:** Programs work like audiences: one row per program and patient, unique counts for reach and pair counts for workload. Using the audience data as a stand-in, Bo is in two groups.

**Tempting mistake:** Summing per-program patient counts, 2 + 2 = 4, as unique patients double-counts the overlap; the true count is 3.

**How to confirm:** Distinct patients across both programs should equal the sum of program counts minus the overlap: 2 + 2 - 1 = 3.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
