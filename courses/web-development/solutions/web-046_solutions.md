# web-046: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-046.md`.

## Exercise 1: Identify status, headers and body in the response model.

**Expected answer:** They are separate fields with different protocol responsibilities.

**Approach:** Label each key in the array by role: `status` is the outcome code, `headers` describe the body, and `body` is the representation.

**Why:** The status tells the client what happened, headers describe the representation and caching, and the body carries the content.

**Plausible wrong approach:** Putting the content type inside the body text fails because clients read media type from headers, not from the body itself.

**How to verify:** Printing the array shows three top level keys, and the content type appears only under headers.

## Exercise 2: Add a not-found response for an unknown path.

**Expected evidence:** The unknown route returns 404 instead of pretending to be a successful page.

**Approach:** Add a final branch that returns status 404 with a short text body when no known path matches the request.

**Why:** A 404 tells clients that the resource does not exist, while a 200 page saying not found misleads caches and tools.

**Plausible wrong approach:** Returning 200 with a Page not found message fails because clients and crawlers then treat the missing page as successful content.

**How to verify:** Requesting /missing returns status 404 in the printed response array.

## Exercise 3: Build a pure router for health and lesson-summary requests.

**Expected evidence:** Known GET routes return their declared representations and unsupported requests are rejected.

**Approach:** Match path and method together, return the declared body for GET, an empty body for HEAD, and 405 with Allow for others.

**Why:** A pure router is easy to test because each request array maps to exactly one response array.

**Plausible wrong approach:** Checking only the path fails because POST or DELETE to the same path then reports success for an operation that never ran.

**How to verify:** GET /health returns 200 with ok, HEAD returns 200 with empty body, and DELETE returns 405.

## Exercise 4: Diagnose headers sent after body output in a real adapter.

**Expected answer:** Response metadata must be established before output begins, subject to the runtime's buffering behavior.

**Approach:** Find any `echo` or whitespace before the `header()` call and move the output after all headers are set.

**Why:** Once body output is flushed, PHP can no longer send headers, unless output buffering delays the flush.

**Plausible wrong approach:** Adding output buffering to hide the warning fails when buffers are flushed early, so the problem returns unpredictably.

**How to verify:** With the stray output removed, the real adapter sends the header with no headers already sent warning.

## Exercise 5: Test a known path with the wrong method.

**Expected evidence:** The route returns 405 with Allow: GET, HEAD, while HEAD itself succeeds with an empty body.

**Approach:** Request a known path with POST and read the status, the Allow header and the body of the returned array.

**Why:** RFC 9110 requires general-purpose servers to support GET and HEAD; other methods get 405 with an Allow header listing what is supported.

**Plausible wrong approach:** Returning 404 for the wrong method fails because the path exists, and the client is misled about what went wrong.

**How to verify:** The response shows status 405 and `Allow: GET, HEAD`, matching the reference router.

## Exercise 6: Explain what a CLI response model does not prove.

**Expected answer:** It does not qualify actual networking, server configuration, cookie handling or browser behavior.

**Approach:** Separate what the model shows, routing decisions as data, from what only a running server shows, such as transport and headers on the wire.

**Why:** Sockets, TLS, server configuration, cookies and browser behavior are absent, so the model proves only routing logic.

**Plausible wrong approach:** Claiming caching works because a `Cache-Control` key appears in the array fails because no client ever received it.

**How to verify:** Your answer names at least three behaviors, such as TLS and cookies, that need a real server test.

## Reference comparison

Open `courses/web-development/solutions/web-046_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
