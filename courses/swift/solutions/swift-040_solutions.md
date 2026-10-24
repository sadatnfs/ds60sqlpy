# swift-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-040_solution.swift](swift-040_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Derive presentation from one state:** Derived presentation avoids a second label field that can become stale. The label follows the stored completion state.

**A state change updates its derived view:** The transition has one source of truth and independent fields remain unchanged. Changing completion changes the derived label while retaining the title.

## Reason through the six tasks

1. **Predict and explain.** Identify stored and derived state in the kernel.

2. **Guided modification.** Add a derived disabled state for an empty title.

3. **Independent construction.** Run JourneyApp and edit a title through its real binding.

4. **Diagnose a defect.** Diagnose a child view copying input into unrelated state and losing later parent updates.

5. **Boundary evidence.** Test a title edit, cancellation and return to the list.

6. **Transfer and justify.** Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.

In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.

A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
