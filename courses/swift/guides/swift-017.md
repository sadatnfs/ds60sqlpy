# swift-017: Protocols and behavioral substitution

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-016`

## Learning objectives

Program against protocols so implementations can be substituted without changing callers. The central exercise is task 3: Define a protocol for a deterministic label formatter.

## Purpose and mental model

A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.

## Vocabulary and concepts

**Protocol:** A declared set of required capabilities.

**Conformance:** A type satisfying a protocol contract.

**Existential:** A value hiding a concrete type behind a protocol interface.

## How to run this lesson

Both examples declare the `Pricer` protocol and its two conformers above `LessonMain`. Task 2 adds another `FlatPrice` value without editing the code that calls `cost`, which is the whole point of the protocol. Task 4 is a design defect that compiles and runs; only a check with known units reveals it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Use a capability

The interface preserves units and result meaning while hiding representation.

```swift
import Foundation

protocol Pricer { func cost(units: Int) -> Int }
struct FlatPrice: Pricer {
  let unit: Int
  func cost(units: Int) -> Int { unit * units }
}
struct CappedPrice: Pricer {
  let unit: Int
  let cap: Int
  func cost(units: Int) -> Int { min(unit * units, cap) }
}

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

**Trace.** `price` has the existential type `any Pricer`, holding a `FlatPrice` with `unit` 3. The call `price.cost(units: 4)` is dispatched at runtime to `FlatPrice.cost`, which multiplies 3 by 4 and returns 12. The calling code never mentions `FlatPrice` after the declaration, so replacing it with another conformer changes the behavior without changing the call site. The protocol guarantees the method exists, but not that every conformer charges in the same currency unit.

### Example B: Substitute another policy

Substitution allows variation within the documented contract, not arbitrary semantic disagreement.

```swift
import Foundation

protocol Pricer { func cost(units: Int) -> Int }
struct FlatPrice: Pricer {
  let unit: Int
  func cost(units: Int) -> Int { unit * units }
}
struct CappedPrice: Pricer {
  let unit: Int
  let cap: Int
  func cost(units: Int) -> Int { min(unit * units, cap) }
}

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

**Trace.** `prices` is an array of `any Pricer` holding two different concrete types. `map` calls `cost(units: 4)` on each element. The flat policy returns 12. The capped policy computes 12 as well, then `min(12, 10)` limits it to 10. The result `[12, 10]` shows one call site producing different valid prices. Both conformers agree that the input is a unit count and the output is a whole price in the same currency, which is the semantic contract the protocol cannot express in its signature.

## Exercises

1. **Predict and explain.** Trace the protocol call to each concrete implementation.

2. **Guided modification.** Add a second flat price without changing the consumer.

3. **Independent construction.** Define a protocol for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose two conformers using incompatible units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a dependency worth abstracting in the importer and explain why a protocol helps.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

Task 4's mismatch is easy to construct: a conformer that returns cents while the others return whole units. With 4 units at 3 per unit, it reports 1200 next to 12, and a consumer summing both is wrong by a factor of 100. For task 5, check zero units, which should cost 0 under both policies, and exactly the cap: 3 units at 3 per unit with a cap of 9 should return 9.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use a capability) before changing anything, and confirm its observation: The consumer calls the pricing capability without needing its storage details.
2. Compare Example B (Substitute another policy) with Example A and name the first line whose behavior differs. Its observation is: Two conforming policies produce different valid prices.
3. Before opening the explanation, check your task 3 attempt (Define a protocol for a deterministic label formatter) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain what `any Pricer` means as a type and what Swift must do at runtime to call `cost` through it. Name one requirement that belongs in the protocol's documentation because the signature cannot express it. Say which dependency of the importer from swift-016 you would abstract behind a protocol, and why.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Protocols chapter of the Swift book covers protocol requirements, conformance and protocols as types; Opaque and Boxed Protocol Types explains `any`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
