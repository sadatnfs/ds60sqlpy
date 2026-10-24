# swift-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-022_solution.swift](swift-022_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe weak lifetime:** The example observes a controlled ownership boundary without retaining the target accidentally. The weak observer becomes nil after the last strong reference is removed.

**Break a parent-child cycle:** The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists. The child survives independently without retaining its parent.

## Reason through the six tasks

1. **Predict and explain.** Draw strong and weak arrows in both examples.

2. **Guided modification.** Add a temporary second strong owner and predict when the weak observer clears.

3. **Independent construction.** Design a weak delegate relationship.

4. **Diagnose a defect.** Diagnose an object retaining a closure that strongly captures the same object.

5. **Boundary evidence.** Test a callback after its weak owner has disappeared.

6. **Transfer and justify.** Choose weak or unowned for a relationship and justify the lifetime guarantee required.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.

`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.

Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
