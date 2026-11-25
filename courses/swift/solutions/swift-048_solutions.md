# swift-048: explanation and comparison

Reference program: [swift-048_solution.swift](swift-048_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Produce a stable completion summary:** The report checks state and identity rather than only a formatted label. One of two uniquely identified items is complete.

**Preserve identity across a value update:** These are the core semantics needed by undo, navigation and persistence. The update retains identity and the prior snapshot.

## Task answers

### Task 1: Predict and explain

Trace one user action from view through model to domain state.

**Written answer.** In JourneyApp, tapping Save changes in ItemEditor calls store.update(id:title:completed:). PlanStore copies the plan into a candidate and calls StudyPlan.update, which finds the item by id and validates the new title. commit then writes the encoded candidate atomically and only afterward assigns plan, so @Observable publishes the change and PlanView redraws the row and the progress count.

### Task 2: Guided modification

Add a derived progress summary without duplicating stored completion counts.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let items = [
  CapstoneItem(id: "a", complete: true),
  CapstoneItem(id: "b", complete: false),
  CapstoneItem(id: "c", complete: true),
]
var progress: String { "\(items.filter(\.complete).count)/\(items.count) complete" }
precondition(progress == "2/3 complete")
```

**Observe:** Two of three items are complete, so the summary reads 2/3 complete.

The count is computed from the items each time, so there is no second stored number that could drift out of sync after an edit.

### Task 3: Independent construction

Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

**Written answer.** The JourneyCore half was run: on swift:6.3.3-amazonlinux2023, swift build ended with Build complete!, swift test reported Executed 4 tests, with 0 failures, and swift run journey-demo printed JourneyCore: 1/2 complete; round trip passed. Running the full JourneyApp needs a prepared Apple destination and was not done for this reference; follow its README and record the destination you actually used.

### Task 4: Diagnose a defect

Introduce and repair a stale-binding, duplicate-identity or failed-save defect.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
enum CapstoneError: Error { case duplicate }
func buggyAdd(_ item: CapstoneItem, to items: [CapstoneItem]) -> [CapstoneItem] { items + [item] }
func add(_ item: CapstoneItem, to items: [CapstoneItem]) throws -> [CapstoneItem] {
  guard !items.contains(where: { $0.id == item.id }) else { throw CapstoneError.duplicate }
  return items + [item]
}
let start = [CapstoneItem(id: "a", complete: false)]
let broken = buggyAdd(CapstoneItem(id: "a", complete: true), to: start)
precondition(Set(broken.map(\.id)).count != broken.count)
precondition((try? add(CapstoneItem(id: "a", complete: true), to: start)) == nil)
```

**Observe:** The buggy add lets two items share id a, and the repaired add refuses the duplicate.

Duplicate identity breaks lookup, navigation and saving, because one id now names two items. The repair checks identity before admitting a value, as StudyPlan.validate does.

### Task 5: Boundary evidence

Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
struct StoredItem: Codable, Equatable {
  let id: String
  let title: String
}
func validated(_ items: [StoredItem]) -> Bool {
  Set(items.map(\.id)).count == items.count && items.allSatisfy { !$0.title.isEmpty }
}
precondition(validated([]))
let long = StoredItem(id: "l", title: String(repeating: "word ", count: 200))
precondition(validated([long]))
precondition(!validated([StoredItem(id: "x", title: "A"), StoredItem(id: "x", title: "B")]))
precondition((try? JSONDecoder().decode([StoredItem].self, from: Data("{".utf8))) == nil)
let saved = try JSONEncoder().encode([long])
let reloaded = try JSONDecoder().decode([StoredItem].self, from: saved)
precondition(reloaded == [long])
```

**Observe:** Empty and long-title plans are valid, duplicate ids fail, malformed storage does not decode, and a save then reload returns the same item.

These portable checks cover the data rules. How long titles wrap and how the app reports malformed storage still have to be checked in JourneyApp itself.

### Task 6: Transfer and justify

Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `CapstoneItem` is a struct with a constant `id` and a mutable `complete` flag. Example A counts completed items and checks that ids are unique by comparing a `Set` of ids with the array count. Example B copies an item, marks the copy complete and checks that the id is kept and the original is unchanged. The capstone builds the full JourneyApp around these rules.

**Why it is correct.** In Example A only item a is complete, so `filter(\.complete).count` is 1. The ids "a" and "b" are distinct, so the set has two elements, equal to the array count; a duplicate would make the set smaller. In Example B `var changed = original` copies the struct, so setting `changed.complete` leaves `original.complete` false while both share id "a". Those two facts support undo, navigation by id and save and reload.

**A plausible wrong approach.** Storing a separate `completedCount` and incrementing it in the button action duplicates state: after a reload or an undo the stored count and the items can disagree. Task 2 asks for a derived summary instead. Allowing two items with id "a" would let a deep link or save open or overwrite the wrong one, which is why the uniqueness check is in Example A.

**How to verify.** Duplicate id "a" in Example A and confirm the set check fails. For tasks 3 and 5, test JourneyCore with `swift test`, then run JourneyApp on an Apple destination with an empty list, a long title, a corrupted save file and a save and relaunch, and record what happened in each case in the project README.

## Mechanism and diagnostic reasoning

The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.

A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.

A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

## Review before continuing

Run the reference and confirm it prints `swift-048: passed`, then rerun the guide's counterexample.
