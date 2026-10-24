# swift-004: Strings, Unicode and collection indices

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-003`

## Learning objectives

Write a function returning the first Character as an optional value. Then design a text-field limit and document whether it counts bytes or visible characters.

## Purpose and mental model

Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.

## Vocabulary and concepts

**Grapheme cluster:** A user-perceived character assembled from Unicode scalars.

**String.Index:** A valid position in a particular string.

**Substring:** A slice that may share storage with its source.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Predict Character and byte counts for both accent spellings.

2. **Guided modification.** Add an emoji and compare counts again.

3. **Independent construction.** Write a function returning the first Character as an optional value.

4. **Diagnose a defect.** Diagnose treating a byte offset as a String.Index.

5. **Boundary evidence.** Test empty text and a multi-scalar grapheme.

6. **Transfer and justify.** Design a text-field limit and document whether it counts bytes or visible characters.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Grapheme cluster, String.Index, Substring without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
