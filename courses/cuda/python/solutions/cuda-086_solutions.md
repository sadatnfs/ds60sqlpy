# cuda-086: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive fitted means

Means are [2,3].

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive fitted means** is qualified there.

## Exercise 2: Score the centered rows

Scores are [-1,1].

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **score the centered rows** is qualified there.

## Exercise 3: Add a constant column

Center to zero and define scale policy.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add a constant column** is qualified there.

## Exercise 4: Draw owners and waits

Include producer and final-consumer lifetimes.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **draw owners and waits** is qualified there.

## Exercise 5: Design train-validation separation

Fit only on the training subset.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design train-validation separation** is qualified there.

## Exercise 6: Write the capstone acceptance report

Report values tolerances timing boundaries and unsupported cases.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write the capstone acceptance report** is qualified there.

## Reference observation

Fitted means [2,3] and scores [-1,1].

The reference file is `courses/cuda/python/references/cuda-086_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
