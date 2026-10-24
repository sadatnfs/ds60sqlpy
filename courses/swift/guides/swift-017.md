# swift-017: Protocols and behavioral substitution

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-016`

## Learning objectives

Define a protocol for a deterministic label formatter. Then choose a dependency worth abstracting in the importer and explain why a protocol helps.

## Purpose and mental model

A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.

## Vocabulary and concepts

**Protocol:** A declared set of required capabilities.

**Conformance:** A type satisfying a protocol contract.

**Existential:** A value hiding a concrete type behind a protocol interface.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use a capability

The interface preserves units and result meaning while hiding representation.

```swift
import Foundation

protocol Pricer { func cost(units: Int) -> Int }
struct FlatPrice: Pricer { let unit: Int; func cost(units: Int) -> Int { unit * units } }
struct CappedPrice: Pricer { let unit: Int; let cap: Int; func cost(units: Int) -> Int { min(unit * units, cap) } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let price: any Pricer = FlatPrice(unit: 3)
            precondition(price.cost(units: 4) == 12)
        }
        print("swift-017: passed")
    }
}
```

**Observe:** The consumer calls the pricing capability without needing its storage details.

### Example B: Substitute another policy

Substitution allows variation within the documented contract, not arbitrary semantic disagreement.

```swift
import Foundation

protocol Pricer { func cost(units: Int) -> Int }
struct FlatPrice: Pricer { let unit: Int; func cost(units: Int) -> Int { unit * units } }
struct CappedPrice: Pricer { let unit: Int; let cap: Int; func cost(units: Int) -> Int { min(unit * units, cap) } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]
            precondition(prices.map { $0.cost(units: 4) } == [12, 10])
        }
        print("swift-017: passed")
    }
}
```

**Observe:** Two conforming policies produce different valid prices.

## Exercises

1. **Predict and explain.** Trace the protocol call to each concrete implementation.

2. **Guided modification.** Add a second flat price without changing the consumer.

3. **Independent construction.** Define a protocol for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose two conformers using incompatible units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a dependency worth abstracting in the importer and explain why a protocol helps.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Protocol, Conformance, Existential without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-017: Protocols and behavioral substitution.
Read courses/swift/guides/swift-017.md and courses/swift/lessons/swift-017.swift. Prerequisites: swift-016.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-017_solution.swift and
courses/swift/solutions/swift-017_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
