# swift-022: ARC, weak references and retain cycles

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-021`

## Learning objectives

Prevent retain cycles with weak and unowned references and verify that objects are released. The central exercise is task 3: Design a weak delegate relationship.

## Purpose and mental model

Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.

## Vocabulary and concepts

**ARC:** Automatic management of strong class-reference counts.

**Weak reference:** A non-owning optional reference that can become nil.

**Retain cycle:** A cycle of strong references preventing release.

## How to run this lesson

All three classes are declared above `LessonMain` in both examples. Draw strong references as solid arrows and weak references as dashed ones before running; task 1 asks for that drawing. Deallocation timing depends on releasing the last strong reference, so keep every extra binding you add for task 2 in a known scope.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Observe weak lifetime

The example observes a controlled ownership boundary without retaining the target accidentally.

```swift
import Foundation

final class Owner {}
final class Parent { var child: Child? }
final class Child { weak var parent: Parent? }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var owner: Owner? = Owner()
      weak var observer = owner
      precondition(observer != nil)
      owner = nil
      precondition(observer == nil)
    }
    print("swift-022: passed")
  }
}
```

**Observe:** The weak observer becomes nil after the last strong reference is removed.

**Trace.** `owner` is an optional strong reference to a new `Owner` instance, whose strong reference count is now one. `weak var observer = owner` refers to the same object without adding a strong reference. The first check sees a live object. Setting `owner` to nil releases the only strong reference, so the instance is deallocated, and Swift sets every weak reference to it to nil. The second check confirms that the observer now reads nil instead of pointing at freed memory.

### Example B: Break a parent-child cycle

The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists.

```swift
import Foundation

final class Owner {}
final class Parent { var child: Child? }
final class Child { weak var parent: Parent? }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var parent: Parent? = Parent()
      let child = Child()
      parent?.child = child
      child.parent = parent
      weak var observed = parent
      parent = nil
      precondition(observed == nil && child.parent == nil)
    }
    print("swift-022: passed")
  }
}
```

**Observe:** The child survives independently without retaining its parent.

**Trace.** `parent` strongly owns a new `Parent`. `child` strongly owns a `Child`. Assigning `parent?.child = child` gives the parent a second strong reference to the child. `child.parent = parent` is weak, so it adds nothing to the parent's count. `observed` is another weak reference. Setting `parent` to nil releases the last strong reference to the `Parent`, which is deallocated, clearing both weak references. The `Child` survives because the local constant `child` still owns it.

## Exercises

1. **Predict and explain.** Draw strong and weak arrows in both examples.

2. **Guided modification.** Add a temporary second strong owner and predict when the weak observer clears.

3. **Independent construction.** Design a weak delegate relationship.

4. **Diagnose a defect.** Diagnose an object retaining a closure that strongly captures the same object.

5. **Boundary evidence.** Test a callback after its weak owner has disappeared.

6. **Transfer and justify.** Choose weak or unowned for a relationship and justify the lifetime guarantee required.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

Task 4's cycle appears when an object stores a closure that mentions `self` without a capture list. Give such a class a property `var onChange: (() -> Void)?` set to `{ self.count += 1 }`, keep a weak observer and release the last outside reference: the observer stays non-nil, which proves the leak. Adding `[weak self]` to the closure lets it become nil.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe weak lifetime) before changing anything, and confirm its observation: The weak observer becomes nil after the last strong reference is removed.
2. Compare Example B (Break a parent-child cycle) with Example A and name the first line whose behavior differs. Its observation is: The child survives independently without retaining its parent.
3. Before opening the explanation, check your task 3 attempt (Design a weak delegate relationship) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why a weak reference must be declared as an optional `var`. Describe what would happen in Example B if `Child.parent` were strong. Choose weak or unowned for a delegate, a parent pointer and a closure stored by its owner, and state the lifetime guarantee each choice relies on.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Automatic Reference Counting chapter of the Swift book covers strong reference cycles, weak and unowned references, and capture lists for closures.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-022: ARC, weak references and retain cycles.
Read courses/swift/guides/swift-022.md and courses/swift/lessons/swift-022.swift. Prerequisites: swift-021.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-022_solution.swift and
courses/swift/solutions/swift-022_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
