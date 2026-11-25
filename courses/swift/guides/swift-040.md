# swift-040: SwiftUI state, bindings and a single source of truth

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-039`

## Learning objectives

Manage SwiftUI state and bindings with a single source of truth. The central exercise is task 3: Run JourneyApp and edit a title through its real binding.

## Purpose and mental model

SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.

## Vocabulary and concepts

**Source of truth:** The owner whose value defines the current state.

**Binding:** Read/write access to state owned elsewhere.

**View identity:** The continuity SwiftUI uses to associate state with a view position.

## How to run this lesson

Only the `FormState` kernel runs here, and the property wrappers named in the notes belong to the Apple app. Tasks 3 and 5 need JourneyApp on macOS with Xcode; on Linux, record them as not performed rather than reasoning from the kernel. Tasks 1 and 2 work in the pad.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Apple-only project lab: [JourneyApp state and editing workflow](../fixtures/JourneyApp/README.md). Linux verifies the domain kernel only.

## Syntax anatomy and execution trace

In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Derive presentation from one state

Derived presentation avoids a second label field that can become stale.

```swift
import Foundation

struct FormState {
  var title: String
  var completed: Bool
  var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let state = FormState(title: "Read", completed: false)
      precondition(state.buttonLabel == "Mark complete")
    }
    print("swift-040: passed")
  }
}
```

**Observe:** The label follows the stored completion state.

**Trace.** `FormState` has two stored properties, title and completed, and one computed property, `buttonLabel`. Nothing stores a label. Reading `buttonLabel` evaluates the conditional at that moment: completed is false, so it returns Mark complete. Because the label is computed on each read, no code path can update the state and forget to update the label, which is the bug a separate stored label field invites.

### Example B: A state change updates its derived view

The transition has one source of truth and independent fields remain unchanged.

```swift
import Foundation

struct FormState {
  var title: String
  var completed: Bool
  var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var state = FormState(title: "Read", completed: false)
      state.completed = true
      precondition(state.buttonLabel == "Mark incomplete")
      precondition(state.title == "Read")
    }
    print("swift-040: passed")
  }
}
```

**Observe:** Changing completion changes the derived label while retaining the title.

**Trace.** `state` is declared with `var` so its stored property can change. Setting completed to true is the only mutation. The next read of `buttonLabel` evaluates the conditional again and now returns Mark incomplete. The second check confirms title is still Read, so changing one stored field did not reset its neighbor. In SwiftUI the same rule appears as one source of truth with views computed from it.

## Exercises

1. **Predict and explain.** Identify stored and derived state in the kernel.

2. **Guided modification.** Add a derived disabled state for an empty title.

3. **Independent construction.** Run JourneyApp and edit a title through its real binding.

4. **Diagnose a defect.** Diagnose a child view copying input into unrelated state and losing later parent updates.

5. **Boundary evidence.** Test a title edit, cancellation and return to the list.

6. **Transfer and justify.** Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

For task 2, a disabled state must be derived from title, and the boundary is a title of only spaces: decide whether trimming applies and test it. Task 4's child view copies the parent's value into its own state once, so later parent changes never reach it. The counterexample is changing the title in the parent after the child appears and seeing the child still show the old text.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Derive presentation from one state) before changing anything, and confirm its observation: The label follows the stored completion state.
2. Compare Example B (A state change updates its derived view) with Example A and name the first line whose behavior differs. Its observation is: Changing completion changes the derived label while retaining the title.
3. Before opening the explanation, check your task 3 attempt (Run JourneyApp and edit a title through its real binding) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Name the stored and derived properties of `FormState` and explain why the label must not be stored. Describe what `@State`, `@Observable` and `@Bindable` each contribute in the app. For one piece of form state, decide whether it belongs to the view, the model or the domain core and justify its lifetime.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app): Apple's SwiftUI documentation covers `State`, `Bindable` and the Observation framework; the Swift book's Properties chapter covers computed properties.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-040: SwiftUI state, bindings and a single source of truth.
Read courses/swift/guides/swift-040.md and courses/swift/lessons/swift-040.swift. Prerequisites: swift-039.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-040_solution.swift and
courses/swift/solutions/swift-040_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
