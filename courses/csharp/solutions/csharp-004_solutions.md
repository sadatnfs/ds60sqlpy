# csharp-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-004_solution.cs](csharp-004_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Immutable transformations:** Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture. The original remains data while the result is DATA.

**Choose the counting unit:** The fixture disproves the assumption that Length is a universal character count. One scalar occupies two UTF-16 units and four UTF-8 bytes.

## Task answers

### Task 1: Predict and explain

Predict both string values after ToUpperInvariant and explain ownership of the result.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture. The original remains data while the result is DATA.

### Task 2: Guided modification

Build an interpolated label containing a count and a unit.

No separate reference answer has been written for this task. Start from Example B: The fixture disproves the assumption that Length is a universal character count. One scalar occupies two UTF-16 units and four UTF-8 bytes.

### Task 3: Independent construction

Implement case-insensitive machine-key comparison with an explicit policy.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool SameKey(string left, string right) {
  return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
}
Check(SameKey("Report-ID", "report-id"), "case-insensitive match");
Check(!SameKey("report-id", "report_id"), "different characters differ");
Check(SameKey("i", "I"), "ordinal policy, no culture rules");
```

**Observe:** Keys that differ only by ASCII case match; a different separator does not.

OrdinalIgnoreCase compares machine keys by code unit with simple case folding, so the result does not depend on the current culture.

### Task 4: Diagnose a defect

Diagnose code that takes one char from the emoji and assumes it is a complete symbol.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

### Task 5: Boundary evidence

Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Immutable transformations) and Example B (Choose the counting unit).

### Task 6: Transfer and justify

Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Code unit**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.

`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.

Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

## Review before continuing

Run the reference and confirm that it prints `csharp-004: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
