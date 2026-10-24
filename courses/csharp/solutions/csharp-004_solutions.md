# csharp-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-004_solution.cs](csharp-004_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Immutable transformations:** Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture. The original remains data while the result is DATA.

**Choose the counting unit:** The fixture disproves the assumption that Length is a universal character count. One scalar occupies two UTF-16 units and four UTF-8 bytes.

## Reason through the six tasks

1. **Predict and explain.** Predict both string values after ToUpperInvariant and explain ownership of the result.

2. **Guided modification.** Build an interpolated label containing a count and a unit.

3. **Independent construction.** Implement case-insensitive machine-key comparison with an explicit policy.

4. **Diagnose a defect.** Diagnose code that takes one char from the emoji and assumes it is a complete symbol.

5. **Boundary evidence.** Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.

6. **Transfer and justify.** Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.

`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.

Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
