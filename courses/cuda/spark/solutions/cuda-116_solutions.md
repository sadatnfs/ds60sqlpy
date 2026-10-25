# cuda-116: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify fallback versus unavailable device

Fallback is per supported execution environment.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify fallback versus unavailable device** is qualified there.

## Exercise 2: Find an unsupported expression

Consult operator type and expression rules.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find an unsupported expression** is qualified there.

## Exercise 3: Count boundary costs

Include representation and transfer costs.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count boundary costs** is qualified there.

## Exercise 4: Rewrite an opaque function declaratively

Use built-in expressions only when equivalent.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **rewrite an opaque function declaratively** is qualified there.

## Exercise 5: Preserve edge semantics

Test nulls overflow strings and timestamps.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **preserve edge semantics** is qualified there.

## Exercise 6: Design a mixed-plan report

List each reason and observed transition.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a mixed-plan report** is qualified there.

## Reference observation

CPU-only baseline and per-operator fallback are modeled separately.

The reference file is `courses/cuda/spark/references/cuda-116_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
