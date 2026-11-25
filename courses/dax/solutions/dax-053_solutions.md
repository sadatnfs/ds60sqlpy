# dax-053: explained reference and practice reasoning

Confirm that the reference computes mean, median and best for A and B from DATATABLE values and labels every column as synthetic. Your notes should explain why B wins on best and median yet loses on mean. Read it beside the [reference source](dax-053_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

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

The mean becomes (20 + 40 + 21)/3 = 27 ms for that revised synthetic scenario.

**Why it fits this model:** Replacing 25 with 40 gives 20, 40 and 21. Recompute the same mean over all three trials.

**Tempting mistake:** Dropping 40 as an outlier and reporting 20.5 ms. That changes the statistic after seeing the data.

**How to confirm:** The mean is 81 / 3 = 27 ms; the median is 21 ms.

### Exercise 2

Compare A's cold trial with B's warm trial conceptually.

That comparison cannot isolate a formula effect; measure both under a controlled, recorded condition.

**Why it fits this model:** Cold trials average 110 ms and warm trials 22 ms, so comparing across cache states mixes two causes.

**Tempting mistake:** Timing A cold, near case A's 110 ms, and B warm, near 22 ms, then crediting B's formula with an 88 ms gain. Cache state alone explains a gap that size.

**How to confirm:** Compare A and B only under the same cache condition, as case B does: means 20 and 32, medians 20 and 18.

### Exercise 3

Write a real benchmark protocol without running it here.

Pin source/model/engine, specify filters and cache preparation, collect repeated results and diagnostics, validate outputs, and report variability and limitations.

**Why it fits this model:** A protocol fixes what is being compared before timing: the same model and engine, the same filters, results that match, and a stated cache preparation.

**Tempting mistake:** Running each candidate once after editing it, so the first run is cold for one and warm for the other.

**How to confirm:** Each candidate must return the same result before timing; report repeated trials with mean, median and spread, as case B's three trials show.

### Exercise 4

Diagnose quoting 18 ms as B's stable production latency.

It is not a measurement at all in this lesson, and a best trial would not establish production latency even if observed.

**Why it fits this model:** B's trials are 18, 60 and 18. The best is 18, the mean 32, and the 60 ms trial shows variability.

**Tempting mistake:** Quoting 18 ms as production latency. These numbers are synthetic, and a best trial hides the slow one.

**How to confirm:** Report 18, 60 and 18 with mean 32 and median 18, and label them synthetic.

### Exercise 5

Explain why a smaller toy model cannot establish behavior at production cardinality.

Treat toy semantic checks and representative-scale performance evidence as separate gates.

**Why it fits this model:** The 8-row Sales table proves results, such as 187, not speed. Plans, memory and contention change at millions of rows.

**Tempting mistake:** Timing two expressions on this fixture and expecting the faster one to stay faster in production.

**How to confirm:** Use toy models for correctness and a representative-scale model for speed.

### Exercise 6

Transfer the review to a machine-learning inference benchmark.

Record comparable conditions and actual output correctness before interpreting throughput or latency, especially with accelerators.

**Why it fits this model:** Inference benchmarks have the same cold path: model loading, compilation and warmup. A first trial like B's 60 ms can be setup cost.

**Tempting mistake:** Averaging the first call with steady-state calls, or reporting only warm calls without saying so.

**How to confirm:** Report setup and steady-state timings separately, with batch size and synchronization stated, and check the outputs match before comparing speed.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
