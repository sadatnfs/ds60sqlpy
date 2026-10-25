# cuda-071: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Identify the timing boundary

Completion must be inside the interval when timing finished work.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify the timing boundary** is qualified there.

## Exercise 2: Compute the median

Median is eleven.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute the median** is qualified there.

## Exercise 3: Add transfer cost

Include both transfers for end-to-end latency.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add transfer cost** is qualified there.

## Exercise 4: Separate first-call compile time

Report cold and warm distributions separately.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate first-call compile time** is qualified there.

## Exercise 5: Design equal-work comparison

Use same data and tolerances.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design equal-work comparison** is qualified there.

## Exercise 6: Explain why CPU trace is not a benchmark

The supplied times are invented teaching observations.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain why CPU trace is not a benchmark** is qualified there.

## Reference observation

Median 11 ms and maximum 100 ms, from synthetic trace data.

The reference file is `courses/cuda/python/references/cuda-071_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
