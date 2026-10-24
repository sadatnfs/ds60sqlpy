# swift-040: SwiftUI state, bindings and a single source of truth

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-039`

## Learning objectives

Run JourneyApp and edit a title through its real binding. Then decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

## Purpose and mental model

SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.

## Vocabulary and concepts

**Source of truth:** The owner whose value defines the current state.

**Binding:** Read/write access to state owned elsewhere.

**View identity:** The continuity SwiftUI uses to associate state with a view position.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Apple-only project lab: [JourneyApp state and editing workflow](../fixtures/JourneyApp/README.md). Linux verifies the domain kernel only.

## Syntax anatomy and execution trace

In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Derive presentation from one state

Derived presentation avoids a second label field that can become stale.

```swift
import Foundation

struct FormState { var title: String; var completed: Bool; var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" } }

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

### Example B: A state change updates its derived view

The transition has one source of truth and independent fields remain unchanged.

```swift
import Foundation

struct FormState { var title: String; var completed: Bool; var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" } }

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

## Exercises

1. **Predict and explain.** Identify stored and derived state in the kernel.

2. **Guided modification.** Add a derived disabled state for an empty title.

3. **Independent construction.** Run JourneyApp and edit a title through its real binding.

4. **Diagnose a defect.** Diagnose a child view copying input into unrelated state and losing later parent updates.

5. **Boundary evidence.** Test a title edit, cancellation and return to the list.

6. **Transfer and justify.** Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Source of truth, Binding, View identity without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
