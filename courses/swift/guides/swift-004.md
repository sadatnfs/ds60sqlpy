# swift-004: Strings, Unicode and collection indices

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-003`

## Learning objectives

Count and slice strings by Character and index, not by assumed byte or code unit positions. The central exercise is task 3: Write a function returning the first Character as an optional value.

## Purpose and mental model

Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.

## Vocabulary and concepts

**Grapheme cluster:** A user-perceived character assembled from Unicode scalars.

**String.Index:** A valid position in a particular string.

**Substring:** A slice that may share storage with its source.

## How to run this lesson

Unicode surprises show up as runtime values, not compile errors, so predict every count in task 1 on paper before pasting Example A. Task 4 asks you to misuse an integer position: `text[1]` does not compile, because `String` has no integer subscript, and that diagnostic belongs in your evidence.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Count the right unit

Character count follows grapheme boundaries instead of byte storage.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let text = "é"
      precondition(text.count == 1)
      precondition(text.utf8.count == 2)
      let combined = "e\u{301}"
      precondition(combined.count == 1 && combined.utf8.count == 3)
    }
    print("swift-004: passed")
  }
}
```

**Observe:** Both spellings contain one Character but differ in UTF-8 bytes.

**Trace.** The first literal is the single precomposed scalar U+00E9. It forms one Character, and UTF-8 encodes it in two bytes, so the counts are 1 and 2. `combined` is the letter e followed by U+0301, the combining acute accent. Swift's grapheme rules join the two scalars into one Character, so `count` is still 1, while UTF-8 needs one byte for the e and two for the accent: 3 in total. The glyph looks the same both times; `count` follows what a reader sees, and `utf8.count` follows storage.

### Example B: Slice with a valid index

A valid index belongs to the source string and respects its representation boundaries.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let text = "A😀B"
      let firstEnd = text.index(after: text.startIndex)
      precondition(String(text[..<firstEnd]) == "A")
      precondition(String(text[firstEnd...]) == "😀B")
    }
    print("swift-004: passed")
  }
}
```

**Observe:** The split preserves the emoji as a complete Character.

**Trace.** `text` holds A, a grinning-face emoji (one scalar, four UTF-8 bytes) and B. `startIndex` points at A, and `index(after:)` moves past one whole Character, landing at the start of the emoji rather than one byte later. `text[..<firstEnd]` is the Substring containing only A, and `String(...)` copies it into new storage. `text[firstEnd...]` runs from the emoji to the end. Because the index came from `text` itself, the slice boundary cannot split the emoji's bytes.

## Exercises

1. **Predict and explain.** Predict Character and byte counts for both accent spellings.

2. **Guided modification.** Add an emoji and compare counts again.

3. **Independent construction.** Write a function returning the first Character as an optional value.

4. **Diagnose a defect.** Diagnose treating a byte offset as a String.Index.

5. **Boundary evidence.** Test empty text and a multi-scalar grapheme.

6. **Transfer and justify.** Design a text-field limit and document whether it counts bytes or visible characters.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

For the first-Character function in task 3, the decisive inputs are the empty string and a first Character built from several scalars. Empty text must return nil rather than trap on `text[text.startIndex]`. A flag emoji is two regional-indicator scalars forming one Character, so returning `text.unicodeScalars.first` gives only half of it. Compare both inputs against `text.first` before trusting your version.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Count the right unit) before changing anything, and confirm its observation: Both spellings contain one Character but differ in UTF-8 bytes.
2. Compare Example B (Slice with a valid index) with Example A and name the first line whose behavior differs. Its observation is: The split preserves the emoji as a complete Character.
3. Before opening the explanation, check your task 3 attempt (Write a function returning the first Character as an optional value) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

For the word naïve, state its Character count and explain why its UTF-8 byte count depends on how the ï was entered. Explain why an index taken from one string must not be used on another, and when you would convert a `Substring` back to `String` before storing it in a long-lived property.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Strings and Characters chapter of the Swift book covers extended grapheme clusters, counting characters, string indices and substrings.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-004: Strings, Unicode and collection indices.
Read courses/swift/guides/swift-004.md and courses/swift/lessons/swift-004.swift. Prerequisites: swift-003.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-004_solution.swift and
courses/swift/solutions/swift-004_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
