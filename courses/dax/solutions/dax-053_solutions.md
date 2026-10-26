# dax-053: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-053_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Cold and warm are different conditions

Original synthetic trial scenario, not measured engine output; three supplied values per cache-state label.

| SyntheticColdMeanMs | SyntheticWarmMeanMs |
| --- | --- |
| 110 | 22 |

Cache-state labels are part of a benchmark's design. These invented values teach the comparison issue but establish no performance property of this course or a DAX engine.

- The synthetic cold values sum to 330 and average 110.
- The synthetic warm values sum to 66 and average 22.
- The different conditions must not be presented as proof that one formula is five times faster.

### Case B: Best trial and average can disagree

Two synthetic three-trial candidates under a hypothetical comparable condition; no real benchmark claim.

| MeanA | MedianA | BestA | MeanB | MedianB | BestB |
| --- | --- | --- | --- | --- | --- |
| 20 | 20 | 19 | 32 | 18 | 18 |

Three invented trials cannot estimate production tail latency. The point is to inspect the full evidence and design an adequate real measurement procedure.

- CandidateA has mean 20, median 20 and best 19.
- CandidateB has mean 32, median 18 and best 18 because one supplied trial is 60.
- Selecting only the best trial hides the variability shown by the complete record.

## Explained practice answers

### Exercise 1

Predict the mean if the warm 25 ms value is replaced by 40 ms.

The mean becomes(20+40+21)/3 =27 ms for that revised synthetic scenario.

### Exercise 2

Compare A's cold trial with B's warm trial conceptually.

That comparison cannot isolate a formula effect; measure both under a controlled, recorded condition.

### Exercise 3

Write a real benchmark protocol without running it here.

Pin source/model/engine, specify filters and cache preparation, collect repeated results and diagnostics, validate outputs, and report variability and limitations.

### Exercise 4

Diagnose quoting 18 ms as B's stable production latency.

It is not a measurement at all in this lesson, and a best trial would not establish production latency even if observed.

### Exercise 5

Explain why a smaller toy model cannot establish behavior at production cardinality.

Treat toy semantic checks and representative-scale performance evidence as separate gates.

### Exercise 6

Transfer the review to a machine-learning inference benchmark.

Record comparable conditions and actual output correctness before interpreting throughput or latency, especially with accelerators.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
