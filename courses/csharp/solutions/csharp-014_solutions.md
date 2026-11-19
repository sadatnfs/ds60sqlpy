# csharp-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-014_solution.cs](csharp-014_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Equal data with distinct identities:** Value equality and reference identity answer different questions. Equal records can be distinct objects; with preserves the previous age.

**Notice nested shared state:** The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise. Both records see the appended list item.

## Task answers

### Task 1: Predict and explain

Predict record equality and reference equality separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Value equality and reference identity answer different questions. Equal records can be distinct objects; with preserves the previous age.

### Task 2: Guided modification

Create a changed copy with a new name and retain the original.

No separate reference answer has been written for this task. Start from Example B: The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise. Both records see the appended list item.

### Task 3: Independent construction

Design an immutable coordinate using a readonly record struct.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Record** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose a supposedly immutable history entry containing a mutable list.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

### Task 5: Boundary evidence

Compare records whose nested collections contain equal values but have different identities.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Equal data with distinct identities) and Example B (Notice nested shared state).

### Task 6: Transfer and justify

Choose identity-based or data-based equality for an order and explain how updates affect collection membership.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Record**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.

`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.

Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

## Review before continuing

Run the reference and confirm that it prints `csharp-014: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
