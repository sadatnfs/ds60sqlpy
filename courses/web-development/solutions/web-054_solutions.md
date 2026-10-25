# web-054: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An API contract describes inputs, outputs, error behavior and relevant operational limits. JSON is only the serialization format. A client needs to know whether minutes is an integer, whether a field can be null, which errors are recoverable and whether an operation changes state. Adding a field can be compatible for some clients while changing its meaning or type can break them.

Error responses should be structured and consistent without exposing internal exceptions. A validation error can identify fields; an unexpected internal error should provide a safe message and a correlation mechanism in a real deployment. Status codes, headers and body must agree. Returning a JSON error object with an unconditional 200 status makes clients and monitoring misinterpret failures.

Keep a response builder separate from the domain function. Encode with JSON_THROW_ON_ERROR and declare application/json in the real HTTP adapter. Decode test output and inspect types rather than comparing arbitrary whitespace. This CLI lesson models the response; the external HTTP fixture later checks actual status and headers. It does not enable cross-origin access automatically.

## Exercise 1: Distinguish a JSON number from a numeric-looking string.

30 and "30" have different JSON types and can affect client validation.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a consistent error code to invalid-input responses.

Clients can inspect a stable code without parsing human prose.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a response model that maps success and validation failure consistently.

Status, content type and JSON body agree with the declared contract.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose an internal exception serialized directly to a public response.

Translate it at the boundary and keep sensitive details in controlled diagnostics.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Round-trip a Unicode label and a boolean through JSON.

The decoded values retain their intended types and text.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain a backward-compatible versus breaking API change.

Compatibility depends on the documented client contract, especially type and semantic changes.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
