// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Create and retrieve an item over real HTTP: change one input
// Copy Example A into a scratch `main.mjs` and change `JSON.stringify({ id: 'A', value: 2
// })` to `JSON.stringify({ id: 'A', value: 3 })`. Before running it, predict which check
// fails and which value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual(await created.json(), { id: 'A', value: 2 })`. Restoring the original
// line brings back the worked observation: 201 created; subsequent 200 list contains exactly
// A.

// Exercise 2: Reject malformed data before changing state: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `assert.deepEqual(await
// (await request(context, '/items!')).json(), []);`. Run Example B with that line, explain
// why the edited check now fails for the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual(await (await request(context, '/items')).json(), [])`; after it the line
// reads `assert.deepEqual(await (await request(context, '/items')).json(), []);` again and
// both 400; list remains empty.

// Exercise 3: Preserve original state on duplicate creation
// Create A with value 2, then try A with value 9.
// Expected: second request 409; stored value remains 2.

// Exercise 4: Enforce body and media-type contracts
// Send 513 body bytes, then a text/plain payload.
// Expected: 413 for size and 415 for media type.

// Exercise 5: Distinguish unknown routes and unsupported methods
// Request an absent path and DELETE on the item route.
// Expected: 404 and 405 respectively.

// Exercise 6: Correlate safe events and prove listener cleanup
// Request health, inspect its request id and event keys, then check the server after the
// helper exits.
// Expected: matching id and status; server no longer listening.

console.log("Implement the six exercises in your saved copy.");
