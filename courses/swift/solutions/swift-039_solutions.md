# swift-039: explanation and comparison

Reference program: [swift-039_solution.swift](swift-039_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Apply a domain action:** A pure transition supports undo, testing and separate UI rendering. The transformed item changes completion while retaining the original value.

**Keep identity stable during edits:** Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item. Completion changes do not manufacture a new identity.

## Task answers

### Task 1: Predict and explain

Identify domain and presentation responsibilities.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let item = PlannerItem(id: "one", title: "Read", completed: false)
let updated = toggled(item)
let rowText = "\(updated.title): \(updated.completed ? "done" : "open")"
precondition(updated.completed && rowText == "Read: done")
```

**Observe:** The domain step flips completion, and a separate presentation step renders Read: done.

toggled is domain logic: it decides what completing an item means and knows nothing about text or views. Turning the value into Read: done is presentation, which can change without touching the rule.

### Task 2: Guided modification

Add a pure rename operation with nonempty-title validation.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
enum RenameError: Error { case emptyTitle }
func renamed(_ item: PlannerItem, to title: String) throws -> PlannerItem {
  let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
  guard !trimmed.isEmpty else { throw RenameError.emptyTitle }
  return PlannerItem(id: item.id, title: trimmed, completed: item.completed)
}
let item = PlannerItem(id: "one", title: "Read", completed: true)
let changed = try renamed(item, to: " Review ")
precondition(changed.id == "one" && changed.title == "Review" && changed.completed)
precondition((try? renamed(item, to: "   ")) == nil)
```

**Observe:** Renaming to padded Review keeps id one and completion, while a blank title is refused.

The rename is pure: it returns a new value and keeps identity, and the rule that titles are nonempty lives in the domain, so every caller gets the same refusal.

### Task 3: Independent construction

Build and test JourneyCore before opening the Apple app.

**Written answer.** Copy fixtures/JourneyCore into your own workspace and run swift build and then swift test there before touching JourneyApp. In the reference run on swift:6.3.3-noble the build ended with Build complete! and the test run reported Executed 4 tests, with 0 failures. A green core is the precondition for the app, but it says nothing yet about rendering or navigation.

### Task 4: Diagnose a defect

Diagnose placing file access directly inside a model property getter.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct PlanSnapshot {
  let titles: [String]
  var count: Int { titles.count }
}
func loadPlan(from storage: [String: [String]], key: String) -> PlanSnapshot {
  PlanSnapshot(titles: storage[key] ?? [])
}
let storage = ["plan": ["Read", "Practice"]]
let plan = loadPlan(from: storage, key: "plan")
precondition(plan.count == 2 && plan.count == 2)
```

**Observe:** The plan is loaded once by an adapter, and reading count twice is a plain computation returning 2 each time.

A getter that reads a file runs I/O on every access, can fail with nowhere to report the error, and hides cost behind property syntax. Loading belongs to an adapter that returns a value; model properties then stay pure and cheap.

### Task 5: Boundary evidence

Test unknown identity and duplicate identity admission.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
enum AdmitError: Error { case duplicate, unknown }
func admit(_ item: PlannerItem, into items: [PlannerItem]) throws -> [PlannerItem] {
  guard !items.contains(where: { $0.id == item.id }) else { throw AdmitError.duplicate }
  return items + [item]
}
func toggle(id: String, in items: [PlannerItem]) throws -> [PlannerItem] {
  guard let index = items.firstIndex(where: { $0.id == id }) else { throw AdmitError.unknown }
  var result = items
  result[index] = toggled(result[index])
  return result
}
let items = try admit(PlannerItem(id: "a", title: "Read", completed: false), into: [])
precondition(
  (try? admit(PlannerItem(id: "a", title: "Copy", completed: false), into: items)) == nil)
precondition((try? toggle(id: "missing", in: items)) == nil)
let toggledItems = try toggle(id: "a", in: items)
precondition(toggledItems[0].completed)
```

**Observe:** A second item with id a is refused, toggling an unknown id fails, and toggling a succeeds.

Both rules are checked in the domain before anything changes, so a duplicate cannot slip in and an unknown id cannot silently do nothing.

### Task 6: Transfer and justify

Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** The domain core in this lesson is a value type, `PlannerItem`, with a constant `id` and `title` and a mutable `completed` flag, plus a pure function `toggled` that copies the item, flips the flag and returns the copy. Example A checks the flag; Example B checks that identity and title survive. The lesson then moves to JourneyCore, the package that holds the same kind of logic for the real app.

**Why it is correct.** `PlannerItem` is a struct, so `var result = item` makes an independent copy. Toggling `result.completed` changes only the copy: `changed.completed` is true while `original.completed` stays false. Because `id` and `title` are `let` constants copied unchanged, `changed.id == original.id` and the titles match. That stable id is what lets navigation, persistence and SwiftUI diffing treat the edited value as the same item. The function reads no files, clock or global state, so the same input always gives the same output, which is what makes it testable without the app.

**A plausible wrong approach.** Making `PlannerItem` a class and mutating `item.completed` inside `toggled` would also flip the original, so the check `!original.completed` fails and undo has nothing to return to. Generating a fresh UUID for each edited item breaks identity: a list would treat the edit as a deletion plus an insertion. Reading a file inside a computed property getter (task 4) hides I/O and failure inside what looks like a plain value read.

**How to verify.** For task 2, add `renamed(_:to:)` that returns nil for an empty title and check both outcomes plus an unchanged id. For task 3, run `swift build` and `swift test` in JourneyCore before opening the Apple project; record whether a Swift toolchain was available, because a passing kernel does not show the app renders.

## Mechanism and diagnostic reasoning

An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.

A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.

A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

## Review before continuing

Run the reference and confirm it prints `swift-039: passed`, then rerun the guide's counterexample.
