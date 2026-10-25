# cuda-006: explanatory solutions

## Mechanism review

Floating-point arithmetic stores a finite approximation to a real number. Adding a small quantity to a large one may round away the small quantity; subtracting similar large values can expose that loss. Relative error scales with a reference magnitude, while absolute error remains meaningful near zero. A common comparison accepts an error no larger than absolute tolerance plus relative tolerance times reference magnitude. The tolerances must come from input ranges, precision and the calculation, not from repeatedly widening them until a broken index passes. Check finite output explicitly, and use exact comparison for integer counts that cannot overflow.

The separate [CPU reference](../references/cuda-006_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

The exact sum of \([10^{16},1,-10^{16}]\) is 1. A sequential binary64 addition can return 0 because \(10^{16}+1\) rounds back to \(10^{16}\). Python's compensated `math.fsum` recovers 1 for this fixture. Different summation order is a numerical mechanism, not proof that either processor is faulty.

## Exercise 2

Compare output 0.00000004 with reference zero under absolute tolerance 0.0000001. It passes. A relative-only rule with zero reference would reject every nonzero result. Conversely, output 4 where reference is 3 cannot be excused as ordinary small rounding under those tolerances; first investigate shape, indexing and the mathematical contract.

## Exercise 3

The bound is \(0.001+0.01\times 20=0.201\). This is a chosen acceptance policy, not a universal CUDA tolerance.

## Exercise 4

Require finite values before tolerance evaluation and reject NaN or infinity unless the specification explicitly expects them.

## Exercise 5

The sum can exceed the representable range. Bound the worst-case sum or accumulate using a sufficiently wide type.

## Exercise 6

Compare every integer bin exactly and verify total count. Include empty, all-in-one-bin and out-of-range input policies; floating tolerance is unnecessary.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-006_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare every integer bin exactly and verify total count. Include empty, all-in-one-bin and out-of-range input policies; floating tolerance is unnecessary.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
