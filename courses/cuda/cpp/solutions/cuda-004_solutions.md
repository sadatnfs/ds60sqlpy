# cuda-004: explanatory solutions

## Mechanism review

Decomposition assigns parts of a problem to workers while preserving its mathematical meaning. A map transforms each input independently. A reduction combines many values into one. A scan produces every prefix, so its outputs encode more information than a reduction. Gather reads from chosen locations; scatter writes to chosen locations and needs a conflict policy when destinations overlap. Work counts all operations, while dependency depth counts the longest chain that cannot be parallelized. A useful decomposition names each output owner, describes required inputs and states when producers must finish before consumers read.

## Exercise 1

Partition 10 elements into conceptual blocks of four. The ownership ranges are [0,4), [4,8) and [8,10). The half-open notation includes the start and excludes the end. Each element appears once; the final block has a tail. Allocating three full blocks of output without a bounds predicate would incorrectly expose positions 10 and 11.

**Approach:** Step through starts 0, 4 and 8 with block size 4, clamp each end to 10, and list the half-open ranges.

**Why it is correct:** Half-open ranges [0,4), [4,8) and [8,10) cover every index exactly once, and the final range stops at 10.

**A plausible wrong approach:** Writing ranges as [0,3], [4,7], [8,11] without clamping invents positions 10 and 11, outside the output.

**How to verify:** The reference concatenates the ranges and asserts they equal list(range(10)), catching both gaps and overruns.

## Exercise 2

For \([2,1,3,4]\), reduction returns 10. Inclusive scan returns \([2,3,6,10]\), and exclusive scan returns \([0,2,3,6]\). A reduction alone cannot tell element 2 where to write in a stable filtered output. That position comes from a prefix count of earlier selected elements.

**Approach:** Compute the total once, then build inclusive and exclusive scans of [2, 1, 3, 4] by carrying a running sum.

**Why it is correct:** The exclusive scan records the sum before each element, so element i learns how many units precede it.

**A plausible wrong approach:** Using the reduction value 10 to place selected elements fails because every element receives the same number.

**How to verify:** The reference asserts prefix == [0, 2, 3, 6] and total == 10; add the last prefix and last value to get 10.

## Exercise 3

Four tiles cover it. Predicate both x<7 and y<3; the right and bottom tiles contain invalid lane positions.

**Approach:** Count tiles per axis with ceil(7 / 4) = 2 and ceil(3 / 2) = 2, then mark which lanes fall outside.

**Why it is correct:** Two by two tiles cover an 8-by-4 lane area, and predicates x < 7 and y < 3 reject the extra column and row.

**A plausible wrong approach:** Checking only x < 7 lets the bottom tile write row 3, which does not exist in a height-3 image.

**How to verify:** Enumerate every lane coordinate and confirm exactly 21 pass both predicates, matching 7 times 3 pixels.

## Exercise 4

Unique readers do not imply unique output ownership. Define an atomic combine, collision-free destination calculation or a staged grouping algorithm.

**Approach:** Name the output owner for output[2], then choose atomics, a collision-free mapping or a sort-and-group stage.

**Why it is correct:** Two distinct readers can compute the same destination, so input uniqueness says nothing about write conflicts.

**A plausible wrong approach:** Accepting plain stores and assuming the last writer wins produces a nondeterministic value when both writes race.

**How to verify:** Feed a fixture where two inputs map to index 2 and confirm the result equals the declared combine of both.

## Exercise 5

The reduction identity is zero; both scans are empty. An implementation should define these cases before launching work.

**Approach:** Apply the identity rule: a reduction over no elements returns 0 for addition, and each scan returns a list of length zero.

**Why it is correct:** Zero is the additive identity, and a scan has exactly one output per input, so empty input yields empty output.

**A plausible wrong approach:** Returning [0] for the exclusive scan adds an element that no input owns and breaks length equality.

**How to verify:** Assert sum([]) == 0 and that the prefix loop over an empty list leaves prefix == [] and total == 0.

## Exercise 6

Map produces selection flags, exclusive scan gives each selected element's destination, and the final prefix plus flag gives output count.

**Approach:** Map each element to a flag, exclusive-scan the flags for destinations, and add the last prefix to the last flag for the count.

**Why it is correct:** Earlier selected elements fix each destination, so a stable output keeps original order without collisions.

**A plausible wrong approach:** Assigning destinations with an atomic counter gives unique slots but scrambles the order across threads.

**How to verify:** For flags [1, 0, 1, 1] expect prefixes [0, 1, 1, 2] and count 3, with selected values in input order.

## Self-check answers

1. **Write the ownership ranges for 13 elements in blocks of five.** [0,5), [5,10) and [10,13); the last block has only three valid elements.
2. **Why does a stable filter need a scan rather than a reduction?** Each selected element needs its own output position, which is the count of selected elements before it, a prefix result that a single total cannot supply.
3. **What extra rule does scatter need that map does not?** A conflict policy for destinations written by more than one worker, such as atomic combination or a guarantee of unique targets.

## Numerical reference and its limits

The [CPU reference](../references/cuda-004_cpu.py) reproduces worked example 1 and prints `{'exclusive_scan': [0, 2, 3, 6], 'reduction': 10, 'ownership': [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]}`.

## Transfer review

Map produces selection flags, exclusive scan gives each selected element's destination, and the final prefix plus flag gives output count.
