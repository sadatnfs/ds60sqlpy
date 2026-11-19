# swift-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-045_solution.swift](swift-045_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Avoid redundant imperative updates:** A value comparison can prevent unnecessary callback or layout churn at the bridge boundary. The same value is not assigned twice.

**Retain user changes as actions:** The actual platform delegate must route its edit through the same single-source policy. The portable kernel exposes a deliberate state transition.

## Task answers

### Task 1: Predict and explain

Identify the value-driven and imperative sides of the bridge.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A value comparison can prevent unnecessary callback or layout churn at the bridge boundary. The same value is not assigned twice.

### Task 2: Guided modification

Add a no-op case and verify no extra assignment.

No separate reference answer has been written for this task. Start from Example B: The actual platform delegate must route its edit through the same single-source policy. The portable kernel exposes a deliberate state transition.

### Task 3: Independent construction

Inspect and build SelectableText.swift in the Apple project.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Representable adapter** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose an update callback that writes the same binding recursively.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

### Task 5: Boundary evidence

Test empty text, large text and repeated updates in the platform view.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Avoid redundant imperative updates) and Example B (Retain user changes as actions).

### Task 6: Transfer and justify

Document coordinator ownership, delegate cleanup and platform-specific API availability.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Representable adapter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.

UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.

A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

## Review before continuing

Run the reference and confirm that it prints `swift-045: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
