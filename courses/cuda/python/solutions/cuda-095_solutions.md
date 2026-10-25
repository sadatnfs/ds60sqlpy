# cuda-095: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute throughput

Batch divided by completed seconds.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute throughput** is qualified there.

## Exercise 2: Separate per-item cost and request latency

Amortized cost is not latency.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate per-item cost and request latency** is qualified there.

## Exercise 3: Set both PyTorch inference controls

Use eval plus inference_mode when appropriate.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **set both PyTorch inference controls** is qualified there.

## Exercise 4: Specify TensorFlow training behavior

Pass training=False for relevant calls.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify TensorFlow training behavior** is qualified there.

## Exercise 5: Measure cold start

Include load and first execution separately.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **measure cold start** is qualified there.

## Exercise 6: Test an exported signature boundary

Reject unsupported shape or dtype explicitly.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test an exported signature boundary** is qualified there.

## Reference observation

4000 items/s with 8 ms batch latency, not 0.25 ms request latency.

The reference file is `courses/cuda/python/references/cuda-095_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
