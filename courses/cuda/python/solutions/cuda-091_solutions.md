# cuda-091: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: State cross-correlation convention

Write the exact index formula.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **state cross-correlation convention** is qualified there.

## Exercise 2: Calculate output length

Valid length is input minus kernel plus one.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate output length** is qualified there.

## Exercise 3: Count layout conversion cost

Include conversions in complete latency.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count layout conversion cost** is qualified there.

## Exercise 4: Compare forward and backward

Both computations matter for training.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare forward and backward** is qualified there.

## Exercise 5: Explain algorithm warmup

Algorithm choice may need startup work.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain algorithm warmup** is qualified there.

## Exercise 6: Design two shape cases

Use a narrow and wider batch with unchanged semantics.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design two shape cases** is qualified there.

## Reference observation

Valid cross-correlation [-1,-1,-1]; conversion amortization depends on reuse.

The reference file is `courses/cuda/python/references/cuda-091_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
