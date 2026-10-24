# csharp-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-039_solution.cs](csharp-039_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Decode a successful offline response:** A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection. The handler supplies count 3 without network access.

**Preserve unsuccessful status:** Response arrival and application success are separate facts. 503 remains an observable failure rather than a default successful count.

## Reason through the six tasks

1. **Predict and explain.** Trace transport, status, decoding and schema validation boundaries.

2. **Guided modification.** Return valid JSON with a missing count property and classify the failure.

3. **Independent construction.** Write a client method accepting a supplied HttpClient and CancellationToken.

4. **Diagnose a defect.** Diagnose converting every non-2xx response into an empty success result.

5. **Boundary evidence.** Test malformed JSON and an unexpected count type.

6. **Transfer and justify.** Design a retry policy that distinguishes safe reads from writes with unknown outcomes.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.

A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.

A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
