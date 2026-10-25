# cuda-127: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive expected revenue

A revenue is \((2+4)\times10=60\), and B revenue is \(3\times20=60\).

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive expected revenue** is qualified there.

## Exercise 2: Write Scala expressions

Use explicit schema join and groupBy.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write Scala expressions** is qualified there.

## Exercise 3: Write PySpark expressions

Match those operations and sort output.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write PySpark expressions** is qualified there.

## Exercise 4: Test duplicate dimension keys

Reject or explicitly accept multiplicity.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test duplicate dimension keys** is qualified there.

## Exercise 5: Capture executed GPU evidence

Require plans metrics and equality on actual hardware.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **capture executed GPU evidence** is qualified there.

## Exercise 6: Prepare a balanced capstone report

Include CPU functionality and pending GPU limitations separately.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **prepare a balanced capstone report** is qualified there.

## Reference observation

Sorted revenue [(A,60),(B,60)].

The reference file is `courses/cuda/spark/references/cuda-127_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
