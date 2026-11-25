// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Request a valid local calculation: change one input
// In a scratch copy of Example A, change `new URL('/sum?a=2&b=3', base)` to `new
// URL('/sum?a=3&b=3', base)`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.deepEqual(await
// response.json(), { total: 5 })`. Restoring `new URL('/sum?a=2&b=3', base)` brings back:
// status 200; application/json; total 5.

// Exercise 2: Inspect an HTTP error without expecting fetch rejection: diagnose an edited check
// Example B's check was edited to read `assert.deepEqual(await response.json(), { error:
// 'not_found!' });`. Run it, explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.deepEqual(await response.json(), { error: 'not_found!' });`. Restoring
// `assert.deepEqual(await response.json(), { error: 'not_found' });` brings back: fetch
// resolves; status 404, ok false, error not_found.

// Exercise 3: Encode query values through the URL API
// Round-trip a query containing spaces, ampersand and equals without contacting a server.
// Expected: the value round-trips as one parameter.

// Exercise 4: Reject repeated or invalid parameters
// Request repeated a values and a non-integer b value.
// Expected: both responses are 400 with invalid_parameters.

// Exercise 5: Reject an unsupported method
// POST to the read-only sum route without a body.
// Expected: status 405 and Allow: GET.

// Exercise 6: Guard arithmetic overflow after parsing
// Add one to Number.MAX_SAFE_INTEGER through the endpoint.
// Expected: status 400 rather than a rounded success value.

console.log("Implement the six exercises in your saved copy.");
