# js-017: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

HTTP transfers representations between a client and a server using a method, target, headers, status and body. A successful TCP exchange is not the same as a successful application response. fetch resolves for HTTP error statuses such as 404; callers must inspect status or ok. Parsing JSON is another separate stage, and schema validation remains necessary after successful parsing.

A URL parser separates the path, query and origin using defined encoding rules. Constructing query strings by concatenating user text can change the meaning of characters such as ampersand or equals. URLSearchParams encodes values and supports repeated keys. Applications must decide whether repeated parameters are allowed, rejected or combined instead of silently choosing a surprising value.

This lesson runs a real local HTTP server on an ephemeral port bound only to 127.0.0.1. The server handles a tiny read-only sum endpoint. It validates the method, exact parameter multiplicity and safe integer domain before calculating. The client sends actual requests and reads actual responses. The fixture has no authentication, persistence, TLS, rate limiting or public deployment claim. Loopback-only binding and a tiny bounded response make it appropriate for learning the protocol boundary.

**HTTP status:** The server's protocol-level result code.

**Representation:** The bytes and media type describing a resource or result.

**Query encoding:** Escaping values so delimiters retain their structural meaning.

**Application validation:** Checking parsed values against the endpoint's domain contract.

## Reading the implementation

createServer receives request and response objects. Construct new URL(request.url, a known base) to parse the target. searchParams.getAll lets the handler check duplicate parameters. writeHead selects the status and content type; end finishes the body. server.listen(0, '127.0.0.1') asks the OS for an available local port. fetch uses AbortSignal.timeout as a waiting bound. In finally, closeAllConnections and close ensure the fixture releases its listener even if an assertion fails.

## Exercise 1: Request a valid local calculation

Task: GET /sum with a=2 and b=3 and inspect status, content type and JSON.

The checks distinguish transport completion, protocol success and representation content. An endpoint can respond successfully at one layer while violating another layer's contract.

```javascript
await withServer(async (base) => {
  const response = await fetch(new URL('/sum?a=2&b=3', base), {
    signal: AbortSignal.timeout(2000),
  });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /application\/json/u);
  assert.deepEqual(await response.json(), { total: 5 });
});
```

**Expected:** status 200; application/json; total 5.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Inspect an HTTP error without expecting fetch rejection

Task: Request an unknown route and inspect the actual response.

fetch rejects for failures such as network errors or aborts, not simply because the server sent a 404. A client that only catches rejection may mistakenly treat a protocol error body as success data.

```javascript
await withServer(async (base) => {
  const response = await fetch(new URL('/missing', base), { signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 404);
  assert.equal(response.ok, false);
  assert.deepEqual(await response.json(), { error: 'not_found' });
});
```

**Expected:** fetch resolves; status 404, ok false, error not_found.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Encode query values through the URL API

Task: Round-trip a query containing spaces, ampersand and equals without contacting a server.

URLSearchParams preserves delimiters as data by encoding them. This is URL encoding, not HTML escaping or SQL parameter binding; each boundary has its own rules.

```javascript
const url = new URL('http://127.0.0.1/search');
url.searchParams.set('q', 'a & b=c');
assert.equal(url.searchParams.get('q'), 'a & b=c');
assert.equal([...url.searchParams].length, 1);
assert.ok(url.href.includes('%26'));
```

**Expected:** the value round-trips as one parameter.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Reject repeated or invalid parameters

Task: Request repeated a values and a non-integer b value.

Checking getAll length prevents an ambiguous duplicate-parameter policy. The numeric parser rejects strings that JavaScript Number might otherwise coerce in unintended ways.

```javascript
await withServer(async (base) => {
  for (const path of ['/sum?a=1&a=2&b=3', '/sum?a=1&b=hello']) {
    const response = await fetch(new URL(path, base), { signal: AbortSignal.timeout(2000) });
    assert.equal(response.status, 400);
    assert.deepEqual(await response.json(), { error: 'invalid_parameters' });
  }
});
```

**Expected:** both responses are 400 with invalid_parameters.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Reject an unsupported method

Task: POST to the read-only sum route without a body.

A route includes method semantics, not just its path. Explicit method rejection prevents an accidental write-looking request from being accepted as an ordinary read.

```javascript
await withServer(async (base) => {
  const response = await fetch(new URL('/sum?a=1&b=2', base), {
    method: 'POST',
    signal: AbortSignal.timeout(2000),
  });
  assert.equal(response.status, 405);
  assert.equal(response.headers.get('allow'), 'GET');
  assert.deepEqual(await response.json(), { error: 'method_not_allowed' });
});
```

**Expected:** status 405 and Allow: GET.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Guard arithmetic overflow after parsing

Task: Add one to Number.MAX_SAFE_INTEGER through the endpoint.

Each input can be a safe integer while the result is outside the safe range. Validate derived output invariants as well as input syntax.

```javascript
await withServer(async (base) => {
  const url = new URL('/sum', base);
  url.searchParams.set('a', String(Number.MAX_SAFE_INTEGER));
  url.searchParams.set('b', '1');
  const response = await fetch(url, { signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), { error: 'unsafe_total' });
});
```

**Expected:** status 400 rather than a rounded success value.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
