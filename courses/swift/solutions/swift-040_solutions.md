# swift-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-040_solution.swift](swift-040_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Derive presentation from one state:** Derived presentation avoids a second label field that can become stale. The label follows the stored completion state.

**A state change updates its derived view:** The transition has one source of truth and independent fields remain unchanged. Changing completion changes the derived label while retaining the title.

## Task answers

### Task 1: Predict and explain

Identify stored and derived state in the kernel.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Derived presentation avoids a second label field that can become stale. The label follows the stored completion state.

### Task 2: Guided modification

Add a derived disabled state for an empty title.

No separate reference answer has been written for this task. Start from Example B: The transition has one source of truth and independent fields remain unchanged. Changing completion changes the derived label while retaining the title.

### Task 3: Independent construction

Run JourneyApp and edit a title through its real binding.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Source of truth** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose a child view copying input into unrelated state and losing later parent updates.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

### Task 5: Boundary evidence

Test a title edit, cancellation and return to the list.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Derive presentation from one state) and Example B (A state change updates its derived view).

### Task 6: Transfer and justify

Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Source of truth**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.

In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.

A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

## Review before continuing

Run the reference and confirm that it prints `swift-040: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
