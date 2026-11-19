# swift-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-048_solution.swift](swift-048_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Produce a stable completion summary:** The report checks state and identity rather than only a formatted label. One of two uniquely identified items is complete.

**Preserve identity across a value update:** These are the core semantics needed by undo, navigation and persistence. The update retains identity and the prior snapshot.

## Task answers

### Task 1: Predict and explain

Trace one user action from view through model to domain state.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The report checks state and identity rather than only a formatted label. One of two uniquely identified items is complete.

### Task 2: Guided modification

Add a derived progress summary without duplicating stored completion counts.

No separate reference answer has been written for this task. Start from Example B: These are the core semantics needed by undo, navigation and persistence. The update retains identity and the prior snapshot.

### Task 3: Independent construction

Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Offline-first** and the lesson notes.

### Task 4: Diagnose a defect

Introduce and repair a stale-binding, duplicate-identity or failed-save defect.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

### Task 5: Boundary evidence

Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Produce a stable completion summary) and Example B (Preserve identity across a value update).

### Task 6: Transfer and justify

Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Offline-first**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.

A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.

A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

## Review before continuing

Run the reference and confirm that it prints `swift-048: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
