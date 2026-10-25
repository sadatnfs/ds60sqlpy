# web-045: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A template combines trusted structure with data. If a visitor's text is inserted directly into HTML, the browser may interpret it as elements or script-capable attributes. Output escaping represents the data so it remains data in a particular destination context. It is not a one-time cleanup that makes a value safe everywhere. Keep the original validated value and encode it when crossing the output boundary.

For HTML text and ordinary quoted attribute values, htmlspecialchars with explicit flags and UTF-8 is a useful primitive. It is not a JavaScript-string encoder, a CSS sanitizer or a URL policy. A URL in an href needs a separate scheme and destination decision before attribute escaping. Avoid dynamic inline scripts and styles when a simpler data boundary is available.

Define a small e function that calls htmlspecialchars with ENT_QUOTES, ENT_SUBSTITUTE and UTF-8. Use it only for the contexts described by its contract. The CLI reference prints an HTML string as text so you can inspect the escaped bytes; it does not execute that string in a browser. A server template later uses the same contextual boundary before returning a response.

## Exercise 1: Predict the escaped form of a name containing < and &.

The special syntax characters become HTML character references.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add an escaping helper with an explicit UTF-8 contract.

The helper names its HTML context and handles quotes as well as angle brackets.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Render a study-card template from synthetic untrusted labels.

The structure stays fixed while labels are escaped at output.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why the same helper is insufficient for a JavaScript string.

JavaScript has a different parser and escaping rules; use a dedicated serialization boundary.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test quotes, ampersands and an attack-shaped tag string.

The resulting HTML string contains escaped data rather than an additional live element.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why validated text still needs output escaping.

A valid name can contain syntax characters that are meaningful in the destination context.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
