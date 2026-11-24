# cuda-024: explanatory solutions

## Mechanism review

A pipeline is more than a list of correct kernels. Each stage has a shape, ownership and validity contract that must match its consumer. Filtering changes count; normalization changes numeric range; histogramming assumes valid bins. Keep the count with the output buffer, and do not pass allocation capacity as the number of valid elements. First build a tiny CPU oracle, then introduce one GPU stage at a time. A useful capstone report includes cases where a CPU is preferable, because proving that a GPU exists is different from proving it helps the application.

The separate [CPU reference](../references/cuda-024_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic event pipeline keeps nonnegative values from \([-2,1,3,-1,2]\), producing \([1,3,2]\). It computes count three, sum six and mean two. A histogram over bins 0 through 3 gives \([0,1,1,1]\). This ties compaction output count to every downstream stage.

**Approach:** Select nonnegative values from [-2, 1, 3, -1, 2], then compute count, sum, mean and four bins from the selected count only.

**Why it is correct:** Compaction yields [1, 3, 2], so count 3, sum 6 and mean 2 follow, and bins 1, 2, 3 each get one value.

**A plausible wrong approach:** Running the aggregate kernels over the full capacity of the output buffer adds unselected garbage to the sum.

**How to verify:** The reference asserts selected == [1, 3, 2], bins == [0, 1, 1, 1] and the result dictionary with mean 2.0.

## Exercise 2

An empty selection from \([-4,-1]\) has count zero and sum zero, but no defined ordinary arithmetic mean. Return a named empty-result status or optional mean rather than dividing by zero. The histogram remains four zeros under this contract.

**Approach:** Detect count zero after compaction and return an empty status or optional mean while keeping count and sum at zero.

**Why it is correct:** Zero values have a defined count and sum but no ordinary mean, and the histogram is four zeros.

**A plausible wrong approach:** Dividing sum by count anyway produces NaN for floats or a division fault for integers.

**How to verify:** Run [-4, -1] and assert count 0, sum 0, a missing mean and bins [0, 0, 0, 0].

## Exercise 3

Count three, sum three, mean one and histogram \([2,0,0,1]\) under four bins.

**Approach:** Keep all three values of [0, 0, 3], then aggregate and bin them.

**Why it is correct:** Count is 3, sum 3 and mean 1, and two zeros plus one three give [2, 0, 0, 1].

**A plausible wrong approach:** Treating zero as falsy in the predicate drops both zeros and returns count 1.

**How to verify:** Assert the full result and check that the bins sum to the count.

## Exercise 4

Capacity is storage extent, not valid count. Carry the selected count explicitly and bound downstream reads by it.

**Approach:** Pass the selected count produced by compaction to every downstream launch and bound reads by it.

**Why it is correct:** Capacity ten describes storage, while only three slots hold valid selected values.

**A plausible wrong approach:** Zeroing the unused seven slots makes the sum correct but still corrupts count, mean and bin zero.

**How to verify:** Fill unused slots with a sentinel such as 99 and confirm no downstream result changes.

## Exercise 5

Reject or explicitly extend the declared bin policy. Do not silently clamp unless clamping is part of the specification.

**Approach:** Reject 7 with a clear error or add an overflow bin named in the specification.

**Why it is correct:** Bins 0 to 3 cannot index 7, and clamping it to 3 changes the meaning of bin 3.

**A plausible wrong approach:** Clamping without saying so makes the histogram sum match while the distribution is wrong.

**How to verify:** Add a fixture containing 7 and assert the rejection or the overflow count.

## Exercise 6

Use identical selection, aggregation and result semantics; include required transfers and allocation or document reused state, retain samples and compare numerical outputs first.

**Approach:** Hold selection, aggregation, outputs and transfer scope identical for both implementations.

**Why it is correct:** Only then does a time difference reflect implementation rather than different work.

**A plausible wrong approach:** Comparing a GPU kernel time against a CPU time that includes I/O favors whichever side omits more.

**How to verify:** Check outputs agree first, then record repeated samples for each with the same inputs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-024_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use identical selection, aggregation and result semantics; include required transfers and allocation or document reused state, retain samples and compare numerical outputs first.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
