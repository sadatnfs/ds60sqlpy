# swift-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-041_solution.swift](swift-041_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Parse an admitted route:** The parser translates untrusted text into a limited domain route. The admitted scheme and host resolve to item one.

**Reject unrelated or incomplete links:** A route parser is an allowlist, not a generic command interpreter. Unrelated schemes, missing identity and unlisted actions are rejected.

## Reason through the six tasks

1. **Predict and explain.** Trace each URL component into the route decision.

2. **Guided modification.** Add a separate explicit overview route.

3. **Independent construction.** Run JourneyApp and navigate by stable item identity.

4. **Diagnose a defect.** Diagnose navigation keyed by array position after reordering.

5. **Boundary evidence.** Test a missing item identity and an item deleted while its route is open.

6. **Transfer and justify.** Design a restoration format for navigation without storing view instances or private payloads.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.

A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.

Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
