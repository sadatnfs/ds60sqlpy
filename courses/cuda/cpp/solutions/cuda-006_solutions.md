# cuda-006: explanatory solutions

## Mechanism review

Floating-point arithmetic stores a finite approximation to a real number. Adding a small quantity to a large one may round away the small quantity; subtracting similar large values can expose that loss. Relative error scales with a reference magnitude, while absolute error remains meaningful near zero. A common comparison accepts an error no larger than absolute tolerance plus relative tolerance times reference magnitude. The tolerances must come from input ranges, precision and the calculation, not from repeatedly widening them until a broken index passes. Check finite output explicitly, and use exact comparison for integer counts that cannot overflow.

The separate [CPU reference](../references/cuda-006_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

The exact sum of \([10^{16},1,-10^{16}]\) is 1. A sequential binary64 addition can return 0 because \(10^{16}+1\) rounds back to \(10^{16}\). Python's compensated `math.fsum` recovers 1 for this fixture. Different summation order is a numerical mechanism, not proof that either processor is faulty.

**Approach:** Trace the sum in order: 1e16 + 1 rounds to 1e16, then subtracting 1e16 leaves 0.0.

**Why it is correct:** Binary64 has a 53-bit significand, so near 1e16 the spacing is 2 and adding 1 is lost.

**A plausible wrong approach:** Blaming the processor for the zero ignores that the same order on any IEEE 754 machine gives 0.0.

**How to verify:** The reference asserts naive == 0.0 and math.fsum(values) == 1.0, printing sequential 0.0 and compensated 1.0.

## Exercise 2

Compare output 0.00000004 with reference zero under absolute tolerance 0.0000001. It passes. A relative-only rule with zero reference would reject every nonzero result. Conversely, output 4 where reference is 3 cannot be excused as ordinary small rounding under those tolerances; first investigate shape, indexing and the mathematical contract.

**Approach:** Evaluate 4e-8 against atol 1e-7 with reference zero, then contrast with a relative-only rule.

**Why it is correct:** Absolute tolerance handles a zero reference, where relative error is undefined or infinite.

**A plausible wrong approach:** Widening tolerance until output 4 matches reference 3 hides an indexing or contract bug as rounding.

**How to verify:** The reference asserts abs(4e-8) <= 1e-7; also confirm |4 - 3| far exceeds any stated bound.

## Exercise 3

The bound is \(0.001+0.01\times 20=0.201\). This is a chosen acceptance policy, not a universal CUDA tolerance.

**Approach:** Substitute into atol + rtol * |reference|, giving 0.001 + 0.01 * 20.

**Why it is correct:** The relative term scales with the magnitude 20, producing 0.2, and the absolute floor adds 0.001.

**A plausible wrong approach:** Using rtol alone gives 0.2 and rejects an output at error 0.2005 that the policy accepts.

**How to verify:** Compute 0.201 by hand and test values 20.2 (pass) and 20.3 (fail) against the rule.

## Exercise 4

Require finite values before tolerance evaluation and reject NaN or infinity unless the specification explicitly expects them.

**Approach:** Add an explicit finiteness check before tolerance comparison and fail with a message naming the bad index.

**Why it is correct:** Any comparison with NaN is false, so a test that branches only on the tolerance silently misreports it.

**A plausible wrong approach:** Replacing NaN with zero before comparing hides the defect and can make a broken kernel pass.

**How to verify:** Inject one NaN into an output array and confirm the test fails at that index, not at the tolerance step.

## Exercise 5

The sum can exceed the representable range. Bound the worst-case sum or accumulate using a sufficiently wide type.

**Approach:** Bound the worst case as count times maximum value and compare with the int32 limit of 2,147,483,647.

**Why it is correct:** Exact inputs do not prevent overflow; the running total itself can exceed 32 bits and wrap.

**A plausible wrong approach:** Switching to float32 avoids wrapping but loses exactness above 2^24, so counts become wrong.

**How to verify:** Sum 3 values of 1e9 in int32 arithmetic and confirm the result exceeds the limit, while int64 holds it.

## Exercise 6

Compare every integer bin exactly and verify total count. Include empty, all-in-one-bin and out-of-range input policies; floating tolerance is unnecessary.

**Approach:** Build an exact integer reference histogram on the host and compare every bin plus the total count.

**Why it is correct:** Bin counts are integers, so exact equality is the correct contract and tolerance would hide miscounts.

**A plausible wrong approach:** Comparing only the total misses a kernel that puts every value in the wrong bin but keeps the sum.

**How to verify:** Run fixtures for empty input, all-one-bin input and out-of-range values, and check each bin exactly.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-006_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare every integer bin exactly and verify total count. Include empty, all-in-one-bin and out-of-range input policies; floating tolerance is unnecessary.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
