# dax-037: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-037_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Dense and skip ranks

Query-local candidate fixture; descending score; four unique names and one score tie.

| Name | Score | DenseRank | SkipRank |
| --- | --- | --- | --- |
| Alpha | 100 | 1 | 1 |
| Beta | 80 | 2 | 2 |
| Gamma | 80 | 2 | 2 |
| Delta | 50 | 3 | 4 |

The shared ranks are intentional. Displaying Beta before Gamma does not make its dense rank smaller.

- Alpha has the only score 100 and rank 1.
- Beta and Gamma share score 80 and rank 2.
- Delta follows the tie at dense rank 3 or skip rank 4.

### Case B: Tied cutoff versus a deliberate tie-breaker

Same candidate table; compare score-only selection with score plus unique Name ordering.

| TopTwoByScoreRows | TopTwoWithTieBreakerRows |
| --- | --- |
| 3 | 2 |

A user-facing Top N specification must say whether ties are all included or resolved by a secondary key.

- The second score position is 80 and two candidates share it.
- Score-only TOPN includes Alpha, Beta and Gamma.
- Adding Name as a tie-breaker selects Alpha and Beta exactly.

## Explained practice answers

### Exercise 1

Predict both ranks if Gamma's score becomes 79.

Alpha, Beta, Gamma, Delta rank 1, 2, 3, 4 under both policies.

**Why it fits this model:** Without the 80 tie, the four scores 100, 80, 79 and 50 are distinct. DENSE and SKIP differ only after a tie, so both give 1, 2, 3 and 4.

**Tempting mistake:** Expecting Delta to keep SkipRank 4 and DenseRank 3, as in case A. That gap came from the Beta and Gamma tie, which no longer exists.

**How to confirm:** With Gamma at 79 in the DATATABLE, both rank columns read 1, 2, 3, 4.

### Exercise 2

Change the cutoff from 2 to 1.

Both selection expressions return Alpha alone.

**Why it fits this model:** TOPN keeps every row tied with the last selected value. At N = 1 the last value is Alpha's 100, which nobody shares, so the tie-breaker has nothing to decide.

**Tempting mistake:** Concluding from case B that TOPN always returns extra rows. Ties only add rows when they fall at the cutoff, as the 80s do at N = 2.

**How to confirm:** Both COUNTROWS expressions return 1 at N = 1.

### Exercise 3

Write a ranking specification including its comparison population.

State eligible candidates, score definition, filter-removal policy, order, tie handling and unique display key.

**Why it fits this model:** State the population first. In the retail model, products ranked over ALL(Product[ProductName]) by NetRevenue give Mug 96, Notebook 67, Pen 24 and Bag BLANK. Within the Paper category, Notebook ranks first.

**Tempting mistake:** Writing RANKX(ALL(Product), [NetRevenue]) for a by-category visual ranks Notebook 2 globally when the reader expected 1 within Paper. The filter-removal choice is part of the spec.

**How to confirm:** The spec lists the population, the score measure, ALL versus ALLSELECTED, DESC, the DENSE or SKIP policy and ProductName as the display key.

### Exercise 4

Diagnose formatting two unequal decimals to the same displayed score.

Decide whether rounded scores should define ties; if so, round the ranking expression deliberately rather than relying on display formatting.

**Why it fits this model:** RANKX compares stored values. Scores such as 80.4 and 79.6 both display as 80 at zero decimals but still rank 2 and 3.

**Tempting mistake:** Assuming a format string creates the tie readers see. It only changes the display, so two rows that look equal get different ranks.

**How to confirm:** If rounded ties are intended, rank `ROUND ( [Score], 0 )`; both rows then get rank 2 under DENSE, matching the display.

### Exercise 5

Explain a blank score's policy.

Decide whether blank-scored candidates belong in the ranking population and filter them explicitly if they do not.

**Why it fits this model:** A blank score is still ranked unless it is excluded. Ranked by NetRevenue over all products, Bag's BLANK sorts below every positive value and takes rank 4.

**Tempting mistake:** Leaving Bag in the population and reporting four ranked products when the business population was products with sales.

**How to confirm:** Filtering the table to products where NOT ISBLANK([NetRevenue]) leaves three ranked products, with Pen last at 3.

### Exercise 6

Transfer the distinction to selecting customers for a limited-capacity program.

Do not claim that a deterministic secondary key creates a substantive difference between equally scored candidates.

**Why it fits this model:** Capacity is exact, so the rule must break ties and say how. At two slots, Beta and Gamma tie at 80 for the second place.

**Tempting mistake:** Using Name as the tie-breaker and presenting Beta as a better candidate than Gamma. Alphabetical order is a disclosed rule, not evidence of merit.

**How to confirm:** TOPN by score alone returns 3 rows; with the Name tie-breaker it returns 2 (Alpha and Beta). The program notes should say the second slot was decided by name between equal scores.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
