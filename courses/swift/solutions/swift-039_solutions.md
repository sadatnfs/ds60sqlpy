# swift-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-039_solution.swift](swift-039_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Apply a domain action:** A pure transition supports undo, testing and separate UI rendering. The transformed item changes completion while retaining the original value.

**Keep identity stable during edits:** Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item. Completion changes do not manufacture a new identity.

## Task answers

### Task 1: Predict and explain

Identify domain and presentation responsibilities.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A pure transition supports undo, testing and separate UI rendering. The transformed item changes completion while retaining the original value.

### Task 2: Guided modification

Add a pure rename operation with nonempty-title validation.

No separate reference answer has been written for this task. Start from Example B: Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item. Completion changes do not manufacture a new identity.

### Task 3: Independent construction

Build and test JourneyCore before opening the Apple app.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Domain core** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose placing file access directly inside a model property getter.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

### Task 5: Boundary evidence

Test unknown identity and duplicate identity admission.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Apply a domain action) and Example B (Keep identity stable during edits).

### Task 6: Transfer and justify

Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Domain core**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.

A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.

A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

## Review before continuing

Run the reference and confirm that it prints `swift-039: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
