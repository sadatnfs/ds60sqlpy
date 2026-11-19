# swift-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-004_solution.swift](swift-004_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count the right unit:** Character count follows grapheme boundaries instead of byte storage. Both spellings contain one Character but differ in UTF-8 bytes.

**Slice with a valid index:** A valid index belongs to the source string and respects its representation boundaries. The split preserves the emoji as a complete Character.

## Task answers

### Task 1: Predict and explain

Predict Character and byte counts for both accent spellings.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Character count follows grapheme boundaries instead of byte storage. Both spellings contain one Character but differ in UTF-8 bytes.

### Task 2: Guided modification

Add an emoji and compare counts again.

No separate reference answer has been written for this task. Start from Example B: A valid index belongs to the source string and respects its representation boundaries. The split preserves the emoji as a complete Character.

### Task 3: Independent construction

Write a function returning the first Character as an optional value.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func firstCharacter(_ text: String) -> Character? {
  text.first
}
precondition(firstCharacter("😀B") == "😀")
precondition(firstCharacter("") == nil)
```

**Observe:** The first Character of 😀B is 😀, and empty text gives nil.

A Character is a full grapheme cluster, so the emoji is one element, and the optional result keeps empty text distinct from any character.

### Task 4: Diagnose a defect

Diagnose treating a byte offset as a String.Index.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

### Task 5: Boundary evidence

Test empty text and a multi-scalar grapheme.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Count the right unit) and Example B (Slice with a valid index).

### Task 6: Transfer and justify

Design a text-field limit and document whether it counts bytes or visible characters.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Grapheme cluster**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.

`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.

Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

## Review before continuing

Run the reference and confirm that it prints `swift-004: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
