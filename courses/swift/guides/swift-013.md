# swift-013: Classes, identity and shared state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-012`

## Learning objectives

Choose classes for shared identity and structs for values, and predict sharing and copying. The central exercise is task 3: Choose class or struct for a shared connection coordinator and a coordinate value.

## Purpose and mental model

A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.

## Vocabulary and concepts

**Reference identity:** The identity of one shared object instance.

**Final class:** A class that cannot be subclassed.

**Composition:** Building behavior by collaborating with contained objects.

## How to run this lesson

Both examples declare `Counter` as a `final class` above `LessonMain`. Draw two boxes for the bindings and one box per object before pasting anything; task 1 asks for exactly that diagram. Task 3 is a design decision rather than a program, so write the class or struct choice and its reason in your pad as comments.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Observe shared identity

The copied reference still identifies one object, even though both bindings are constant.

```swift
import Foundation

final class Counter {
  private(set) var value = 0
  func increment() { value += 1 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let first = Counter()
      let second = first
      second.increment()
      precondition(first.value == 1)
      precondition(first === second)
    }
    print("swift-013: passed")
  }
}
```

**Observe:** Both names observe the same increment.

**Trace.** `Counter()` creates one object on the heap with `value` 0, and `first` holds a reference to it. `let second = first` copies the reference, not the object, so both constants now point at the same instance. `second.increment()` is allowed even though `second` is a `let`, because the constant fixes which object is referenced, not the object's contents. The object's value becomes 1, so reading through `first` also gives 1, and `===` confirms the two references identify one instance.

### Example B: Equal state need not mean identity

Object identity answers a different question from comparing a property value.

```swift
import Foundation

final class Counter {
  private(set) var value = 0
  func increment() { value += 1 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let first = Counter()
      let second = Counter()
      precondition(first.value == second.value)
      precondition(first !== second)
    }
    print("swift-013: passed")
  }
}
```

**Observe:** Two fresh counters have equal state but distinct identities.

**Trace.** This time `Counter()` runs twice, producing two separate objects, each with `value` 0. Comparing `first.value == second.value` asks whether their states are equal, and the answer is yes. Comparing `first !== second` asks whether they are the same instance, and the answer is no. `Counter` does not conform to `Equatable`, so `first == second` would not compile at all: Swift gives classes identity comparison for free but makes you define what equal state means.

## Exercises

1. **Predict and explain.** Draw references before and after assignment.

2. **Guided modification.** Create a separate object and mutate only one.

3. **Independent construction.** Choose class or struct for a shared connection coordinator and a coordinate value.

4. **Diagnose a defect.** Diagnose expecting class assignment to create an independent snapshot.

5. **Boundary evidence.** Test equal property values on distinct objects.

6. **Transfer and justify.** Explain whether a shared class needs synchronization before use from concurrent tasks.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

Task 4's mistaken expectation is that `let snapshot = counter` freezes the current count. The counterexample takes three lines: assign, call `increment()` on the original, then read `snapshot.value`, which has moved too. A real snapshot must copy the state into a value, for example `let saved = counter.value`, which stays at the old number after the increment.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe shared identity) before changing anything, and confirm its observation: Both names observe the same increment.
2. Compare Example B (Equal state need not mean identity) with Example A and name the first line whose behavior differs. Its observation is: Two fresh counters have equal state but distinct identities.
3. Before opening the explanation, check your task 3 attempt (Choose class or struct for a shared connection coordinator and a coordinate value) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Describe what `===` compares and what `==` would compare once a class conforms to `Equatable`. Explain why a `let` binding to a class instance still permits calling a mutating method on that object. Name one reason a shared coordinator should be a class and one reason a map coordinate should be a struct.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Structures and Classes chapter of the Swift book explains reference types and identity operators; Automatic Reference Counting explains instance lifetime.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-013: Classes, identity and shared state.
Read courses/swift/guides/swift-013.md and courses/swift/lessons/swift-013.swift. Prerequisites: swift-012.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-013_solution.swift and
courses/swift/solutions/swift-013_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
