# cuda-098: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive the input VJP

Multiply upstream by a and the positive mask.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive the input VJP** is qualified there.

## Exercise 2: Derive bias gradient

Sum masked upstream values.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive bias gradient** is qualified there.

## Exercise 3: Run finite differences away from a kink

Use symmetric perturbations and a suitable epsilon.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **run finite differences away from a kink** is qualified there.

## Exercise 4: Explain a failed kink gradcheck

The derivative is not unique at the boundary.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain a failed kink gradcheck** is qualified there.

## Exercise 5: Specify higher-order support

Do not imply it from first-order success.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify higher-order support** is qualified there.

## Exercise 6: Compare each framework reference

Compare native forward and backward independently.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare each framework reference** is qualified there.

## Reference observation

Finite-difference derivative approximately 2 and bias VJP 3.

The reference file is `courses/cuda/python/references/cuda-098_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
