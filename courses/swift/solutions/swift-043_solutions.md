# swift-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-043_solution.swift](swift-043_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accept the current request result:** Identity connects a result to the intent that authorized it. The matching generation updates current state.

**Ignore a superseded result:** Cancellation alone would not establish this guarantee because an operation may still complete. The stale response cannot overwrite the newer value.

## Task answers

### Task 1: Predict and explain

Trace current intent and result identity.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
var state = LoadState(generation: 1, title: nil)
state.generation += 1
state.accept("first", generation: 1)
precondition(state.title == nil)
state.accept("second", generation: 2)
precondition(state.title == "second")
```

**Observe:** After intent moves to generation 2, the reply tagged 1 is ignored and the reply tagged 2 is shown.

generation records the current intent, and each reply carries the generation of the request that produced it; only a matching pair may change the visible title.

### Task 2: Guided modification

Advance the generation and accept only the new response.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var state = LoadState(generation: 3, title: "three")
state.generation = 4
state.accept("late three", generation: 3)
state.accept("four", generation: 4)
precondition(state.title == "four")
```

**Observe:** After advancing to generation 4, the late reply for 3 is dropped and four is accepted.

Advancing the generation when a new request starts makes every older in-flight reply stale at once, without having to cancel each one first.

### Task 3: Independent construction

Implement a deterministic fake transport returning success and failure values.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let fake = FakeTransport(responses: [
  "/ok": TransportResponse(status: 200, body: Data("Read".utf8)),
  "/down": TransportResponse(status: 503, body: Data()),
])
let title = try await loadTitle("/ok", using: fake)
precondition(title == "Read")
var failure: TitleLoadError?
do { _ = try await loadTitle("/down", using: fake) } catch let error as TitleLoadError {
  failure = error
}
precondition(failure == .status(503))
```

**Observe:** The fake returns Read for /ok and a status 503 failure for /down, the same way on every run.

The loader depends on a protocol, so a fixed table of responses replaces the network; success and failure are reproducible without sockets, timing or a server.

### Task 4: Diagnose a defect

Diagnose an old search response replacing a newer search result.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
var state = LoadState(generation: 0, title: nil)
state.generation = 1
let oldQuery = state.generation
state.generation = 2
let newQuery = state.generation
state.accept("results for re", generation: newQuery)
state.accept("results for r", generation: oldQuery)
precondition(state.title == "results for re")
```

**Observe:** The slower reply for the old query arrives last but cannot overwrite results for re.

Without a request identity, whichever reply finishes last wins, so a slow old search can replace a newer one. Tagging each reply with its generation lets late replies be dropped.

### Task 5: Boundary evidence

Test empty data, malformed data, non-success status and cancellation separately in the prepared adapter.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
enum Outcome: Equatable {
  case title(String)
  case empty, malformed
  case status(Int)
}
func adapt(status: Int, body: Data) -> Outcome {
  guard status == 200 else { return .status(status) }
  guard !body.isEmpty else { return .empty }
  guard let text = String(data: body, encoding: .utf8) else { return .malformed }
  return .title(text)
}
precondition(adapt(status: 200, body: Data()) == .empty)
precondition(adapt(status: 200, body: Data([0xFF, 0xFE])) == .malformed)
precondition(adapt(status: 404, body: Data("x".utf8)) == .status(404))
let task = Task { () -> Bool in
  do {
    try await Task.sleep(for: .seconds(30))
    return false
  } catch { return error is CancellationError }
}
task.cancel()
let cancelled = await task.value
precondition(cancelled)
```

**Observe:** Empty, malformed and 404 replies map to three different outcomes, and the cancelled request ends with CancellationError.

Each case gets its own outcome so the UI can explain it, and cancellation is a separate path rather than a failure, which keeps a cancelled search from showing an error.

### Task 6: Transfer and justify

Design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Implement a deterministic fake transport returning success and failure values) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `LoadState` keeps a `generation` number for the current request and an optional `title`. Its `accept` method stores a result only when the result's generation equals the current one. Example A delivers a matching generation; Example B delivers a result tagged with an older generation. The task 3 answer is a fake transport that returns fixed success and failure values.

**Why it is correct.** In Example A both generations are 2, so the guard passes and the title becomes "new". In Example B the state is at generation 2 and the late result carries 1; the guard fails, `accept` returns early and the title remains "new". Because the check uses identity rather than arrival time, it holds even when an old request finishes after a newer one.

**A plausible wrong approach.** Assigning every arriving result to `title` is the task 4 defect: if the user searches "a" and then "ab", and the slower "a" response arrives last, it overwrites the newer result. Relying on cancelling the old request does not fix this, because a request may already have completed and be delivering its value when cancel is called.

**How to verify.** For task 2, set `generation` to 3, accept a result tagged 2 and confirm it is ignored, then accept one tagged 3. For task 5, use the fake transport to return empty data, malformed JSON and a 500 status, and confirm each produces its own error state rather than a blank success.

## Mechanism and diagnostic reasoning

A network-backed view needs more states than a Boolean loading flag. Idle, loading, ready and failed states carry different information and should be rendered honestly. Cancellation of an old request can reduce work, but a stale response can still arrive if the operation does not cooperate. A request generation or identity check prevents an older result from overwriting newer intent.

URLSession is a Foundation API with platform differences: Linux networking code requires FoundationNetworking. The ordinary pad uses an injected deterministic data source and a pure acceptance rule, so it contacts no server. The app lab explains where a real transport adapter belongs, with status, size, schema and cancellation checks before admission.

A request generation increments when intent changes. Accept a result only if its generation still matches current state. A transport protocol can return Data for a validated decoder while keeping the UI model independent of URLSession.

An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.

## Review before continuing

Run the reference and confirm that it prints `swift-043: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
