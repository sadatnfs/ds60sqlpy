# cuda-087: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive the scalar gradient

The mean derivative is average of 2*x*(w*x-y).

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive the scalar gradient** is qualified there.

## Exercise 2: Calculate the update

Weight becomes 1.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate the update** is qualified there.

## Exercise 3: Compare sum and mean

Sum scales by batch size.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare sum and mean** is qualified there.

## Exercise 4: Inspect every tensor device

Include parameters inputs targets and optimizer tensors.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **inspect every tensor device** is qualified there.

## Exercise 5: Write equal PyTorch and TensorFlow contracts

Use identical data initial state reduction and rate.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write equal PyTorch and TensorFlow contracts** is qualified there.

## Exercise 6: Distinguish correctness and performance

Time only after output and gradient agreement.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish correctness and performance** is qualified there.

## Reference observation

Loss 10, gradient-10, new weight 1.

The reference file is `courses/cuda/python/references/cuda-087_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
