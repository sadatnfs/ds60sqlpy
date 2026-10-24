# swift-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-044_solution.swift](swift-044_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe state with words:** A textual state remains meaningful when a visual marker is unavailable. The label communicates completion without relying on color.

**Keep identity separate from translation:** Saved work and navigation should not break when a learner changes language. Display text changes while identity remains stable.

## Reason through the six tasks

1. **Predict and explain.** Identify which information would be lost without color.

2. **Guided modification.** Write an accessible label for an incomplete item and its action.

3. **Independent construction.** Run JourneyApp using keyboard navigation and VoiceOver on macOS.

4. **Diagnose a defect.** Diagnose using a testing identifier as the only meaningful accessibility label.

5. **Boundary evidence.** Check large text, empty content and long translated titles in the Apple project.

6. **Transfer and justify.** Create a manual accessibility acceptance checklist with concrete observations and retained defects.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.

In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.

A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
