# cuda-108: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute grouped sums

Ignore null only under the stated aggregate contract.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute grouped sums** is qualified there.

## Exercise 2: Distinguish null and zero

Zero contributes a numeric value.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish null and zero** is qualified there.

## Exercise 3: Define category mapping

Fit once and reserve an unknown category if needed.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define category mapping** is qualified there.

## Exercise 4: Preserve row identity

Carry a stable key through transformations.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **preserve row identity** is qualified there.

## Exercise 5: Count conversion bytes

Count masks dtype conversions and host-device copies.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count conversion bytes** is qualified there.

## Exercise 6: Distinguish cuDF from Spark acceleration

One is a dataframe library and the other integrates Spark physical execution.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish cuDF from Spark acceleration** is qualified there.

## Reference observation

Grouped sums A 2, B 5 and row count A 2.

The reference file is `courses/cuda/python/references/cuda-108_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
