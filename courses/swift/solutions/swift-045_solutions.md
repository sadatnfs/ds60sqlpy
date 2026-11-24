# swift-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-045_solution.swift](swift-045_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Avoid redundant imperative updates:** A value comparison can prevent unnecessary callback or layout churn at the bridge boundary. The same value is not assigned twice.

**Retain user changes as actions:** The actual platform delegate must route its edit through the same single-source policy. The portable kernel exposes a deliberate state transition.

## Task answers

### Task 1: Predict and explain

Identify the value-driven and imperative sides of the bridge.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
var bridge = TextBridgeState(text: "", assignments: 0)
let renders = ["draft", "draft", "final"]
for value in renders { bridge.update(value) }
precondition(bridge.text == "final" && bridge.assignments == 2)
```

**Observe:** Three value-driven updates cause only two imperative assignments, ending at final.

SwiftUI side: the struct describes a value and may be re-evaluated often. Imperative side: the platform view holds its own text and should be assigned only when the value actually changes.

### Task 2: Guided modification

Add a no-op case and verify no extra assignment.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var bridge = TextBridgeState(text: "same", assignments: 0)
bridge.update("same")
precondition(bridge.assignments == 0)
bridge.update("other")
precondition(bridge.assignments == 1)
```

**Observe:** Updating to the same text assigns nothing, and a real change assigns once.

The guard compares first, so a re-render with an unchanged value leaves the platform view alone, which preserves selection and avoids extra delegate callbacks.

### Task 3: Independent construction

Inspect and build SelectableText.swift in the Apple project.

**Written answer.** This task needs Xcode and was not run for this reference. SelectableText.swift wraps UITextView under canImport(UIKit) and NSTextField under canImport(AppKit). Build both schemes from the README: JourneyMac compiles only the AppKit branch and JourneyIOS only the UIKit branch. Each update method assigns text only when it differs, the same guard as the portable kernel.

### Task 4: Diagnose a defect

Diagnose an update callback that writes the same binding recursively.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
var writes = 0
var value = "a"
func callback(_ incoming: String, depth: Int) {
  guard depth < 5 else { return }
  guard incoming != value else { return }
  value = incoming
  writes += 1
  callback(incoming, depth: depth + 1)
}
callback("b", depth: 0)
precondition(writes == 1 && value == "b")
```

**Observe:** With an equality guard, the echoed callback stops after one write.

An update that writes the binding triggers another update, which writes again; with no change check it recurses or loops. Compare before writing so the echo becomes a no-op.

### Task 5: Boundary evidence

Test empty text, large text and repeated updates in the platform view.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
var bridge = TextBridgeState(text: "x", assignments: 0)
bridge.update("")
precondition(bridge.text.isEmpty && bridge.assignments == 1)
let large = String(repeating: "a", count: 100_000)
bridge.update(large)
bridge.update(large)
precondition(bridge.text.count == 100_000 && bridge.assignments == 2)
```

**Observe:** Empty text is assigned once, and a 100,000 character string repeated twice is assigned only once more.

This checks the portable state rule. Scrolling, layout and memory with large text in the real UITextView or NSTextField still need the Apple project.

### Task 6: Transfer and justify

Document coordinator ownership, delegate cleanup and platform-specific API availability.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Inspect and build SelectableText.swift in the Apple project) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `TextBridgeState` is a portable model of the boundary between a SwiftUI value and an imperative UIKit or AppKit text control. It stores the current `text` and counts `assignments`. Its `update` method returns early when the incoming text equals what is already stored, and otherwise stores the new text and increments the count. Example A sends the same new value twice; Example B sends one edit. The Apple project's SelectableText.swift applies this rule in a real representable adapter with a coordinator.

**Why it is correct.** In Example A the first `update("new")` finds "old" stored, so it assigns and the count becomes 1. The second call finds "new" already stored, the guard returns, and the count stays 1. In Example B a single real change from "start" to "edited" assigns once. The equality guard is what breaks a potential loop: when the platform control reports an edit, SwiftUI updates its binding and calls the adapter's update again with the same text, and the guard sees nothing to do. Counting assignments turns that otherwise invisible churn into a number a test can check.

**A plausible wrong approach.** Assigning to the platform view's text on every update, and writing the binding again from the delegate callback, is the task 4 defect. Each assignment fires the delegate, which writes the binding, which triggers another update, so the view either loops or resets the cursor on every keystroke. Storing the SwiftUI view value inside the coordinator as permanent state is another mistake, since SwiftUI recreates those values freely.

**How to verify.** For task 2, call `update` with the current text and confirm `assignments` does not change. For tasks 3 and 5, build SelectableText.swift on an Apple destination, type into the field, paste a long text and clear it, and record whether the cursor stayed in place. A successful `canImport` branch on one platform says nothing about the other.

## Mechanism and diagnostic reasoning

SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.

UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.

A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

## Review before continuing

Run the reference and confirm that it prints `swift-045: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
