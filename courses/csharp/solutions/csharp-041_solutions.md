# csharp-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-041_solution.cs](csharp-041_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Map a valid request:** The kernel isolates validation and status selection from host configuration. Valid input maps to the created outcome.

**Reject before claiming success:** The response category is part of the public contract and must not disagree with domain acceptance. Invalid requests produce 400 decisions.

## Task answers

### Task 1: Predict and explain

Describe the valid request and its status/body contract.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The kernel isolates validation and status selection from host configuration. Valid input maps to the created outcome.

### Task 2: Guided modification

Add a maximum quantity rule and document its rejection.

No separate reference answer has been written for this task. Start from Example B: The response category is part of the public contract and must not disagree with domain acceptance. Invalid requests produce 400 decisions.

### Task 3: Independent construction

Run the separately prepared ApiLab project and inspect GET and POST responses.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Endpoint** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose returning 200 before input validation finishes.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

### Task 5: Boundary evidence

Test missing identity, zero quantity and unknown resource lookup.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Map a valid request) and Example B (Reject before claiming success).

### Task 6: Transfer and justify

Design idempotent update behavior and explain how duplicate creation differs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Endpoint**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.

A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.

An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

## Review before continuing

Run the reference and confirm that it prints `csharp-041: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
