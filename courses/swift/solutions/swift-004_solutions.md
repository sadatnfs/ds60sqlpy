# swift-004: explanation and comparison

Reference program: [swift-004_solution.swift](swift-004_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Count the right unit:** Character count follows grapheme boundaries instead of byte storage. Both spellings contain one Character but differ in UTF-8 bytes.

**Slice with a valid index:** A valid index belongs to the source string and respects its representation boundaries. The split preserves the emoji as a complete Character.

## Task answers

### Task 1: Predict and explain

Predict Character and byte counts for both accent spellings.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let precomposed = "\u{E9}"
let combined = "e\u{301}"
precondition(precomposed.count == 1 && combined.count == 1)
precondition(precomposed.utf8.count == 2 && combined.utf8.count == 3)
precondition(precomposed.unicodeScalars.count == 1 && combined.unicodeScalars.count == 2)
precondition(precomposed == combined)
```

**Observe:** Both spellings are one Character; the precomposed one is 2 UTF-8 bytes and 1 scalar, the combined one 3 bytes and 2 scalars, and they compare equal.

count measures grapheme clusters, while utf8 and unicodeScalars measure the encoding. String equality uses canonical equivalence, so the two spellings are the same text.

### Task 2: Guided modification

Add an emoji and compare counts again.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let text = "\u{E9}😀"
precondition(text.count == 2)
precondition(text.utf8.count == 2 + 4)
precondition(text.utf16.count == 1 + 2)
```

**Observe:** Adding 😀 makes 2 Characters, 6 UTF-8 bytes and 3 UTF-16 code units.

The emoji lies outside the Basic Multilingual Plane, so it takes 4 UTF-8 bytes and a UTF-16 surrogate pair while still being a single Character.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let text = "A😀B"
let byteOffset = Array(text.utf8).firstIndex(of: UInt8(ascii: "B"))!
precondition(byteOffset == 5)
let index = text.firstIndex(of: "B")!
precondition(text.distance(from: text.startIndex, to: index) == 2)
precondition(text[index] == "B")
```

**Observe:** B is at byte offset 5 but only 2 Characters from the start; the String.Index found in the same string reads B.

A byte offset counts UTF-8 units, not Characters, and String has no Int subscript. Deriving the index from the string itself (firstIndex or index(after:)) is what keeps the emoji whole.

### Task 5: Boundary evidence

Test empty text and a multi-scalar grapheme.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let empty = ""
precondition(empty.first == nil && empty.isEmpty)
let flag = "🇺🇸"
precondition(flag.count == 1 && flag.unicodeScalars.count == 2)
precondition(flag.first == "🇺🇸")
let family = "👨‍👩‍👧"
precondition(family.count == 1 && family.unicodeScalars.count == 5)
```

**Observe:** Empty text has no first Character; the flag is one Character of 2 scalars and the family emoji one Character of 5 scalars.

Regional indicator pairs and zero-width-joiner sequences are single grapheme clusters, so first returns the whole cluster and empty text returns nil rather than an error.

### Task 6: Transfer and justify

Design a text-field limit and document whether it counts bytes or visible characters.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A writes the same visible letter two ways, as the precomposed `é` and as `e` followed by the combining acute accent, and checks Character and UTF-8 counts for each. Example B builds a `String.Index` with `index(after:)` and slices `A😀B` around it. The task 3 answer returns the first Character as an optional.

**Why it is correct.** Swift's `count` walks grapheme clusters, so both spellings count as one Character, while their UTF-8 views hold 2 and 3 bytes. The index after `startIndex` lands after `A`, a valid boundary, so the prefix is `A` and the suffix keeps the four-byte emoji whole as `😀B`. An empty string has no first Character, so the answer returns nil.

**A plausible wrong approach.** Treating the second byte as position 1 and slicing by integer offsets is a common carryover from other languages. Swift does not allow `text[1]` on a String, and a byte offset into `😀` would split a scalar. Using `utf8.count` as a text-field limit would also reject `e\u{301}` too early.

**How to verify.** For task 3, expect `😀` from `😀B` and nil from an empty string. Add `print(Array("e\u{301}".unicodeScalars).count)` in a scratch pad and confirm it prints 2, showing two scalars inside one Character.

## Mechanism and diagnostic reasoning

Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.

`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.

Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

## Review before continuing

Run the reference and confirm it prints `swift-004: passed`, then rerun the guide's counterexample.
