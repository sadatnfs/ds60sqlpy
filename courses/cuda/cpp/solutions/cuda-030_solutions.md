# cuda-030: explanatory solutions

## Mechanism review

A minimal reproducer removes unrelated work while preserving the failure. For a shape-dependent bug, reduce dimensions and data complexity independently, then retain the smallest case that still fails. Add source line information and stage-specific checks before interpreting a large trace. Debug builds change optimization and resource usage; a disappearing failure is a clue, not proof of a fix. A device fault can make further operations in a context unreliable. Preserve source and diagnostics before restarting a process. Device reset and shared-engine recovery belong to the resource owner, not an automatic learner-code repair path.

The separate [CPU reference](../references/cuda-030_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A hypothetical bad predicate i<=n fails at lengths 1,33 and 1,001. Reduce it to length one, where index one is already invalid. This gives a tiny regression fixture and a direct explanation. A giant dataset is unnecessary to show the underlying off-by-one error.

**Approach:** Shrink the failing inputs to length one, where i <= n reaches index 1.

**Why it is correct:** A length-one array has only index 0, so the bad predicate already fails.

**A plausible wrong approach:** Debugging the 1,001-element case first buries one bad index in a large trace.

**How to verify:** The reference asserts invalid_indices(1) == [1] and invalid_indices(33) == [33].

## Exercise 2

A recorded timeout contains 'kernel submitted; completion not observed'. It does not contain a correct numerical result. Classify it as incomplete execution and inspect boundedness/dependencies. Do not add an arbitrary sleep and call the change a synchronization fix.

**Approach:** Classify the record as incomplete execution and inspect loop bounds and waits.

**Why it is correct:** Submitted without observed completion means no result exists to validate.

**A plausible wrong approach:** Adding a sleep before reading output may hide the hang without fixing the dependency.

**How to verify:** The reference receipt marks completed and validated False; keep that classification.

## Exercise 3

Learner source, exact input/shape, compile and runtime diagnostics, operation phase, environment identity and whether output validation completed.

**Approach:** Save source, exact input and shape, compile and runtime diagnostics, phase, environment and validation status.

**Why it is correct:** These fields let someone reproduce the failure after the worker is replaced.

**A plausible wrong approach:** Restarting first and collecting later loses the diagnostics tied to the failure.

**How to verify:** Restore the saved fields on a fresh worker and confirm the same failure appears.

## Exercise 4

It destroys learner state without identifying the defect and does not repair the kernel's ordering or bounds.

**Approach:** Leave learner volumes alone and investigate the kernel failure directly.

**Why it is correct:** Deleting state removes evidence and work without touching the defect.

**A plausible wrong approach:** Wiping everything and seeing a clean start mistakes a reset for a repair.

**How to verify:** Rerun the minimal failing case after any change and confirm it passes.

## Exercise 5

Restore one removed dimension or input condition at a time and document the threshold. Do not claim a fix from an unrelated passing case.

**Approach:** Restore one removed dimension or condition at a time until the failure returns.

**Why it is correct:** This finds the threshold where the bug appears.

**A plausible wrong approach:** Declaring a fix because a smaller unrelated case passes ignores the original trigger.

**How to verify:** Record the threshold and add that exact case as a test.

## Exercise 6

Keep at least one exact failing tail shape, a nearby divisible control and an empty/singleton boundary, checking full outputs.

**Approach:** Keep an exact failing tail shape, a nearby divisible control and empty and singleton inputs.

**Why it is correct:** The control separates tail logic from general logic, and boundaries catch the edges.

**A plausible wrong approach:** Testing only the divisible size passes while the tail bug remains.

**How to verify:** Confirm the test fails on the old code and passes on the fix.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-030_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep at least one exact failing tail shape, a nearby divisible control and an empty/singleton boundary, checking full outputs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
