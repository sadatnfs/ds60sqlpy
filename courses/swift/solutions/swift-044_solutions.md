# swift-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-044_solution.swift](swift-044_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe state with words:** A textual state remains meaningful when a visual marker is unavailable. The label communicates completion without relying on color.

**Keep identity separate from translation:** Saved work and navigation should not break when a learner changes language. Switching language changes the title from Read to Lire while the completion saved under lesson-one still shows complete.

## Task answers

### Task 1: Predict and explain

Identify which information would be lost without color.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A textual state remains meaningful when a visual marker is unavailable. The label communicates completion without relying on color.

### Task 2: Guided modification

Write an accessible label for an incomplete item and its action.

No separate reference answer has been written for this task. Start from Example B: Saved work and navigation should not break when a learner changes language. Switching language changes the title from Read to Lire while the completion saved under lesson-one still shows complete.

### Task 3: Independent construction

Run JourneyApp using keyboard navigation and VoiceOver on macOS.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Accessible name** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose using a testing identifier as the only meaningful accessibility label.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

### Task 5: Boundary evidence

Check large text, empty content and long translated titles in the Apple project.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Describe state with words) and Example B (Keep identity separate from translation).

### Task 6: Transfer and justify

Create a manual accessibility acceptance checklist with concrete observations and retained defects.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Accessible name**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.

In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.

A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

## Review before continuing

Run the reference and confirm that it prints `swift-044: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
