# cuda-022: explanatory solutions

## Mechanism review

A histogram counts values into bins. Several threads can increment the same bin, so ordinary read-modify-write operations can lose updates. An atomic addition makes that individual update indivisible at its supported scope. It does not make an entire multi-step algorithm atomic or publish unrelated data automatically. A block-private histogram can reduce global contention by combining local counts before a global merge. It also costs shared memory and initialization work. Distribution matters: uniformly spread samples and one hot bin exercise very different contention patterns even with identical input size.

## Exercise 1

Values \([0,2,2,1,2,0]\) with three bins produce \([2,1,3]\). The sum of bins is six. Two workers both reading an old count of zero and then each writing one lose a count; correct atomic accumulation produces two.

**Approach:** Count [0, 2, 2, 1, 2, 0] into three bins with an atomic increment per element, giving [2, 1, 3].

**Why it is correct:** atomicAdd makes each read-modify-write indivisible, so two threads hitting bin 0 at once produce 2 instead of both writing 1.

**A plausible wrong approach:** A plain bins[v]++ looks atomic in source but compiles to separate load, add and store, and two workers reading the old zero both store one.

**How to verify:** The reference asserts the merged bins equal [2, 1, 3] and sum to six, the input length, which is the conservation check to keep on a GPU.

## Exercise 2

Split the values into two groups of three. Their private histograms are \([1,0,2]\) and \([1,1,1]\); merging gives \([2,1,3]\). This explains the algorithm without promising the private version is faster. For small inputs, initialization and merging may cost more than direct atomic updates.

**Approach:** Give each of two groups a private histogram, [1, 0, 2] for the first three values and [1, 1, 1] for the rest, then add them binwise.

**Why it is correct:** Addition is associative and commutative on integer counts, so merging private bins yields exactly the global histogram.

**A plausible wrong approach:** Claiming the privatized version must be faster ignores the cost of zeroing and merging private copies, which can dominate for six elements.

**How to verify:** The reference prints partials [[1, 0, 2], [1, 1, 1]] and merged [2, 1, 3]; time each variant on a GPU before stating which wins.

## Exercise 3

\([1,1,0,3]\), with total five. Include the empty bin in validation.

**Approach:** Allocate four bins and increment for each of [3, 3, 0, 1, 3].

**Why it is correct:** Category 3 appears three times, 0 and 1 once each, and 2 never, giving [1, 1, 0, 3].

**A plausible wrong approach:** Allocating max(values) bins from the observed data would still be four here but drops bins silently whenever the top category is absent.

**How to verify:** Assert the result equals [1, 1, 0, 3], the sum is five, and bin 2 is reported as zero rather than omitted.

## Exercise 4

Reject it before indexing or explicitly count it in an overflow category. Never let it address memory before the bins.

**Approach:** Check 0 <= v < bins before any atomic, and either reject the input or route it to a declared overflow bin.

**Why it is correct:** Without the guard, -1 becomes an address one int before the bin array and corrupts whatever lives there.

**A plausible wrong approach:** Casting the value to unsigned makes -1 a huge index that skips the lower check yet still writes far outside the allocation.

**How to verify:** Feed [0, -1, 2] and confirm a rejection or overflow count of one while the in-range bins stay [1, 0, 1].

## Exercise 5

Repeating one category for every element; compare with a spread distribution under the same count and bin size.

**Approach:** Make every element the same category so every atomic targets one address, and run a uniform spread of the same length beside it.

**Why it is correct:** Same-address atomics serialize in the memory system, while spread values let updates proceed on distinct bins.

**A plausible wrong approach:** Using random data alone measures an average case and never exposes the worst-case serialization a skewed real dataset can trigger.

**How to verify:** Record measured times for both fixtures on one device and confirm both histograms still sum to the input length.

## Exercise 6

Specify bin edges, inclusivity, out-of-range and NaN policies before mapping values to integer bins.

**Approach:** Write down bin edges, whether each is closed on the left or right, and what happens to values below, above and NaN.

**Why it is correct:** A float exactly on an edge must map to one bin, and NaN compares false with every edge, so it needs an explicit rule.

**A plausible wrong approach:** Computing int((x - lo) / width) without a policy sends the maximum value to a bin one past the end.

**How to verify:** Test values equal to each edge, the top edge, a value below range, and NaN, and check each lands where the contract says.

## Self-check answers

1. **Why must the bin counts in worked example 1 sum to six?** Every input value lands in exactly one bin, so the total equals the input count.
2. **What does an atomic add guarantee and what does it not?** Each single update is indivisible; it does not make a multi-step algorithm atomic or order other writes.
3. **When might a private histogram be slower?** On small inputs or with many bins, where initializing and merging private copies costs more than it saves.

## Numerical reference and its limits

The [CPU reference](../references/cuda-022_cpu.py) reproduces worked example 1 and prints `{'partials': [[1, 0, 2], [1, 1, 1]], 'merged': [2, 1, 3]}`.

## Transfer review

Specify bin edges, inclusivity, out-of-range and NaN policies before mapping values to integer bins.
