# csharp-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-020_solution.cs](csharp-020_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe query timing:** Constructing Where does not copy the source values. The deferred query sees the subsequently appended 3.

**Capture a stable result:** Materialization creates a deliberate temporal boundary while preserving the original list separately. The earlier snapshot contains only 2 while a new projection sees three values.

## Reason through the six tasks

1. **Predict and explain.** Predict whether adding an item before enumeration affects query and snapshot.

2. **Guided modification.** Add a projection from integers to labeled strings.

3. **Independent construction.** Build a deterministic report selecting, transforming and ordering records.

4. **Diagnose a defect.** Diagnose a query with a side-effect counter enumerated twice.

5. **Boundary evidence.** Test empty input and a filter matching no rows.

6. **Transfer and justify.** Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.

`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.

LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
