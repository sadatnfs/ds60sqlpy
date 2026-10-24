# rust-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-020_solution.rs](rust-020_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume a transformation recipe:** Copied turns referenced integers into independent small values before filtering and mapping. The recipe selects and transforms while retaining the borrowed source.

**Observe iterator progress:** Calling next again does not restart the source automatically. The iterator advances and eventually exhausts.

## Reason through the six tasks

1. **Predict and explain.** Identify adapters and the final consumer.

2. **Guided modification.** Add a take limit and predict how much work is demanded.

3. **Independent construction.** Write a borrowed transformation returning a collected result.

4. **Diagnose a defect.** Diagnose constructing a lazy map and expecting it to execute immediately.

5. **Boundary evidence.** Test empty input and a partially consumed iterator.

6. **Transfer and justify.** Choose iter, iter_mut or into_iter for three operations and justify ownership.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.

`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.

Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
