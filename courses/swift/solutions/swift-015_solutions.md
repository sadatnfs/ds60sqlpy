# swift-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-015_solution.swift](swift-015_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Transform a sequence:** The transformation is pure and its element-to-element relationship is visible. Map creates transformed values while retaining the original array.

**Freeze a captured value deliberately:** This differs from a closure observing a mutable captured variable later. The explicit capture list retains factor 2 for the closure.

## Reason through the six tasks

1. **Predict and explain.** Predict the mapped result and unchanged source.

2. **Guided modification.** Filter even numbers before mapping.

3. **Independent construction.** Write a function accepting a transformation closure.

4. **Diagnose a defect.** Diagnose a closure whose captured mutable state changes before later execution.

5. **Boundary evidence.** Test empty arrays and a closure that returns an optional.

6. **Transfer and justify.** Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.

`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.

An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
