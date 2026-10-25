# cuda-030: explanatory solutions

## Mechanism review

A minimal reproducer removes unrelated work while preserving the failure. For a shape-dependent bug, reduce dimensions and data complexity independently, then retain the smallest case that still fails. Add source line information and stage-specific checks before interpreting a large trace. Debug builds change optimization and resource usage; a disappearing failure is a clue, not proof of a fix. A device fault can make further operations in a context unreliable. Preserve source and diagnostics before restarting a process. Device reset and shared-engine recovery belong to the resource owner, not an automatic learner-code repair path.

The separate [CPU reference](../references/cuda-030_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A hypothetical bad predicate i<=n fails at lengths 1,33 and 1,001. Reduce it to length one, where index one is already invalid. This gives a tiny regression fixture and a direct explanation. A giant dataset is unnecessary to show the underlying off-by-one error.

## Exercise 2

A recorded timeout contains 'kernel submitted; completion not observed'. It does not contain a correct numerical result. Classify it as incomplete execution and inspect boundedness/dependencies. Do not add an arbitrary sleep and call the change a synchronization fix.

## Exercise 3

Learner source, exact input/shape, compile and runtime diagnostics, operation phase, environment identity and whether output validation completed.

## Exercise 4

It destroys learner state without identifying the defect and does not repair the kernel's ordering or bounds.

## Exercise 5

Restore one removed dimension or input condition at a time and document the threshold. Do not claim a fix from an unrelated passing case.

## Exercise 6

Keep at least one exact failing tail shape, a nearby divisible control and an empty/singleton boundary, checking full outputs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-030_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep at least one exact failing tail shape, a nearby divisible control and an empty/singleton boundary, checking full outputs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
