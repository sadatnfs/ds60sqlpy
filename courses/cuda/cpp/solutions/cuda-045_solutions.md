# cuda-045: explanatory solutions

## Mechanism review

CUDA Core Compute Libraries bring maintained building blocks such as Thrust algorithms, CUB primitives and CUDA-oriented standard-library facilities. Their abstractions do not remove ownership, stream or temporary-storage obligations. Prefer a tested library primitive when it matches semantics, and keep a handwritten version as a learning baseline or for a demonstrated special requirement. Some primitive interfaces separate workspace-size queries from execution; read the pinned interface rather than guessing. Iterator adapters can avoid materializing intermediate arrays, but they must preserve valid lifetimes and access patterns.

## Exercise 1

Transform \([1,2,3,4]\) by squaring and sum, obtaining 30. A fused transform-reduce can avoid a separate \([1,4,9,16]\) allocation when its interface supports the desired operation. The mathematical result is the same; the memory and scheduling behavior differ.

**Approach:** Express squaring and summing of [1, 2, 3, 4] as one transform-reduce call.

**Why it is correct:** 1 + 4 + 9 + 16 = 30, and fusion avoids storing [1, 4, 9, 16].

**A plausible wrong approach:** Materializing the squares then reducing is correct but allocates and reads an extra array.

**How to verify:** The reference asserts the sum of squares is 30.

## Exercise 2

Stable filtering \([5,2,5,1]\) for values at least five returns \([5,5]\). Sorting before filtering also retains the two fives here, but generally changes order. Choose the algorithm according to semantic requirements, not merely the nearest familiar function name.

**Approach:** Use a stable selection keeping values at least 5 in input order.

**Why it is correct:** Stable filtering of [5, 2, 5, 1] returns [5, 5] with original order preserved.

**A plausible wrong approach:** Sorting first passes this fixture but reorders survivors in general.

**How to verify:** Test a fixture with distinct survivors such as [7, 2, 5] and confirm order [7, 5].

## Exercise 3

Both can produce thirty for the fixture, but transform-reduce can express transformation without a materialized full intermediate.

**Approach:** Compare a reduce over a materialized squares array with transform-reduce.

**Why it is correct:** Both give 30, but transform-reduce never stores the intermediate.

**A plausible wrong approach:** Claiming the results differ because the algorithms differ confuses implementation with value.

**How to verify:** Run both on the fixture and assert equal outputs.

## Exercise 4

Work can otherwise occur on a different queue than its producers/consumers, breaking dependencies or introducing unexpected synchronization.

**Approach:** Pass the same stream that orders producer and consumer work.

**Why it is correct:** Library work on another stream can run before inputs are ready.

**A plausible wrong approach:** Leaving the default stream can add hidden synchronization with other streams.

**How to verify:** Profile or check ordering with a delayed producer to confirm dependencies hold.

## Exercise 5

Zero under the chosen reduction operator; confirm the library call's initial-value contract.

**Approach:** Use zero as the initial value for an empty sum of squares.

**Why it is correct:** Zero is the identity for addition, so the empty result is zero.

**A plausible wrong approach:** Passing the first element as initial value fails when no element exists.

**How to verify:** Call the library with an empty range and assert zero.

## Exercise 6

A measured unmet contract or fusion opportunity after correctness and library baseline comparison, not merely a desire to avoid reading library documentation.

**Approach:** Write a custom reduction only after a measured shortfall against a library baseline.

**Why it is correct:** The library already handles correctness and tuning across devices.

**A plausible wrong approach:** Writing one to avoid reading documentation duplicates tested code with new bugs.

**How to verify:** Show the library result, the unmet requirement and correct custom output.

## Self-check answers

1. **Why can transform-reduce use less memory than transform followed by reduce?** It fuses the steps and avoids storing the intermediate squared array.
2. **What is the sum of squares of an empty input?** Zero, the identity of addition.
3. **Why is a library stream argument a correctness choice?** Work on the wrong stream is not ordered with the producers and consumers of its data.

## Numerical reference and its limits

The [CPU reference](../references/cuda-045_cpu.py) reproduces worked example 1 and prints `{'transform_reduce_reference': 30, 'stable_selection': [5, 5]}`.

## Transfer review

A measured unmet contract or fusion opportunity after correctness and library baseline comparison, not merely a desire to avoid reading library documentation.
