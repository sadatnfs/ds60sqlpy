# swift-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-013_solution.swift](swift-013_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe shared identity:** The copied reference still identifies one object, even though both bindings are constant. Both names observe the same increment.

**Equal state need not mean identity:** Object identity answers a different question from comparing a property value. Two fresh counters have equal state but distinct identities.

## Reason through the six tasks

1. **Predict and explain.** Draw references before and after assignment.

2. **Guided modification.** Create a separate object and mutate only one.

3. **Independent construction.** Choose class or struct for a shared connection coordinator and a coordinate value.

4. **Diagnose a defect.** Diagnose expecting class assignment to create an independent snapshot.

5. **Boundary evidence.** Test equal property values on distinct objects.

6. **Transfer and justify.** Explain whether a shared class needs synchronization before use from concurrent tasks.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.

`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.

Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
