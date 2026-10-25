# web-029: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An origin is generally a combination of scheme, host and port. The browser uses origins to separate access to data and documents. The same-origin policy is not a complete application security system; a server still needs authentication, authorization and deliberate cross-origin behavior. CORS is a protocol for relaxing some browser response-reading restrictions, not a mechanism that makes an unsafe endpoint safe.

Injection occurs when data is interpreted as code or structure in a context where it should remain data. textContent avoids HTML parsing for text, while building an href still requires a separate URL policy. Content Security Policy can reduce what a document may load or execute, but it is a defense layer rather than a replacement for correct output handling. The classroom preview is deliberately isolated and network restricted.

Treat rendering contexts separately: HTML text, quoted HTML attribute, URL, JavaScript and CSS each have different rules. This reference renders an attack-shaped string only as text. No attack is performed against another site. A sandboxed iframe can have an opaque origin, so do not assume localStorage, cookies or a same-origin parent API exists inside the preview.

## Exercise 1: Compare origins for the same host on two different ports.

Different ports form different origins even when the host matches.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Render an angle-bracket string safely as visible text.

No extra element or event handler is created.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a small rendering demo that separates text handling from URL policy.

Plain text remains data and navigation candidates pass an explicit scheme decision.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why CORS is not authorization.

Non-browser clients can still send requests, and the server must enforce permissions.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Inspect the preview without relying on cookies or parent-window access.

The lesson remains functional within its isolated local contract.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the separate roles of escaping, validation, CSP and sandboxing.

They address contextual interpretation, accepted values, document capabilities and isolation respectively.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
