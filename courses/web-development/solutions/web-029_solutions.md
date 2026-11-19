# web-029: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-029.md`.

## Exercise 1: Compare origins for the same host on two different ports.

**Expected answer:** Different ports form different origins even when the host matches.

**Why:** An origin is the triple of scheme, host and port, so a different port is a different origin.

## Exercise 2: Render an angle-bracket string safely as visible text.

**Expected evidence:** No extra element or event handler is created.

**Why:** textContent creates a text node, so the angle brackets display as characters and no img element or handler is created.

## Exercise 3: Build a small rendering demo that separates text handling from URL policy.

**Expected evidence:** Plain text remains data and navigation candidates pass an explicit scheme decision.

**Why:** Text needs safe insertion, while URLs need an explicit allowlist of schemes before they become navigation targets.

## Exercise 4: Explain why CORS is not authorization.

**Expected answer:** Non-browser clients can still send requests, and the server must enforce permissions.

**Why:** CORS only controls which browser pages may read responses; it does not stop requests, so the server must check permissions.

## Exercise 5: Inspect the preview without relying on cookies or parent-window access.

**Expected evidence:** The lesson remains functional within its isolated local contract.

**Why:** The sandboxed preview has no cookies or parent access, so a correct lesson works without them.

## Exercise 6: Explain the separate roles of escaping, validation, CSP and sandboxing.

**Expected answer:** They address contextual interpretation, accepted values, document capabilities and isolation respectively.

**Why:** Escaping stops data from being interpreted as code in one context, validation limits accepted values, CSP limits what the page may load or run, and sandboxing isolates a document's capabilities.

## Reference comparison

Open `courses/web-development/solutions/web-029_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
