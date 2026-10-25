# cuda-122: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute transfer lower bound

Bytes divided by effective bandwidth.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute transfer lower bound** is qualified there.

## Exercise 2: Identify local versus network time

Measure the complete stage.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify local versus network time** is qualified there.

## Exercise 3: Explain pre-aggregation

Combine only when mathematical semantics allow.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain pre-aggregation** is qualified there.

## Exercise 4: List transport qualification

Verify devices topology libraries and real traffic.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **list transport qualification** is qualified there.

## Exercise 5: Separate startup settings

Some shuffle choices require fresh executors.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate startup settings** is qualified there.

## Exercise 6: Design a bounded shuffle comparison

Use identical partitioned fixtures and capture bytes spills and output.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a bounded shuffle comparison** is qualified there.

## Reference observation

Ten-second payload lower bound;50 ms kernel saving is below 1 percent of it.

The reference file is `courses/cuda/spark/references/cuda-122_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
