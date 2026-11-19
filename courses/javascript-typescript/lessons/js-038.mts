// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Handle and decode a successful request: change one input
// Copy Example A into a scratch `main.mts` and change `const reply = handle({ method:
// 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });` to `const reply =
// handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 3, b: 3 } });`. Before
// running it, predict which check fails and which value it now sees; then run it and restore
// the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(decoded.body.data.total, 5)`. Restoring the original line brings back the
// worked observation: status 200 and decoded total 5.

// Exercise 2: Return a stable invalid-input envelope: debug a regression
// A regression changed one token in Example B, so one line now reads `const reply = handle({
// method: 'POST', path: '/sum', requestId: 'R3', body: { a: '2', b: 3 } });`. Run Example B
// with that line, use the failing check to locate the defect and repair it without changing
// the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(reply.body.requestId, 'R2')`; after it the line reads `const reply =
// handle({ method: 'POST', path: '/sum', requestId: 'R2', body: { a: '2', b: 3 } });` again
// and status 400 with bad_request and matching request id.

// Exercise 3: Distinguish route and method failures
// Use an unknown path and an unsupported method.
// Expected: 404 not_found versus 405 method_not_allowed.

// Exercise 4: Reject version or status/body disagreement
// Decode an unsupported version and a success envelope paired with status 400.
// Expected: TypeError for both malformed replies.

// Exercise 5: Require success narrowing in checked client code
// Attempt data access before checking ok in an uncalled function.
// Expected: expected compiler error; correctly narrowed success remains usable.

// Exercise 6: Keep invalid payload details out of response errors
// Include a secret-looking extra field in an invalid request.
// Expected: bad_request response does not echo the supplied value.

console.log("Implement the six exercises in your saved copy.");
