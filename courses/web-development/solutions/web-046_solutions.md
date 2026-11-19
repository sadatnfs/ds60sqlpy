# web-046: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-046.md`.

## Exercise 1: Identify status, headers and body in the response model.

**Expected answer:** They are separate fields with different protocol responsibilities.

**Why:** The status tells the client what happened, headers describe the representation and caching, and the body carries the content.

## Exercise 2: Add a not-found response for an unknown path.

**Expected evidence:** The unknown route returns 404 instead of pretending to be a successful page.

**Why:** A 404 tells clients that the resource does not exist, while a 200 page saying not found misleads caches and tools.

## Exercise 3: Build a pure router for health and lesson-summary requests.

**Expected evidence:** Known GET routes return their declared representations and unsupported requests are rejected.

**Why:** A pure router is easy to test because each request array maps to exactly one response array.

## Exercise 4: Diagnose headers sent after body output in a real adapter.

**Expected answer:** Response metadata must be established before output begins, subject to the runtime's buffering behavior.

**Why:** Once body output is flushed, PHP can no longer send headers, unless output buffering delays the flush.

## Exercise 5: Test a known path with the wrong method.

**Expected evidence:** The route returns 405 with Allow: GET, HEAD, while HEAD itself succeeds with an empty body.

**Why:** RFC 9110 requires general-purpose servers to support GET and HEAD; other methods get 405 with an Allow header listing what is supported.

## Exercise 6: Explain what a CLI response model does not prove.

**Expected answer:** It does not qualify actual networking, server configuration, cookie handling or browser behavior.

**Why:** Sockets, TLS, server configuration, cookies and browser behavior are absent, so the model proves only routing logic.

## Reference comparison

Open `courses/web-development/solutions/web-046_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
