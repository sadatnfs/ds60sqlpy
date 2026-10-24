# csharp-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-012_solution.cs](csharp-012_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Copy a value:** The struct contains only integer fields, so its copied state is independently mutable. Changing the copied point leaves the original X at 2.

**Share an object identity:** Passing or assigning a reference by value does not clone the referenced object. Both references observe the same counter increment.

## Reason through the six tasks

1. **Predict and explain.** Draw the values and references after each assignment.

2. **Guided modification.** Make a separate Counter instance and compare identity with equal property values.

3. **Independent construction.** Choose a representation for a coordinate and for a shared session, explaining the difference.

4. **Diagnose a defect.** Diagnose expecting assignment of a class variable to produce a deep copy.

5. **Boundary evidence.** Place a mutable list inside a struct and explain which part of the copied value remains shared.

6. **Transfer and justify.** Design a data boundary that prevents callers from mutating an internal collection.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.

`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.

A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
