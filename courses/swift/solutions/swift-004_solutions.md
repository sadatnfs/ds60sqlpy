# swift-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-004_solution.swift](swift-004_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count the right unit:** Character count follows grapheme boundaries instead of byte storage. Both spellings contain one Character but differ in UTF-8 bytes.

**Slice with a valid index:** A valid index belongs to the source string and respects its representation boundaries. The split preserves the emoji as a complete Character.

## Reason through the six tasks

1. **Predict and explain.** Predict Character and byte counts for both accent spellings.

2. **Guided modification.** Add an emoji and compare counts again.

3. **Independent construction.** Write a function returning the first Character as an optional value.

4. **Diagnose a defect.** Diagnose treating a byte offset as a String.Index.

5. **Boundary evidence.** Test empty text and a multi-scalar grapheme.

6. **Transfer and justify.** Design a text-field limit and document whether it counts bytes or visible characters.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.

`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.

Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
