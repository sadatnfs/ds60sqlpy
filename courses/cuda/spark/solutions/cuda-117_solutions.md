# cuda-117: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate both counts

Row count 3 and non-null count 2.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate both counts** is qualified there.

## Exercise 2: Handle all-null aggregate

Follow Spark SQL null-result semantics.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **handle all-null aggregate** is qualified there.

## Exercise 3: Compare decimal values

Use exact decimal type and scale.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare decimal values** is qualified there.

## Exercise 4: Name timestamp timezone

Set and record session timezone.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name timestamp timezone** is qualified there.

## Exercise 5: Choose float tolerances

Tie tolerance to dtype algorithm and scale.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose float tolerances** is qualified there.

## Exercise 6: Design ordered result comparison

Sort by stable keys without erasing duplicate rows.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design ordered result comparison** is qualified there.

## Reference observation

Rows 3, non-null 2, sum 7 and exact decimal 3.30.

The reference file is `courses/cuda/spark/references/cuda-117_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
