# csharp-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-014_solution.cs](csharp-014_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Equal data with distinct identities:** Value equality and reference identity answer different questions. Equal records can be distinct objects; with preserves the previous age.

**Notice nested shared state:** The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise. Both records see the appended list item.

## Reason through the six tasks

1. **Predict and explain.** Predict record equality and reference equality separately.

2. **Guided modification.** Create a changed copy with a new name and retain the original.

3. **Independent construction.** Design an immutable coordinate using a readonly record struct.

4. **Diagnose a defect.** Diagnose a supposedly immutable history entry containing a mutable list.

5. **Boundary evidence.** Compare records whose nested collections contain equal values but have different identities.

6. **Transfer and justify.** Choose identity-based or data-based equality for an order and explain how updates affect collection membership.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.

`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.

Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
