# web-058: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Accepting a file creates a new trust boundary. A client-supplied filename, extension and MIME label are untrusted claims. A safe design sets a byte limit, allows only needed formats, checks actual content as appropriate, generates its own storage name and keeps uploads outside executable public directories. An image parser can itself have vulnerabilities, so format validation is part of a broader dependency and isolation policy.

Filesystem paths should be derived from an owned identifier and a controlled root, not concatenated from arbitrary request text. Avoid making user uploads executable or allowing path traversal into application source. Storage quotas, retention and deletion behavior matter because a valid file can still exhaust resources. The default classroom pad does not accept uploaded files, and this lesson does not add an upload endpoint.

PHP's upload APIs distinguish actual HTTP-uploaded files from arbitrary paths, but successful movement does not prove the content is safe. Treat sending email, calling a payment service or publishing a message as explicit side effects with credentials and failure handling. An outbox design can record an intended external action in the same database transaction as a domain update, then process it with idempotency controls. It does not magically make an external network action exactly once.

## Exercise 1: List the untrusted claims in an uploaded file request.

Filename, extension, declared media type, content and size all require a deliberate policy.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Design a maximum size and allowlist for one required format.

The policy rejects unnecessary formats and enforces a bounded resource budget.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Write an upload design with separate validation, storage and retrieval boundaries.

Files receive generated names, stay outside executable public paths and have ownership and retention rules.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose concatenating ../../ into a storage path.

User input must not determine an unrestricted filesystem location.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Model a timeout after a remote service may have accepted an action.

The outcome is ambiguous; retries need idempotency or reconciliation instead of assuming failure means nothing happened.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain which tests are needed before enabling uploads or email.

Exercise actual HTTP upload handling, malformed content, size limits, ownership, cleanup and controlled external-service failure behavior.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
