# swift-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-040_solution.swift](swift-040_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Derive presentation from one state:** Derived presentation avoids a second label field that can become stale. The label follows the stored completion state.

**A state change updates its derived view:** The transition has one source of truth and independent fields remain unchanged. Changing completion changes the derived label while retaining the title.

## Task answers

### Task 1: Predict and explain

Identify stored and derived state in the kernel.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
var state = FormState(title: "Read", completed: false)
precondition(state.buttonLabel == "Mark complete")
state.completed.toggle()
precondition(state.buttonLabel == "Mark incomplete")
```

**Observe:** Toggling the stored completed flag changes the derived label from Mark complete to Mark incomplete.

title and completed are stored; buttonLabel is computed from completed every time it is read, so it can never disagree with the state it describes.

### Task 2: Guided modification

Add a derived disabled state for an empty title.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct EditableForm {
  var title: String
  var completed: Bool
  var saveDisabled: Bool { title.trimmingCharacters(in: .whitespaces).isEmpty }
}
var form = EditableForm(title: "Read", completed: false)
precondition(!form.saveDisabled)
form.title = "  "
precondition(form.saveDisabled)
```

**Observe:** Save is enabled for Read and disabled once the title is only spaces.

saveDisabled is derived from title rather than stored, so no code path can forget to update it; the domain must still reject a blank title on its own.

### Task 3: Independent construction

Run JourneyApp and edit a title through its real binding.

**Written answer.** This task needs a prepared Mac and was not run for this reference. Generate and run JourneyApp as its README describes, add an item, open it and change the title. ItemEditor binds its TextField to a local @State draft, so typing changes only the draft; Save changes calls store.update, which writes through StudyPlan.update and publishes the new title to the list. Cancel dismisses without calling update, so the list keeps the old title.

### Task 4: Diagnose a defect

Diagnose a child view copying input into unrelated state and losing later parent updates.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
final class Model { var title = "Read" }
struct StaleChild {
  var copy: String
  init(model: Model) { copy = model.title }
}
struct LiveChild {
  let model: Model
  var shown: String { model.title }
}
let model = Model()
let stale = StaleChild(model: model)
let live = LiveChild(model: model)
model.title = "Review"
precondition(stale.copy == "Read" && live.shown == "Review")
```

**Observe:** After the parent changes the title, the copying child still shows Read while the reading child shows Review.

Copying input into the child's own state at creation freezes it; later parent updates never arrive. Read from the shared source, or use a binding, unless the copy is a deliberate draft.

### Task 5: Boundary evidence

Test a title edit, cancellation and return to the list.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
struct Draft {
  var title: String
  func commit(into saved: inout String) { saved = title }
}
var saved = "Read"
var edit = Draft(title: saved)
edit.title = "Review"
edit.commit(into: &saved)
precondition(saved == "Review")
var cancelled = Draft(title: saved)
cancelled.title = "Discard me"
precondition(saved == "Review")
```

**Observe:** A committed edit changes the saved title to Review, and a cancelled draft leaves it unchanged on return to the list.

This portable kernel mirrors ItemEditor's draft contract: edits stay in a draft until an explicit save. The real return to the list must still be checked in JourneyApp on an Apple destination.

### Task 6: Transfer and justify

Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Run JourneyApp and edit a title through its real binding) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `FormState` stores `title` and `completed` and derives `buttonLabel` as a computed property. Example A reads the label for an incomplete item; Example B sets `completed` to true and rereads it. In JourneyApp the same rule appears as a SwiftUI view reading one model through a binding.

**Why it is correct.** `buttonLabel` has no storage of its own, so every read evaluates `completed ? "Mark incomplete" : "Mark complete"` from the current flag. False gives "Mark complete"; after the assignment true gives "Mark incomplete". The title is a separate stored field the assignment did not touch, so it is still "Read". With one source of truth there is no second label field to fall out of date.

**A plausible wrong approach.** Storing `buttonLabel` as a `var` set once in `init` would leave it at "Mark complete" after `completed` changes, so Example B's check fails. In SwiftUI the equivalent defect is task 4: a child view that copies its input into its own `@State` in `init` ignores later updates from the parent, because the copy is a separate source.

**How to verify.** For task 2, add `var saveDisabled: Bool { title.isEmpty }` and check it for "" and "Read". For tasks 3 and 5, run JourneyApp on a Mac, edit a title, cancel and return to the list, and write down what each screen showed rather than inferring it from the kernel check.

## Mechanism and diagnostic reasoning

SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.

In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.

A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.

## Review before continuing

Run the reference and confirm that it prints `swift-040: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
