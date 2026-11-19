# swift-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-022_solution.swift](swift-022_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe weak lifetime:** The example observes a controlled ownership boundary without retaining the target accidentally. The weak observer becomes nil after the last strong reference is removed.

**Break a parent-child cycle:** The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists. The child survives independently without retaining its parent.

## Task answers

### Task 1: Predict and explain

Draw strong and weak arrows in both examples.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The example observes a controlled ownership boundary without retaining the target accidentally. The weak observer becomes nil after the last strong reference is removed.

### Task 2: Guided modification

Add a temporary second strong owner and predict when the weak observer clears.

No separate reference answer has been written for this task. Start from Example B: The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists. The child survives independently without retaining its parent.

### Task 3: Independent construction

Design a weak delegate relationship.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
final class Listener {
  var events: [String] = []
}
final class Downloader {
  weak var delegate: Listener?
  func finish() { delegate?.events.append("finished") }
}
let downloader = Downloader()
var listener: Listener? = Listener()
downloader.delegate = listener
downloader.finish()
precondition(listener?.events == ["finished"])
listener = nil
precondition(downloader.delegate == nil)
downloader.finish()
```

**Observe:** The listener receives finished; after it is released the weak delegate becomes nil and finish() does nothing.

The downloader does not own its delegate, so it cannot keep the listener alive or form a retain cycle with it.

### Task 4: Diagnose a defect

Diagnose an object retaining a closure that strongly captures the same object.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

### Task 5: Boundary evidence

Test a callback after its weak owner has disappeared.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe weak lifetime) and Example B (Break a parent-child cycle).

### Task 6: Transfer and justify

Choose weak or unowned for a relationship and justify the lifetime guarantee required.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **ARC**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.

`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.

Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

## Review before continuing

Run the reference and confirm that it prints `swift-022: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
