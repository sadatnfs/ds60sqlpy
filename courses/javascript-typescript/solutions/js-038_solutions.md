# js-038: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A typed API contract connects request validation, domain behavior, transport status and response decoding. TypeScript interfaces document what checked callers expect, but bytes crossing a process boundary are unknown again. JSON round-tripping is therefore part of the test: a server-side typed value must serialize into a representation that the client actually validates and understands.

This lesson defines a versioned sum endpoint with a discriminated success/error envelope and an explicit request identifier. HTTP-like status and body meaning must agree: a success body belongs to status 200, while a failure body carries a documented category for invalid input, absent route or unsupported method. An envelope that says success inside a 400 response creates an ambiguous client policy, even when both pieces are individually well-formed JSON.

The handler here is a pure in-memory function, not an HTTP server. It makes domain and representation contracts easy to test independently. Lesson 040 adds actual local transport. This separation allows malformed requests, version mismatches and information exposure to be tested without conflating them with socket behavior. The error message is a stable generic diagnostic; it does not echo arbitrary request bodies or secret-looking input.

A version field identifies this schema generation. It does not automatically migrate old clients or guarantee compatibility. Adding a required field or changing the meaning of a status can break consumers despite leaving function names unchanged. Contract tests should exercise the client's decoding behavior as well as the server's typed construction.

**Envelope:** A response structure distinguishing success data from failure information.

**Contract test:** A test checking that producer and consumer agree at an actual representation boundary.

**Versioned schema:** A declared generation of a payload shape and meaning.

**Transport/domain agreement:** Consistency between status code and response-body interpretation.

## Reading the implementation

The Reply type connects a status union with an Envelope union, while decodeReply independently checks unknown runtime values. A record guard establishes property access, then explicit comparisons check version, ok, fields and status agreement. Narrow ok before reading data or error. The handler validates exact input keys and safe integer results before constructing a success. Its return object is a fresh value suitable for serialization.

## Exercise 1: Handle and decode a successful request: change one input

Task: In a scratch copy of Example A, change `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });` to `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 3, b: 3 } });`. Which check fails, and what value does it see?

The JSON boundary removes any purely static guarantee. The client decoder re-establishes the runtime schema before using the success payload.

The unchanged code is the exercise block of Example A:

```typescript
const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });
const decoded = decodeReply(JSON.parse(JSON.stringify(reply)));
assert.equal(decoded.status, 200);
if (!decoded.body.ok) throw new Error(decoded.body.error.message);
assert.equal(decoded.body.data.total, 5);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(decoded.body.data.total, 5)`. Restoring `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });` brings back: status 200 and decoded total 5.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });`.

## Exercise 2: Return a stable invalid-input envelope: debug a regression

Task: A regression made one Example B line read `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R3', body: { a: '2', b: 3 } });`. Locate and repair it without editing the check.

The failure is represented deliberately rather than relying on JavaScript coercion. A stable category is easier for clients to branch on than free-form error prose.

The unchanged code is the exercise block of Example B:

```typescript
const reply = handle({ method: 'POST', path: '/sum', requestId: 'R2', body: { a: '2', b: 3 } });
assert.equal(reply.status, 400);
if (reply.body.ok) throw new Error('expected failure');
assert.equal(reply.body.error.code, 'bad_request');
assert.equal(reply.body.requestId, 'R2');
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(reply.body.requestId, 'R2')`. Restoring `const reply = handle({ method: 'POST', path: '/sum', requestId: 'R2', body: { a: '2', b: 3 } });` brings back: status 400 with bad_request and matching request id.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Distinguish route and method failures

Task: Use an unknown path and an unsupported method.

The handler's routing policy is explicit. Transport integration must preserve these distinctions rather than turning every error into 500 or 200.

```typescript
assert.equal(handle({ method: 'POST', path: '/missing', requestId: 'R3', body: null }).status, 404);
assert.equal(handle({ method: 'GET', path: '/sum', requestId: 'R4', body: null }).status, 405);
```

**Expected:** 404 not_found versus 405 method_not_allowed.

**Verify:** Keep `assert.equal(handle({ method: 'GET', path: '/sum', requestId: 'R4', body: null }).status, 405)`. Control: editing it to `assert.equal(handle({ method: 'GET', path: '/sum!', requestId: 'R4', body: null }).status, 405);` must make the check fail; then restore it.

## Exercise 4: Reject version or status/body disagreement

Task: Decode an unsupported version and a success envelope paired with status 400.

A client should reject a contradictory contract rather than choosing whichever part happens to be convenient. Version mismatch remains visible for migration or diagnosis.

```typescript
const valid = handle({ method: 'POST', path: '/sum', requestId: 'R5', body: { a: 1, b: 1 } });
assert.throws(() => decodeReply({ ...valid, body: { ...valid.body, version: 2 } }), TypeError);
assert.throws(() => decodeReply({ ...valid, status: 400 }), TypeError);
```

**Expected:** TypeError for both malformed replies.

**Verify:** Keep the check `assert.throws(() => decodeReply({ ...valid, status: 400 }), TypeError)`; name an input that would make it fail and the value that changes.

## Exercise 5: Require success narrowing in checked client code

Task: Attempt data access before checking ok in an uncalled function.

The compiler protects internal client logic after decoding. It does not replace the decoder that establishes the envelope at runtime.

```typescript
function negativeTypeCheck(envelope: Envelope): void {
  // @ts-expect-error Failure envelopes do not contain data.
  void envelope.data.total;
}
void negativeTypeCheck;
assert.equal(
  decodeReply(handle({ method: 'POST', path: '/sum', requestId: 'R6', body: { a: 0, b: 0 } }))
    .status,
  200,
);
```

**Expected:** expected compiler error; correctly narrowed success remains usable.

**Verify:** Keep `assert.equal(decodeReply(handle({ method: 'POST', path: '/sum', requestId: 'R6', body: { a: 0, b: 0 } })).status, 200)`. Control: editing it to `decodeReply(handle({ method: 'POST!', path: '/sum', requestId: 'R6', body: { a: 0, b: 0 } }))` must make the check fail; then restore it.

## Exercise 6: Keep invalid payload details out of response errors

Task: Include a secret-looking extra field in an invalid request.

An error response is another output boundary. Generic domain diagnostics can be useful without reflecting arbitrary request content into logs or clients.

```typescript
const reply = handle({
  method: 'POST',
  path: '/sum',
  requestId: 'R7',
  body: { a: 1, b: 2, token: 'fixture-secret-value' },
});
assert.equal(reply.status, 400);
assert.equal(JSON.stringify(reply).includes('fixture-secret-value'), false);
```

**Expected:** bad_request response does not echo the supplied value.

**Verify:** Keep `assert.equal(reply.status, 400)`. Control: changing `method: 'POST',` to `method: 'POST!',` must make that check fail; then restore it.

## After comparison

Fresh case: add version 2 with a `difference` field. Predict how a version-1 client decodes a version-2 reply, and write a decoder branch that accepts both versions without trusting the status alone. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
