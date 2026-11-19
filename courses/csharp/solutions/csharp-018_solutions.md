# csharp-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-018_solution.cs](csharp-018_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain the element type:** The constraint guarantees comparison while the generic return preserves the concrete type. The same method returns an int or a string without object casts.

**Preserve a generic relationship:** A generic data model encodes relationships between fields independently of the values used. Swap preserves the element type, and a tie remains a valid value.

## Task answers

### Task 1: Predict and explain

Predict the inferred type at each Max call.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The constraint guarantees comparison while the generic return preserves the concrete type. The same method returns an int or a string without object casts.

### Task 2: Guided modification

Use Max with decimal values.

No separate reference answer has been written for this task. Start from Example B: A generic data model encodes relationships between fields independently of the values used. Swap preserves the element type, and a tie remains a valid value.

### Task 3: Independent construction

Create a generic immutable three-element container.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Type parameter** and the lesson notes.

### Task 4: Diagnose a defect

Explain why an unconstrained T cannot safely call Length.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

### Task 5: Boundary evidence

Test equal values and document whether the first or second object is returned on a tie.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Retain the element type) and Example B (Preserve a generic relationship).

### Task 6: Transfer and justify

Design a generic helper with the smallest useful capability constraint.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Type parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.

`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.

Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

## Review before continuing

Run the reference and confirm that it prints `csharp-018: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
