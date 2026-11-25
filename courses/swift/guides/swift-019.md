# swift-019: Associated types, opaque results and existentials

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-018`

## Learning objectives

Use associated types, opaque results and existentials and explain what each hides. The central exercise is task 3: Write a generic transformation preserving the producer item type.

## Purpose and mental model

An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.

## Vocabulary and concepts

**Associated type:** A type selected by each protocol conformance.

**Opaque type:** A hidden but consistent concrete type.

**Type erasure:** Hiding concrete type information behind an interface.

## How to run this lesson

Both examples share the `Producer` protocol, `IntegerSource`, `read` and `makeLabels`, all declared above `LessonMain`. Task 2 adds a conformer that produces a `String`. Task 4 asks you to return two different concrete types from one `some` function; the compiler rejects it because an opaque result must have a single underlying type.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Retain a produced type

The associated type relationship survives through the generic function.

```swift
import Foundation

protocol Producer {
  associatedtype Item
  func produce() -> Item
}
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }

@main
struct LessonMain {
  static func main() async throws {
    do {
      let source = IntegerSource()
      let value: Int = read(source)
      precondition(value == 7)
    }
    print("swift-019: passed")
  }
}
```

**Observe:** The generic consumer knows the produced value is an Int.

**Trace.** `IntegerSource` conforms to `Producer` by implementing `produce()` returning `Int`, so the compiler infers its associated `Item` as `Int`. Calling `read(source)` binds `P` to `IntegerSource`, so the return type `P.Item` resolves to `Int`. The annotation `let value: Int` therefore needs no cast. The body calls `produce()`, which returns 7, and the check confirms it. With an existential parameter instead of a generic one, the item type would be erased and the caller would no longer know it receives an `Int`.

### Example B: Hide representation with an opaque result

The function selects one underlying result type while exposing its element relationship.

```swift
import Foundation

protocol Producer {
  associatedtype Item
  func produce() -> Item
}
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }

@main
struct LessonMain {
  static func main() async throws {
    do {
      let labels = makeLabels()
      precondition(Array(labels) == ["a", "b"])
    }
    print("swift-019: passed")
  }
}
```

**Observe:** The caller uses sequence behavior without naming the concrete array type.

**Trace.** `makeLabels()` declares an opaque result, `some Sequence<String>`. Inside, it returns an array literal, so the hidden underlying type is `[String]`, but callers see only a sequence whose elements are strings. The caller can iterate it or pass it to `Array(...)`, which collects a and b, but it cannot call array-only operations such as subscripting. Changing the body to return a `Set` later would not break callers, because they never relied on the concrete type.

## Exercises

1. **Predict and explain.** Trace the associated Item type through read.

2. **Guided modification.** Add a String-producing conformance.

3. **Independent construction.** Write a generic transformation preserving the producer item type.

4. **Diagnose a defect.** Explain why returning unrelated concrete types from one opaque-return function is invalid.

5. **Boundary evidence.** Test empty and nonempty opaque sequences.

6. **Transfer and justify.** Choose opaque output or existential storage for an API and document the preserved relationships.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

Task 4's invalid function has an if-else returning an array in one branch and a `Set` in the other. Keep the compiler error in your notes: it says the return statements do not have matching underlying types. For task 5, an opaque sequence of zero labels must still type-check and produce an empty array, so test `Array(labels).isEmpty` as well as the two-element case.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Retain a produced type) before changing anything, and confirm its observation: The generic consumer knows the produced value is an Int.
2. Compare Example B (Hide representation with an opaque result) with Example A and name the first line whose behavior differs. Its observation is: The caller uses sequence behavior without naming the concrete array type.
3. Before opening the explanation, check your task 3 attempt (Write a generic transformation preserving the producer item type) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain who chooses the concrete type for a generic parameter, an opaque result and an existential value. Say why `read` can return `P.Item` but a function taking `any Producer` cannot easily promise a specific item type. Name one API where hiding the concrete collection type is worth the restriction.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Swift book chapters Generics, on associated types, and Opaque and Boxed Protocol Types explain the relationship between `some` and `any`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-019: Associated types, opaque results and existentials.
Read courses/swift/guides/swift-019.md and courses/swift/lessons/swift-019.swift. Prerequisites: swift-018.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-019_solution.swift and
courses/swift/solutions/swift-019_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
