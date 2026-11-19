# swift-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-041_solution.swift](swift-041_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Parse an admitted route:** The parser translates untrusted text into a limited domain route. The admitted scheme and host resolve to item one.

**Reject unrelated or incomplete links:** A route parser is an allowlist, not a generic command interpreter. Unrelated schemes, missing identity and unlisted actions are rejected.

## Task answers

### Task 1: Predict and explain

Trace each URL component into the route decision.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The parser translates untrusted text into a limited domain route. The admitted scheme and host resolve to item one.

### Task 2: Guided modification

Add a separate explicit overview route.

No separate reference answer has been written for this task. Start from Example B: A route parser is an allowlist, not a generic command interpreter. Unrelated schemes, missing identity and unlisted actions are rejected.

### Task 3: Independent construction

Run JourneyApp and navigate by stable item identity.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Route** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose navigation keyed by array position after reordering.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

### Task 5: Boundary evidence

Test a missing item identity and an item deleted while its route is open.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Parse an admitted route) and Example B (Reject unrelated or incomplete links).

### Task 6: Transfer and justify

Design a restoration format for navigation without storing view instances or private payloads.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Route**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.

A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.

Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

## Review before continuing

Run the reference and confirm that it prints `swift-041: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
