# web-047: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A server receives untrusted input even when the page supplied a constrained control. A caller can omit fields, send an array where a string was expected, alter a hidden value or bypass the browser entirely. Validate shape, type, length and domain rules before using values. An allowlist defines accepted choices; rejecting only known bad strings is usually harder to reason about.

Separate raw input, validated domain values and rendered output. Keep useful user input for redisplay after a validation error, but escape it in the HTML context. After a successful state-changing POST, a redirect to a GET page can reduce accidental resubmission on refresh. That pattern does not by itself provide idempotency, CSRF protection or authorization.

A pure validator returns a value and an error map. Check is_string before trim or numeric parsing because request fields can be arrays. For an integer text field, define an accepted syntax and range explicitly. The example uses a bounded decimal digit pattern, then converts only after it passes. The CLI inputs model POST data; no form is submitted.

## Exercise 1: Predict what happens when a caller sends topic[]=HTML.

The server can receive an array, so a string-shape check is required.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add an allowlist for supported topics.

Only explicitly declared topic values are accepted.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a validator returning cleaned values and field-specific errors.

Valid data has a complete domain value; invalid data has actionable errors and no partial write.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose trimming an array-shaped request value.

Validate its type before calling a string function.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test missing fields, arrays, out-of-range minutes and valid data.

Each case returns a deliberate validation result without an uncaught type error.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the limits of POST redirect GET.

It helps refresh behavior but does not replace authorization, CSRF checks or duplicate-operation design.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
