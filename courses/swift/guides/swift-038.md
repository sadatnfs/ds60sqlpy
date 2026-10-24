# swift-038: Result builders and declarative composition

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-037`

## Learning objectives

Build a small report declaration using the existing builder. Then explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.

## Purpose and mental model

A result builder transforms a restricted-looking block of expressions into calls that combine intermediate results. SwiftUI uses this language feature to express view composition, but the feature itself is part of Swift and can be taught without Apple frameworks. Declarative syntax still has ordinary type and control-flow rules underneath.

Build only the operations the small language needs. Supporting conditionals, loops and optionals requires corresponding builder methods. A result builder should make a domain clearer rather than obscure evaluation or failure. The portable fixture constructs a list of report sections, while the later app project uses SwiftUI's own ViewBuilder.

## Vocabulary and concepts

**Result builder:** A compile-time transformation for structured expression composition.

**Declarative composition:** Describing a result structure rather than manual assembly steps.

**Intermediate result:** A value produced by one expression before combination.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`@resultBuilder` marks the builder. buildBlock combines expressions and buildOptional handles an if without else. A function parameter annotated with the builder accepts the transformed closure.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Compose report sections

The builder supplies the combining mechanism; the block supplies domain content.

```swift
import Foundation

@resultBuilder enum SectionBuilder { static func buildExpression(_ value: String) -> [String] { [value] }; static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }; static func buildOptional(_ component: [String]?) -> [String] { component ?? [] } }
func sections(@SectionBuilder _ content: () -> [String]) -> [String] { content() }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let report = sections { "Overview"; "Details" }
            precondition(report == ["Overview", "Details"])
        }
        print("swift-038: passed")
    }
}
```

**Observe:** Two expressions become an ordered array of sections.

### Example B: Include a conditional section

The buildOptional method gives the conditional branch an explicit combination rule.

```swift
import Foundation

@resultBuilder enum SectionBuilder { static func buildExpression(_ value: String) -> [String] { [value] }; static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }; static func buildOptional(_ component: [String]?) -> [String] { component ?? [] } }
func sections(@SectionBuilder _ content: () -> [String]) -> [String] { content() }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let include = true
            let report = sections { "Overview"; if include { "Diagnostics" } }
            precondition(report == ["Overview", "Diagnostics"])
        }
        print("swift-038: passed")
    }
}
```

**Observe:** The conditional contributes its section when true.

## Exercises

1. **Predict and explain.** Translate the first block into its builder calls.

2. **Guided modification.** Set include to false and predict the result.

3. **Independent construction.** Build a small report declaration using the existing builder.

4. **Diagnose a defect.** Diagnose a loop in a builder that lacks buildArray support.

5. **Boundary evidence.** Test an empty block and a false optional section.

6. **Transfer and justify.** Explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Result builder, Declarative composition, Intermediate result without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-038: Result builders and declarative composition.
Read courses/swift/guides/swift-038.md and courses/swift/lessons/swift-038.swift. Prerequisites: swift-037.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-038_solution.swift and
courses/swift/solutions/swift-038_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
