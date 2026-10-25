# cuda-115: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Draw logical versus physical plan

Logical nodes describe intent and physical nodes choose execution.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **draw logical versus physical plan** is qualified there.

## Exercise 2: Mark GPU candidate nodes

Use actual plugin names from the selected release.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **mark GPU candidate nodes** is qualified there.

## Exercise 3: Locate transitions

Each transition may copy or change representation.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **locate transitions** is qualified there.

## Exercise 4: Explain lazy evaluation

An action is required for work.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain lazy evaluation** is qualified there.

## Exercise 5: Compare initial and final AQE plan

Inspect the final executed plan.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare initial and final AQE plan** is qualified there.

## Exercise 6: Choose operator metrics

Use rows batches time spill and device observations together.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose operator metrics** is qualified there.

## Reference observation

Synthetic plan has two GPU nodes and two backend transitions.

The reference file is `courses/cuda/spark/references/cuda-115_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
