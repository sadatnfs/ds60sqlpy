# js-040: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A local service combines transport handling with domain state and resource ownership. The HTTP handler should parse and validate a request before changing state, return a documented status, and finish every response. The domain operation here stores a small item with a unique id and bounded integer value. Duplicate creation returns a conflict without replacing the original item. This in-memory repository is lost when the process stops; it is not a database or a durable transaction system.

The fixture creates an actual HTTP server on an ephemeral 127.0.0.1 port and sends real fetch requests. Each exercise gets a fresh repository and server, preventing one scenario from making another pass through leftover state. The accepted body is JSON with an exact schema. A byte limit bounds retained request data, and unexpected media types or unsupported methods receive distinct errors. Client timeouts bound waiting, while finally closes active connections and the owned listener.

Observability records the operation's outcome without copying the full request. A generated request id is returned in a header and appears in a small event record with a normalized route and status. Unknown routes are logged as unknown rather than preserving arbitrary path text. This makes the evidence useful for correlating a request and its result while avoiding a second uncontrolled payload store in logs.

The service is an offline teaching fixture with no authentication, TLS, durable storage or public deployment claim. Loopback binding reduces exposure but does not establish a security sandbox. A production service would need those operational boundaries in addition to the contract and cleanup mechanisms demonstrated here. The reference's actual socket exchanges establish more than a pure handler unit test, but still only for the bounded local scenarios.

**Transport integration:** Testing actual request and response exchange through sockets.

**Repository lifetime:** The persistence scope of the state backing domain operations.

**Conflict:** A request that would violate an existing-state invariant.

**Structured event:** A bounded diagnostic record with named, intentionally selected fields.

## Reading the implementation

createServer delegates to an async dispatcher and captures unexpected rejections. Request bodies are read incrementally; only bytes within the configured cap are retained. JSON parsing and exact-field checks occur before Map insertion. Responses set application/json and an x-request-id header. The context tracks metrics after choosing a status. withService closes connections and awaits server.close in finally, even when a client assertion fails.

## Exercise 1: Create and retrieve an item over real HTTP

Task: POST item A with value 2, then GET the list.

The assertions cross the real transport boundary. A typed or pure handler result alone would not check serialization, headers, routing or socket cleanup.

```javascript
await withService(async context => {
  const created = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) });
  assert.equal(created.status, 201);
  assert.deepEqual(await created.json(), { id: 'A', value: 2 });
  const listed = await request(context, '/items');
  assert.equal(listed.status, 200);
  assert.deepEqual(await listed.json(), [{ id: 'A', value: 2 }]);
});
```

**Expected:** 201 created; subsequent 200 list contains exactly A.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject malformed data before changing state

Task: Send malformed JSON and a wrong-shaped object, then inspect the repository through GET.

The failure is atomic relative to the in-memory mutation. No partial record is inserted before validation finishes.

```javascript
await withService(async context => {
  for (const body of ['{broken', JSON.stringify({ id: 'A', value: 'wrong' })]) {
    const response = await request(context, '/items', { method: 'POST', body });
    assert.equal(response.status, 400);
    await response.text();
  }
  assert.deepEqual(await (await request(context, '/items')).json(), []);
});
```

**Expected:** both 400; list remains empty.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Preserve original state on duplicate creation

Task: Create A with value 2, then try A with value 9.

A duplicate business identifier is not an instruction to overwrite. The explicit conflict status preserves both the domain invariant and a diagnosable client outcome.

```javascript
await withService(async context => {
  await (await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) })).text();
  const duplicate = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 9 }) });
  assert.equal(duplicate.status, 409);
  assert.deepEqual(await duplicate.json(), { error: 'duplicate_id' });
  assert.deepEqual(await (await request(context, '/items')).json(), [{ id: 'A', value: 2 }]);
});
```

**Expected:** second request 409; stored value remains 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Enforce body and media-type contracts

Task: Send 513 body bytes, then a text/plain payload.

Representation size and representation format are separate boundaries. A JSON parser should not be used as a substitute for either policy.

```javascript
await withService(async context => {
  const large = await request(context, '/items', { method: 'POST', body: 'x'.repeat(513) });
  assert.equal(large.status, 413); await large.text();
  const wrongType = await request(context, '/items', { method: 'POST', body: '{}', headers: { 'content-type': 'text/plain' } });
  assert.equal(wrongType.status, 415); await wrongType.text();
});
```

**Expected:** 413 for size and 415 for media type.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Distinguish unknown routes and unsupported methods

Task: Request an absent path and DELETE on the item route.

A method is part of endpoint semantics. Returning one generic status would remove information needed by a client or operator to diagnose the request.

```javascript
await withService(async context => {
  const missing = await request(context, '/missing');
  assert.equal(missing.status, 404); await missing.text();
  const wrongMethod = await request(context, '/items', { method: 'DELETE' });
  assert.equal(wrongMethod.status, 405); await wrongMethod.text();
});
```

**Expected:** 404 and 405 respectively.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Correlate safe events and prove listener cleanup

Task: Request health, inspect its request id and event keys, then check the server after the helper exits.

The event records only selected metadata. Cleanup is observed after the helper completes, rather than inferred from the presence of a finally block.

```javascript
let owned;
await withService(async context => {
  owned = context.server;
  const response = await request(context, '/health');
  const id = response.headers.get('x-request-id');
  assert.deepEqual(await response.json(), { status: 'ready' });
  assert.equal(context.events[0].requestId, id);
  assert.deepEqual(Object.keys(context.events[0]).sort(), ['method', 'requestId', 'route', 'status']);
  assert.equal(context.events[0].status, 200);
});
assert.equal(owned.listening, false);
```

**Expected:** matching id and status; server no longer listening.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
