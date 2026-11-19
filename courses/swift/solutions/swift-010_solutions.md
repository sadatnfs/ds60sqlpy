# swift-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-010_solution.swift](swift-010_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve absence and zero:** Optional lookup prevents missing information from being confused with a stored value. Pear is present with zero and apple is absent.

**Deduplicate and order deliberately:** Set semantics establish uniqueness while sorting separately establishes order. Duplicate red is not inserted and sorted output is deterministic.

## Task answers

### Task 1: Predict and explain

Explain the optional result of each dictionary lookup.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Optional lookup prevents missing information from being confused with a stored value. Pear is present with zero and apple is absent.

### Task 2: Guided modification

Count repeated tags using the default-value subscript.

No separate reference answer has been written for this task. Start from Example B: Set semantics establish uniqueness while sorting separately establishes order. Duplicate red is not inserted and sorted output is deterministic.

### Task 3: Independent construction

Build a unique sorted list of accepted inventory names.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let rows = ["pear", "apple", "pear", "", "fig"]
let names = Set(rows.filter { !$0.isEmpty }).sorted()
precondition(names == ["apple", "fig", "pear"])
```

**Observe:** The accepted names are apple, fig and pear, each once and sorted.

Empty names are rejected first, the Set removes duplicates, and sorted() gives a stable order that does not depend on hashing.

### Task 4: Diagnose a defect

Diagnose persisting hashValue as a cross-run identifier.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

### Task 5: Boundary evidence

Test missing, present-zero and duplicate keys.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve absence and zero) and Example B (Deduplicate and order deliberately).

### Task 6: Transfer and justify

Design a custom Hashable key using only stable identity fields.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Hashable**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.

`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.

Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

## Review before continuing

Run the reference and confirm that it prints `swift-010: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
