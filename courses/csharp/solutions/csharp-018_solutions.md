# csharp-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-018_solution.cs](csharp-018_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain the element type:** The constraint guarantees comparison while the generic return preserves the concrete type. The same method returns an int or a string without object casts.

**Preserve a generic relationship:** A generic data model encodes relationships between fields independently of the values used. Swap preserves the element type, and a tie remains a valid value.

## Reason through the six tasks

1. **Predict and explain.** Predict the inferred type at each Max call.

2. **Guided modification.** Use Max with decimal values.

3. **Independent construction.** Create a generic immutable three-element container.

4. **Diagnose a defect.** Explain why an unconstrained T cannot safely call Length.

5. **Boundary evidence.** Test equal values and document whether the first or second object is returned on a tie.

6. **Transfer and justify.** Design a generic helper with the smallest useful capability constraint.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.

`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.

Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
