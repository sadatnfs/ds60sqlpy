# cuda-090: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate scaled and unscaled values

Apply inverse scale exactly once.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate scaled and unscaled values** is qualified there.

## Exercise 2: Explain overflow detection

Skip or adjust updates according to the supported scaler when nonfinite.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain overflow detection** is qualified there.

## Exercise 3: Place clipping correctly

Unscale before clipping.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **place clipping correctly** is qualified there.

## Exercise 4: Compare fp16 and bf16 concepts

Their exponent and mantissa allocations differ.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare fp16 and bf16 concepts** is qualified there.

## Exercise 5: Design a full-precision baseline

Use same initialization batch and loss.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a full-precision baseline** is qualified there.

## Exercise 6: Record quality and throughput separately

A speed improvement cannot excuse numerical failure.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **record quality and throughput separately** is qualified there.

## Reference observation

Correct gradient 0.5; incorrect clipping order yields 0.0009765625.

The reference file is `courses/cuda/python/references/cuda-090_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
