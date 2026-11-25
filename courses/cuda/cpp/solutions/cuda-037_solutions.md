# cuda-037: explanatory solutions

## Mechanism review

Divergence occurs when lanes in a warp follow different control-flow paths. It can reduce useful parallel execution, but branches that are uniform across a warp or skip substantial work can be beneficial. Irregular workloads also suffer from imbalance when some lanes have much longer loops. Reordering or compacting work can improve grouping at the cost of an extra pass and changed order. Preserve semantic ordering where required and include preprocessing in end-to-end measurement. Branch elimination that evaluates both expensive sides can make the program slower even when it reduces control flow.

## Exercise 1

Four conceptual lanes process workloads \([1,1,1,9]\). A simplified lockstep cost is nine rounds, with 12 useful lane-rounds out of 36 available positions, or one third utilization. This is a pedagogical model, not an actual CUDA timing prediction.

**Approach:** Take the longest workload 9 as rounds, sum useful work 12, and divide by 4 lanes times 9 rounds.

**Why it is correct:** Lanes with workload 1 idle for 8 rounds while one lane continues, so only 12 of 36 slots do work.

**A plausible wrong approach:** Averaging the workloads to 3 and assuming 3 rounds ignores that lockstep waits for the slowest lane.

**How to verify:** The reference asserts utilization == 1 / 3 and labels the value synthetic, not a timing.

## Exercise 2

A threshold operation has cheap and expensive categories. Grouping expensive items can make work more uniform, but a 2 ms compaction pass is not worthwhile if it saves only 1 ms of kernel time for a one-shot request. Reuse across many iterations can change that decision.

**Approach:** Compare 2 ms of compaction with 1 ms of kernel savings for a one-shot request.

**Why it is correct:** Net cost rises by 1 ms, so grouping only pays if the grouped data is reused across runs.

**A plausible wrong approach:** Adopting bucketing because it made the kernel faster ignores the preprocessing cost.

**How to verify:** The reference prints preprocess_ms_minus_saved_ms 1; measure end-to-end time before deciding.

## Exercise 3

Twelve useful lane-rounds over twelve positions gives one, while total work equals the first example's twelve.

**Approach:** Divide total work 12 by 4 lanes times max workload 3.

**Why it is correct:** Every lane works all three rounds, so utilization is 1.

**A plausible wrong approach:** Reasoning that equal total work means equal utilization misses that balance matters.

**How to verify:** The reference asserts sum([3, 3, 3, 3]) equals the first example's total of 12.

## Exercise 4

It can perform unnecessary arithmetic or invalid operations and increase resource use. Preserve conditional semantics and measure.

**Approach:** Keep the branch where one side does unsafe or expensive work, and measure alternatives.

**Why it is correct:** Computing both sides can divide by zero or read out of range on the inactive side.

**A plausible wrong approach:** Rewriting every if as a select to remove divergence can create invalid operations.

**How to verify:** Test inputs where the guarded side would fault and confirm no error.

## Exercise 5

A correct branch may skip the expensive work entirely. A branch-free implementation must still avoid unnecessary side effects or invalid accesses.

**Approach:** Let a false predicate skip the expensive work and its side effects.

**Why it is correct:** When no lane needs the work, a branch costs almost nothing.

**A plausible wrong approach:** A branch-free version that still loads or writes for every lane does unnecessary memory traffic.

**How to verify:** Run an all-false input and confirm outputs and memory stay unchanged.

## Exercise 6

Group similar lengths, preserve a mapping back to original rows, include grouping cost and validate every output and empty row.

**Approach:** Sort or bucket rows by length, keep their original indices, and scatter results back.

**Why it is correct:** Similar lengths in one warp reduce idle lanes, and the index map preserves output order.

**A plausible wrong approach:** Bucketing without saving original indices returns correct rows in the wrong order.

**How to verify:** Validate every row, including empty ones, and count grouping time in totals.

## Self-check answers

1. **What utilization does the lockstep model give for workloads [2,2,2,8]?** 14 useful lane-rounds out of 32, about 0.44.
2. **When is a branch warp-uniform?** When every lane of the warp takes the same path, so no divergence occurs.
3. **Why might reordering work change results?** It can change output order or arithmetic order unless order is restored or proven irrelevant.

## Numerical reference and its limits

The [CPU reference](../references/cuda-037_cpu.py) reproduces worked example 1 and prints `{'synthetic_lockstep_useful_fraction': 0.3333333333333333, 'preprocess_ms_minus_saved_ms': 1}`.

## Transfer review

Group similar lengths, preserve a mapping back to original rows, include grouping cost and validate every output and empty row.
