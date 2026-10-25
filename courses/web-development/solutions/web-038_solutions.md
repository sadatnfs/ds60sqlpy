# web-038: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

JSON is a data format, not a PHP object model or a validation system. Decoding can produce syntactically valid data with the wrong fields, wrong types or an unexpectedly deep structure. Treat parsing and contract validation as separate steps. The examples use tiny inline JSON and a temporary stream so no host path or persistent file is required.

A stream represents a readable or writable sequence of bytes. File operations can fail, return partial results or expose sensitive data if paths are chosen carelessly. In an application, accept an identifier and map it to an owned location instead of accepting an arbitrary user-supplied filesystem path. Bound size before reading untrusted content into memory, and close resources when finished.

Use JSON_THROW_ON_ERROR so invalid JSON becomes an exception instead of an ambiguous null result. Pass true when an associative-array representation is intended, then validate each required field. `php://temp` provides a temporary stream suitable for this local demonstration. Check resource creation and write results, rewind before reading, and close in a finally block.

## Exercise 1: Explain why valid JSON can still be invalid application input.

It may contain the wrong structure, types, ranges or required fields.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a bounded decoding depth and explicit parse errors.

Malformed or too-deep input produces an intentional failure.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Parse a small study record and round-trip it through a temporary stream.

The field contract passes and the returned bytes match the encoded value.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose an empty read caused by the stream cursor position.

Rewind before reading from the beginning.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Reject an unexpected field type and an oversized input string.

The program checks both byte budget and data contract before use.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why user-controlled paths need an ownership policy.

A path can escape the intended data area or expose unrelated files; identifiers should map through a reviewed boundary.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
