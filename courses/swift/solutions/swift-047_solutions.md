# swift-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-047_solution.swift](swift-047_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep portable policy independent:** A portable core should not import a platform framework merely to format its basic domain outcome. The same domain summary works without a UI framework.

**Declare a capability rather than guess:** Capability descriptions should follow actual prepared runtime evidence. The Linux capability set does not invent SwiftUI support.

## Task answers

### Task 1: Predict and explain

Identify which code belongs in the portable core.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A portable core should not import a platform framework merely to format its basic domain outcome. The same domain summary works without a UI framework.

### Task 2: Guided modification

Add a platform-neutral derived statistic.

No separate reference answer has been written for this task. Start from Example B: Capability descriptions should follow actual prepared runtime evidence. The Linux capability set does not invent SwiftUI support.

### Task 3: Independent construction

Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Deployment target** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose importing UIKit in a shared domain target.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

### Task 5: Boundary evidence

Test unavailable capabilities with a clear message rather than a broken Run action.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Keep portable policy independent) and Example B (Declare a capability rather than guess).

### Task 6: Transfer and justify

Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Deployment target**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.

#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.

CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

## Review before continuing

Run the reference and confirm that it prints `swift-047: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
