# cuda-109: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Define the shape envelope

List bounded dimensions and dtypes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define the shape envelope** is qualified there.

## Exercise 2: Reject an invalid request

Return a clear error before unsafe execution.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **reject an invalid request** is qualified there.

## Exercise 3: Separate export build and execution

Each is a separate evidence step.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate export build and execution** is qualified there.

## Exercise 4: Choose calibration data

Use representative training-side data without evaluation leakage.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose calibration data** is qualified there.

## Exercise 5: Record engine compatibility

Store runtime device and build metadata.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **record engine compatibility** is qualified there.

## Exercise 6: Compare task quality

Evaluate the same held-out examples and metrics.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare task quality** is qualified there.

## Reference observation

Declared shape envelope enforced.

The reference file is `courses/cuda/python/references/cuda-109_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
