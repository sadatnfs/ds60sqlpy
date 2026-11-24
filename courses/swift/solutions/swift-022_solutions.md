# swift-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-022_solution.swift](swift-022_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe weak lifetime:** The example observes a controlled ownership boundary without retaining the target accidentally. The weak observer becomes nil after the last strong reference is removed.

**Break a parent-child cycle:** The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists. The child survives independently without retaining its parent.

## Task answers

### Task 1: Predict and explain

Draw strong and weak arrows in both examples.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
var parent: Parent? = Parent()
var child: Child? = Child()
parent?.child = child
child?.parent = parent
weak var childObserver = child
child = nil
precondition(childObserver != nil)
parent = nil
precondition(childObserver == nil)
```

**Observe:** The child survives losing its local variable while the parent still holds it, and disappears once the parent is gone.

The arrow from Parent.child is strong, so it keeps the child alive; the arrow from Child.parent is weak, so nothing keeps the parent alive after parent = nil, and the child follows.

### Task 2: Guided modification

Add a temporary second strong owner and predict when the weak observer clears.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var owner: Owner? = Owner()
var second: Owner? = owner
weak var observer = owner
owner = nil
precondition(observer != nil && second != nil)
second = nil
precondition(observer == nil)
```

**Observe:** The observer survives clearing owner because second still holds the object, and clears when second is set to nil.

A weak reference becomes nil only after the last strong reference goes away, so the second owner delays deallocation until it is released.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
final class Ticker {
  var count = 0
  var onTick: (() -> Void)?
  func startStrong() { onTick = { self.count += 1 } }
  func startWeak() { onTick = { [weak self] in self?.count += 1 } }
}
var leaky: Ticker? = Ticker()
leaky?.startStrong()
weak var leakObserver = leaky
leaky = nil
precondition(leakObserver != nil)
leakObserver?.onTick = nil
precondition(leakObserver == nil)
var fixed: Ticker? = Ticker()
fixed?.startWeak()
weak var fixedObserver = fixed
fixed = nil
precondition(fixedObserver == nil)
```

**Observe:** The strongly capturing ticker outlives its variable until onTick is cleared; the weakly capturing ticker is freed immediately.

The object owns the closure and the closure owns self, forming a cycle ARC cannot break; [weak self] removes the closure's strong arrow.

### Task 5: Boundary evidence

Test a callback after its weak owner has disappeared.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
final class Screen {
  var shown: [String] = []
}
var screen: Screen? = Screen()
let show = { [weak screen] (text: String) -> Bool in
  guard let screen else { return false }
  screen.shown.append(text)
  return true
}
precondition(show("first") && screen?.shown == ["first"])
screen = nil
precondition(!show("late"))
```

**Observe:** The callback delivers first while the screen exists and returns false for late after it is gone.

The capture list holds the screen weakly, so a late callback finds nil and reports that nothing was delivered instead of reviving or crashing.

### Task 6: Transfer and justify

Choose weak or unowned for a relationship and justify the lifetime guarantee required.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Design a weak delegate relationship) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A holds an `Owner` in an optional strong variable and also in a `weak var`, then removes the strong reference. Example B links a `Parent` and a `Child` where the child's back-reference is `weak`, then drops the only external strong reference to the parent. The task 3 answer designs a weak delegate that receives a finished message.

**Why it is correct.** ARC frees an object when its strong count reaches zero. In Example A the weak variable does not count, so setting `owner = nil` frees the object and the weak variable becomes nil. In Example B the parent strongly holds the child but the child only weakly holds the parent, so releasing `parent` frees it and `child.parent` reads nil while the child stays alive through `let child`.

**A plausible wrong approach.** Declaring `Child.parent` as a strong `var` creates a cycle: parent holds child and child holds parent, so after `parent = nil` neither is freed and `observed == nil` fails. A local `let keep = parent` placed before the release would also keep the parent alive and make the same check fail.

**How to verify.** Remove `weak` from `Child.parent` in a scratch pad and confirm the check fails. For task 3, the listener receives finished, and after it is released the weak delegate becomes nil and `finish()` does nothing.

## Mechanism and diagnostic reasoning

Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.

`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.

Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

## Review before continuing

Run the reference and confirm that it prints `swift-022: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
