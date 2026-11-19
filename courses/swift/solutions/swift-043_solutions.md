# swift-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-043_solution.swift](swift-043_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accept the current request result:** Identity connects a result to the intent that authorized it. The matching generation updates current state.

**Ignore a superseded result:** Cancellation alone would not establish this guarantee because an operation may still complete. The stale response cannot overwrite the newer value.

## Task answers

### Task 1: Predict and explain

Trace current intent and result identity.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Identity connects a result to the intent that authorized it. The matching generation updates current state.

### Task 2: Guided modification

Advance the generation and accept only the new response.

No separate reference answer has been written for this task. Start from Example B: Cancellation alone would not establish this guarantee because an operation may still complete. The stale response cannot overwrite the newer value.

### Task 3: Independent construction

Implement a deterministic fake transport returning success and failure values.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Loading state** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose an old search response replacing a newer search result.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.

### Task 5: Boundary evidence

Test empty data, malformed data, non-success status and cancellation separately in the prepared adapter.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Accept the current request result) and Example B (Ignore a superseded result).

### Task 6: Transfer and justify

Design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Loading state**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A network-backed view needs more states than a Boolean loading flag. Idle, loading, ready and failed states carry different information and should be rendered honestly. Cancellation of an old request can reduce work, but a stale response can still arrive if the operation does not cooperate. A request generation or identity check prevents an older result from overwriting newer intent.

URLSession is a Foundation API with platform differences: Linux networking code requires FoundationNetworking. The ordinary pad uses an injected deterministic data source and a pure acceptance rule, so it contacts no server. The app lab explains where a real transport adapter belongs, with status, size, schema and cancellation checks before admission.

A request generation increments when intent changes. Accept a result only if its generation still matches current state. A transport protocol can return Data for a validated decoder while keeping the UI model independent of URLSession.

An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.

## Review before continuing

Run the reference and confirm that it prints `swift-043: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
