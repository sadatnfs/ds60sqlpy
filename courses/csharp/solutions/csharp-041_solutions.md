# csharp-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-041_solution.cs](csharp-041_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Map a valid request:** The kernel isolates validation and status selection from host configuration. Valid input maps to the created outcome.

**Reject before claiming success:** The response category is part of the public contract and must not disagree with domain acceptance. Invalid requests produce 400 decisions.

## Reason through the six tasks

1. **Predict and explain.** Describe the valid request and its status/body contract.

2. **Guided modification.** Add a maximum quantity rule and document its rejection.

3. **Independent construction.** Run the separately prepared ApiLab project and inspect GET and POST responses.

4. **Diagnose a defect.** Diagnose returning 200 before input validation finishes.

5. **Boundary evidence.** Test missing identity, zero quantity and unknown resource lookup.

6. **Transfer and justify.** Design idempotent update behavior and explain how duplicate creation differs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.

A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.

An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
