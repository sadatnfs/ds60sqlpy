# cuda-021: explanatory solutions

## Mechanism review

An exclusive scan gives each item the reduction of preceding items; an inclusive scan includes the item itself. For stable compaction, map the selection predicate to zeros and ones, scan those flags, then let selected input i write to its exclusive prefix position. Stability means selected elements keep their relative order. Multiple blocks require scanning block totals and adding offsets in another stage. A total count says how much output is needed but does not assign every destination. Separate input and output or prove that aliasing cannot overwrite unread values.

The separate [CPU reference](../references/cuda-021_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For values \([8,3,6,1,4]\), select even values. Flags are \([1,0,1,0,1]\), exclusive positions are \([0,1,1,2,2]\), and selected writes produce \([8,6,4]\). Nonselected elements have positions too, but they do not write.

**Approach:** Map each of [8, 3, 6, 1, 4] to an even flag, run an exclusive prefix sum over the flags, then let flagged elements write at their position.

**Why it is correct:** The exclusive prefix at a selected element counts selected elements before it, so 8 lands at slot 0, 6 at slot 1 and 4 at slot 2 in original order.

**A plausible wrong approach:** Letting each thread claim a slot with atomicAdd on a counter also yields three outputs, but their order depends on scheduling and may come back as [6, 8, 4].

**How to verify:** The CPU reference asserts positions == [0, 1, 1, 2, 2] and out == [8, 6, 4]; on a GPU compare the compacted buffer element by element, not as a set.

## Exercise 2

For flags \([0,0,0]\), the exclusive scan is \([0,0,0]\) and count is zero. For \([1,1,1]\), positions are \([0,1,2]\) and count is three. These cases catch allocating from the final exclusive prefix alone without adding the final flag.

**Approach:** Run the scan on the all-zero and all-one flag arrays and compute count as the final exclusive prefix plus the final flag in both cases.

**Why it is correct:** For [1, 1, 1] the last exclusive prefix is 2 while three items survive, and for [0, 0, 0] the same formula correctly gives zero.

**A plausible wrong approach:** Sizing the output from the last exclusive prefix alone allocates two slots for three survivors, and the third write overruns the buffer.

**How to verify:** Assert count == 0 for the empty selection and count == 3 for the full one, and place a sentinel after the output to catch a short allocation.

## Exercise 3

Flags \([1,0,1,1]\), positions \([0,1,1,2]\), output \([5,7,8]\). The preserved order is part of the contract.

**Approach:** Flag [5, 2, 7, 8] against greater than four to get [1, 0, 1, 1], then scan to positions [0, 1, 1, 2].

**Why it is correct:** Value 5 writes slot 0, value 7 writes slot 1 and value 8 writes slot 2; value 2 has position 1 but never writes.

**A plausible wrong approach:** Writing every element at its own position lets the rejected 2 overwrite slot 1 before or after 7 depending on thread timing.

**How to verify:** Expect exactly [5, 7, 8] with length three, and rerun with the predicate reversed to confirm the complement [2] appears alone.

## Exercise 4

It excludes the last element. Count equals final prefix plus final flag for nonempty input.

**Approach:** Add the final flag to the final exclusive prefix whenever the input is nonempty, or use an inclusive scan's last value directly.

**Why it is correct:** An exclusive prefix at index n minus one sums flags 0 through n minus two, so it omits whether the last element itself survives.

**A plausible wrong approach:** Adding one unconditionally to the last prefix overcounts whenever the final element is rejected, as in [1, 0, 1, 0, 0].

**How to verify:** Test inputs whose last flag is 0 and whose last flag is 1 with the same earlier flags, and confirm the counts differ by exactly one.

## Exercise 5

Both are empty and count is zero; no last-element access is valid.

**Approach:** Handle n == 0 on the host: return an empty scan, an empty compacted array and count zero without launching.

**Why it is correct:** No element exists, so there is no last prefix or last flag to read and nothing to write.

**A plausible wrong approach:** Computing count as positions[n - 1] + flags[n - 1] for n == 0 reads index -1, which in C++ is out of bounds before the buffer.

**How to verify:** Call the wrapper with an empty vector under a sanitizer and assert both outputs are empty and no kernel was enqueued.

## Exercise 6

Exclusive offsets are \([0,2,2]\); append total five to obtain \([0,2,2,5]\), the row-boundary representation.

**Approach:** Exclusive scan the row lengths [2, 0, 3] to [0, 2, 2], then append the total 5 to form [0, 2, 2, 5].

**Why it is correct:** Row r spans offsets[r] to offsets[r + 1], so the empty row 1 spans [2, 2) and row 2 spans [2, 5).

**A plausible wrong approach:** Using an inclusive scan [2, 2, 5] as row starts shifts every row by its own length and makes row 0 begin at 2.

**How to verify:** Check that consecutive differences of the offsets reproduce the original lengths [2, 0, 3] and that the last offset equals the item count.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-021_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Exclusive offsets are \([0,2,2]\); append total five to obtain \([0,2,2,5]\), the row-boundary representation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
