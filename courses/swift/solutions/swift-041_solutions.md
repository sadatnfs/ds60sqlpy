# swift-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-041_solution.swift](swift-041_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Parse an admitted route:** The parser translates untrusted text into a limited domain route. The admitted scheme and host resolve to item one.

**Reject unrelated or incomplete links:** A route parser is an allowlist, not a generic command interpreter. Unrelated schemes, missing identity and unlisted actions are rejected.

## Task answers

### Task 1: Predict and explain

Trace each URL component into the route decision.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let parts = URLComponents(string: "journey://item/one")!
precondition(parts.scheme == "journey" && parts.host == "item" && parts.path == "/one")
precondition(parts.query == nil && parts.fragment == nil)
precondition(parseRoute("journey://item/one?x=1") == nil)
precondition(parseRoute("journey://item/one/two") == nil)
```

**Observe:** The scheme, host and one path segment admit the link, while an added query or a second path segment rejects it.

Each component is a separate gate: scheme and host pick the route family, query and fragment must be absent, and the path must hold exactly one identity segment.

### Task 2: Guided modification

Add a separate explicit overview route.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
enum AppRoute: Equatable {
  case overview
  case item(String)
}
func parseAppRoute(_ text: String) -> AppRoute? {
  guard let url = URLComponents(string: text), url.scheme == "journey", url.query == nil,
    url.fragment == nil
  else { return nil }
  let parts = url.path.split(separator: "/")
  switch (url.host, parts.count) {
  case ("overview"?, 0): return .overview
  case ("item"?, 1): return .item(String(parts[0]))
  default: return nil
  }
}
precondition(parseAppRoute("journey://overview") == .overview)
precondition(parseAppRoute("journey://overview/extra") == nil)
precondition(parseAppRoute("journey://item/one") == .item("one"))
```

**Observe:** journey://overview becomes the overview route, an overview with a path is rejected, and item links still work.

The overview is its own explicit case with its own shape rule, rather than a special value of item, so each accepted link has exactly one meaning.

### Task 3: Independent construction

Run JourneyApp and navigate by stable item identity.

**Written answer.** This task needs a prepared Mac and was not run for this reference. In JourneyApp, each row is NavigationLink(value: item.id), and navigationDestination(for: String.self) looks the id up in store.plan.items. Add two items, open one, go back, add another and reopen: the editor always shows the item whose id was pushed, not whatever now sits at that row position.

### Task 4: Diagnose a defect

Diagnose navigation keyed by array position after reordering.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let items = ["a": "Read", "b": "Practice"]
var order = ["a", "b"]
let selectedIndex = 0
let selectedID = order[selectedIndex]
order.reverse()
precondition(items[order[selectedIndex]] == "Practice")
precondition(items[selectedID] == "Read")
```

**Observe:** After reordering, position 0 now names Practice, while the stored id still names Read.

An array offset identifies a slot, not an item; reordering, inserting or deleting moves a different item into the slot. Navigating by stable id keeps the route attached to the same item.

### Task 5: Boundary evidence

Test a missing item identity and an item deleted while its route is open.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
precondition(parseRoute("journey://item/") == nil)
var items = ["one": "Read"]
let route = parseRoute("journey://item/one")
items["one"] = nil
var screen = "none"
if case .item(let id)? = route { screen = items[id] ?? "Item unavailable" }
precondition(screen == "Item unavailable")
```

**Observe:** A link with no identity is rejected, and a route to an item deleted while open resolves to Item unavailable.

The route stays valid as syntax, but the lookup happens at display time, so a deleted item gets an explicit unavailable screen, which matches the ContentUnavailableView in JourneyApp.

### Task 6: Transfer and justify

Design a restoration format for navigation without storing view instances or private payloads.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Run JourneyApp and navigate by stable item identity) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `parseRoute` turns untrusted text into an optional `Route`. It builds `URLComponents` from the string and returns nil unless the scheme is exactly `journey`, the host is exactly `item`, and there is no query or fragment. It then splits the path on slashes and accepts the link only when exactly one non-empty segment remains, which becomes the item id in `.item(id)`. Example A parses a valid link; Example B feeds three links that must be refused.

**Why it is correct.** For `journey://item/one`, `URLComponents` reports scheme `journey`, host `item` and path `/one`. Splitting `/one` on `/` drops the empty leading piece and leaves `["one"]`, so the count is 1 and the result is `.item("one")`. For `https://example.invalid/one` the scheme check fails first. For `journey://item/` the path is `/`, which splits into an empty array, so the count check fails. For `journey://delete/one` the host is `delete`, which is not on the list. Every accepted link therefore names one item by its stable id and nothing else, because the guard is an allowlist: anything not matched explicitly returns nil.

**A plausible wrong approach.** Treating the host as a command and dispatching on any value would let `journey://delete/one` reach a delete handler, turning a link into a remote control. Accepting `parts.first` without checking the count would map `journey://item/one/extra` to item one and silently discard the rest. Keying navigation by array index instead of id is the task 4 defect: after a reorder the same link opens a different item.

**How to verify.** Add checks for `journey://item/one?x=1` and `journey://item/one/two`, both of which should return nil. For task 2, add `case overview` and accept only `journey://overview` with an empty path, then confirm the old cases still hold. For task 5, open a route, delete its item, and confirm the app shows a missing-item state instead of crashing.

## Mechanism and diagnostic reasoning

Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.

A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.

Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

## Review before continuing

Run the reference and confirm that it prints `swift-041: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
