# cuda-096: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute the validation metric

Mean squared errors 0,1,1 give 2/3.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute the validation metric** is qualified there.

## Exercise 2: Write the sample ledger

Track train validation and consumed counts.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write the sample ledger** is qualified there.

## Exercise 3: Define a memory budget

Include weights state activations and reserve separately.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define a memory budget** is qualified there.

## Exercise 4: Design a restart comparison

Compare uninterrupted and resumed steps.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a restart comparison** is qualified there.

## Exercise 5: Choose one optimization

Tie it to a measured bottleneck.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose one optimization** is qualified there.

## Exercise 6: State pending hardware evidence

Mark CPU and GPU results independently.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **state pending hardware evidence** is qualified there.

## Reference observation

Three examples, MSE 2/3, GPU verification explicitly false.

The reference file is `courses/cuda/python/references/cuda-096_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
