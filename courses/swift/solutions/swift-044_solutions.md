# swift-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-044_solution.swift](swift-044_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe state with words:** A textual state remains meaningful when a visual marker is unavailable. The label communicates completion without relying on color.

**Keep identity separate from translation:** Saved work and navigation should not break when a learner changes language. Switching language changes the title from Read to Lire while the completion saved under lesson-one still shows complete.

## Task answers

### Task 1: Predict and explain

Identify which information would be lost without color.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
struct ColorOnlyRow {
  let title: String
  let tint: String
}
let row = ColorOnlyRow(title: "Read", tint: "green")
let spoken = row.title
precondition(!spoken.contains("complete"))
let labeled = "\(row.title), \(row.tint == "green" ? "complete" : "incomplete")"
precondition(labeled == "Read, complete")
```

**Observe:** With color alone, the spoken text is just Read; adding words produces Read, complete.

Completion was carried only by tint, so anyone who cannot see the color loses it; the word complete survives screen readers, grayscale and color blindness.

### Task 2: Guided modification

Write an accessible label for an incomplete item and its action.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func rowLabel(title: String, complete: Bool) -> String {
  "\(title), \(complete ? "complete" : "incomplete")"
}
func actionLabel(title: String, complete: Bool) -> String {
  complete ? "Mark \(title) incomplete" : "Mark \(title) complete"
}
precondition(rowLabel(title: "Read", complete: false) == "Read, incomplete")
precondition(actionLabel(title: "Read", complete: false) == "Mark Read complete")
```

**Observe:** The incomplete row reads Read, incomplete and its action reads Mark Read complete.

The row label states the current state and the action label states what activating it will do, both naming the item so they make sense out of context.

### Task 3: Independent construction

Run JourneyApp using keyboard navigation and VoiceOver on macOS.

**Written answer.** This task needs a Mac with JourneyApp running and was not performed for this reference. Turn on VoiceOver and Full Keyboard Access, then move through the progress summary, the new item field, Add and each row. PlanView hides the decorative checkmark and gives each row the label title, complete or incomplete, so VoiceOver should say, for example, Read a chapter, incomplete. Record the actual focus order you hear.

### Task 4: Diagnose a defect

Diagnose using a testing identifier as the only meaningful accessibility label.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let identifier = "row-7"
let label = "Read a chapter, incomplete"
precondition(!identifier.contains("Read") && label.contains("Read"))
```

**Observe:** The identifier row-7 tells the user nothing, while the label names the item and its state.

accessibilityIdentifier exists for tests and is never spoken. If it is the only distinguishing text, VoiceOver users hear nothing useful. Keep the identifier for tests and add a real accessibilityLabel.

### Task 5: Boundary evidence

Check large text, empty content and long translated titles in the Apple project.

**Written answer.** These checks need the Apple project on a prepared Mac and were not run for this reference. Set Dynamic Type to the largest accessibility size and confirm row text wraps instead of clipping; delete every item and confirm the list and progress text still make sense; then enter a very long title and confirm it wraps in the row and the editor. Note each failure with the setting that caused it.

### Task 6: Transfer and justify

Create a manual accessibility acceptance checklist with concrete observations and retained defects.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Run JourneyApp using keyboard navigation and VoiceOver on macOS) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A defines `accessibilityText`, which joins a title and the word complete or incomplete. Example B keeps translated titles in a dictionary keyed by language and saved completion in a dictionary keyed by a stable id, `lesson-one`, then builds a row for English and French.

**Why it is correct.** With title "Read" and `complete` true, the interpolation gives "Read, complete", which states completion in words a screen reader can speak instead of relying on a check mark or color. In Example B the completion lookup uses `lesson-one`, not the displayed title, so switching from `en` to `fr` changes only the title lookup: "Read: complete" becomes "Lire: complete" and the saved state is unchanged.

**A plausible wrong approach.** Keying saved progress by the displayed title would lose it on a language switch: `saved["Lire"]` is absent, so the French row would show incomplete. Using a testing identifier such as `row_3` as the accessibility label (task 4) gives VoiceOver users a string that tells them nothing about the item or its state.

**How to verify.** For task 2, check that `accessibilityText(title: "Read", complete: false)` is "Read, incomplete". These string checks cannot show reading order or focus, so for tasks 3 and 5 run JourneyApp with VoiceOver and the largest text size, and record what was announced and whether long titles clipped.

## Mechanism and diagnostic reasoning

An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.

In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.

A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

## Review before continuing

Run the reference and confirm that it prints `swift-044: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
