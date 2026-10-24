# swift-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-045_solution.swift](swift-045_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Avoid redundant imperative updates:** A value comparison can prevent unnecessary callback or layout churn at the bridge boundary. The same value is not assigned twice.

**Retain user changes as actions:** The actual platform delegate must route its edit through the same single-source policy. The portable kernel exposes a deliberate state transition.

## Reason through the six tasks

1. **Predict and explain.** Identify the value-driven and imperative sides of the bridge.

2. **Guided modification.** Add a no-op case and verify no extra assignment.

3. **Independent construction.** Inspect and build SelectableText.swift in the Apple project.

4. **Diagnose a defect.** Diagnose an update callback that writes the same binding recursively.

5. **Boundary evidence.** Test empty text, large text and repeated updates in the platform view.

6. **Transfer and justify.** Document coordinator ownership, delegate cleanup and platform-specific API availability.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.

UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.

A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
