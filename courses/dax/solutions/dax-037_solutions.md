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

Alpha,Beta,Gamma,Delta rank 1,2,3,4 under both policies.

### Exercise 2

Change the cutoff from 2 to 1.

Both selection expressions return Alpha alone.

### Exercise 3

Write a ranking specification including its comparison population.

State eligible candidates, score definition, filter-removal policy, order, tie handling and unique display key.

### Exercise 4

Diagnose formatting two unequal decimals to the same displayed score.

Decide whether rounded scores should define ties; if so, round the ranking expression deliberately rather than relying on display formatting.

### Exercise 5

Explain a blank score's policy.

Decide whether blank-scored candidates belong in the ranking population and filter them explicitly if they do not.

### Exercise 6

Transfer the distinction to selecting customers for a limited-capacity program.

Do not claim that a deterministic secondary key creates a substantive difference between equally scored candidates.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
