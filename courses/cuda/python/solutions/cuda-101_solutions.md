# cuda-101: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count low-rank parameters

Rank times sum of dimensions.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count low-rank parameters** is qualified there.

## Exercise 2: Include base storage

Base parameters are not deleted.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **include base storage** is qualified there.

## Exercise 3: Inspect optimizer membership

Only intended trainable tensors belong in optimizer state.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **inspect optimizer membership** is qualified there.

## Exercise 4: Compare sequence-length budgets

Attention intermediates and caches grow with sequence geometry.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare sequence-length budgets** is qualified there.

## Exercise 5: Design tiny offline training

Use generated tokens and bounded steps.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design tiny offline training** is qualified there.

## Exercise 6: Define held-out evaluation

Keep validation separate from fitting and tuning.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define held-out evaluation** is qualified there.

## Reference observation

Base 1,048,576 and adapter 16,384 parameters.

The reference file is `courses/cuda/python/references/cuda-101_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
