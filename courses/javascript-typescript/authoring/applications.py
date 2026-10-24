from render import add, ex
NODE = 'https://nodejs.org/download/release/v24.11.0/docs/api/'
TS = 'https://www.typescriptlang.org/docs/handbook/2/'

add(38,
'''A typed API contract connects request validation, domain behavior, transport status and response decoding. TypeScript interfaces document what checked callers expect, but bytes crossing a process boundary are unknown again. JSON round-tripping is therefore part of the test: a server-side typed value must serialize into a representation that the client actually validates and understands.

This lesson defines a versioned sum endpoint with a discriminated success/error envelope and an explicit request identifier. HTTP-like status and body meaning must agree: a success body belongs to status 200, while a failure body carries a documented category for invalid input, absent route or unsupported method. An envelope that says success inside a 400 response creates an ambiguous client policy, even when both pieces are individually well-formed JSON.

The handler here is a pure in-memory function, not an HTTP server. It makes domain and representation contracts easy to test independently. Lesson 040 adds actual local transport. This separation allows malformed requests, version mismatches and information exposure to be tested without conflating them with socket behavior. The error message is a stable generic diagnostic; it does not echo arbitrary request bodies or secret-looking input.

A version field identifies this schema generation. It does not automatically migrate old clients or guarantee compatibility. Adding a required field or changing the meaning of a status can break consumers despite leaving function names unchanged. Contract tests should exercise the client\'s decoding behavior as well as the server\'s typed construction.''',
'''The Reply type connects a status union with an Envelope union, while decodeReply independently checks unknown runtime values. A record guard establishes property access, then explicit comparisons check version, ok, fields and status agreement. Narrow ok before reading data or error. The handler validates exact input keys and safe integer results before constructing a success. Its return object is a fresh value suitable for serialization.''',
[('Envelope','A response structure distinguishing success data from failure information.'),('Contract test','A test checking that producer and consumer agree at an actual representation boundary.'),('Versioned schema','A declared generation of a payload shape and meaning.'),('Transport/domain agreement','Consistency between status code and response-body interpretation.')],[
ex('Handle and decode a successful request','Send 2 and 3 through the handler, JSON round-trip its reply, then decode it.','status 200 and decoded total 5.',r'''const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });
const decoded = decodeReply(JSON.parse(JSON.stringify(reply)));
assert.equal(decoded.status, 200);
if (!decoded.body.ok) throw new Error(decoded.body.error.message);
assert.equal(decoded.body.data.total, 5);''','The JSON boundary removes any purely static guarantee. The client decoder re-establishes the runtime schema before using the success payload.'),
ex('Return a stable invalid-input envelope','Submit a string operand instead of a number.','status 400 with bad_request and matching request id.',r'''const reply = handle({ method: 'POST', path: '/sum', requestId: 'R2', body: { a: '2', b: 3 } });
assert.equal(reply.status, 400);
if (reply.body.ok) throw new Error('expected failure');
assert.equal(reply.body.error.code, 'bad_request');
assert.equal(reply.body.requestId, 'R2');''','The failure is represented deliberately rather than relying on JavaScript coercion. A stable category is easier for clients to branch on than free-form error prose.'),
ex('Distinguish route and method failures','Use an unknown path and an unsupported method.','404 not_found versus 405 method_not_allowed.',r'''assert.equal(handle({ method: 'POST', path: '/missing', requestId: 'R3', body: null }).status, 404);
assert.equal(handle({ method: 'GET', path: '/sum', requestId: 'R4', body: null }).status, 405);''','The handler\'s routing policy is explicit. Transport integration must preserve these distinctions rather than turning every error into 500 or 200.'),
ex('Reject version or status/body disagreement','Decode an unsupported version and a success envelope paired with status 400.','TypeError for both malformed replies.',r'''const valid = handle({ method: 'POST', path: '/sum', requestId: 'R5', body: { a: 1, b: 1 } });
assert.throws(() => decodeReply({ ...valid, body: { ...valid.body, version: 2 } }), TypeError);
assert.throws(() => decodeReply({ ...valid, status: 400 }), TypeError);''','A client should reject a contradictory contract rather than choosing whichever part happens to be convenient. Version mismatch remains visible for migration or diagnosis.'),
ex('Require success narrowing in checked client code','Attempt data access before checking ok in an uncalled function.','expected compiler error; correctly narrowed success remains usable.',r'''function negativeTypeCheck(envelope: Envelope): void {
  // @ts-expect-error Failure envelopes do not contain data.
  void envelope.data.total;
}
void negativeTypeCheck;
assert.equal(decodeReply(handle({ method: 'POST', path: '/sum', requestId: 'R6', body: { a: 0, b: 0 } })).status, 200);''','The compiler protects internal client logic after decoding. It does not replace the decoder that establishes the envelope at runtime.'),
ex('Keep invalid payload details out of response errors','Include a secret-looking extra field in an invalid request.','bad_request response does not echo the supplied value.',r'''const reply = handle({ method: 'POST', path: '/sum', requestId: 'R7', body: { a: 1, b: 2, token: 'fixture-secret-value' } });
assert.equal(reply.status, 400);
assert.equal(JSON.stringify(reply).includes('fixture-secret-value'), false);''','An error response is another output boundary. Generic domain diagnostics can be useful without reflecting arbitrary request content into logs or clients.')],helper='''type ErrorCode = 'bad_request' | 'not_found' | 'method_not_allowed';
type Envelope = { version: 1; requestId: string; ok: true; data: { total: number } } | { version: 1; requestId: string; ok: false; error: { code: ErrorCode; message: string } };
type Reply = { status: 200 | 400 | 404 | 405; body: Envelope };
type Request = { method: string; path: string; requestId: string; body: unknown };
function record(value: unknown): value is Record<string, unknown> { return typeof value === 'object' && value !== null && !Array.isArray(value); }
function failure(status: 400 | 404 | 405, code: ErrorCode, requestId: string): Reply {
  return { status, body: { version: 1, requestId, ok: false, error: { code, message: 'Request could not be accepted' } } };
}
function handle(request: Request): Reply {
  if (request.path !== '/sum') return failure(404, 'not_found', request.requestId);
  if (request.method !== 'POST') return failure(405, 'method_not_allowed', request.requestId);
  const body = request.body;
  if (!record(body) || Object.keys(body).sort().join(',') !== 'a,b' || typeof body.a !== 'number' || typeof body.b !== 'number' || !Number.isSafeInteger(body.a) || !Number.isSafeInteger(body.b) || !Number.isSafeInteger(body.a + body.b)) return failure(400, 'bad_request', request.requestId);
  return { status: 200, body: { version: 1, requestId: request.requestId, ok: true, data: { total: body.a + body.b } } };
}
function decodeReply(value: unknown): Reply {
  if (!record(value) || !record(value.body)) throw new TypeError('reply object required');
  const body = value.body;
  if (body.version !== 1 || typeof body.requestId !== 'string' || body.requestId.length === 0) throw new TypeError('unsupported envelope');
  if (body.ok === true && value.status === 200 && record(body.data) && typeof body.data.total === 'number' && Number.isSafeInteger(body.data.total)) {
    return { status: 200, body: { version: 1, requestId: body.requestId, ok: true, data: { total: body.data.total } } };
  }
  if (body.ok === false && record(body.error) && typeof body.error.message === 'string') {
    const code = body.error.code;
    if ((value.status === 400 && code === 'bad_request') || (value.status === 404 && code === 'not_found') || (value.status === 405 && code === 'method_not_allowed')) {
      return { status: value.status, body: { version: 1, requestId: body.requestId, ok: false, error: { code, message: body.error.message } } };
    }
  }
  throw new TypeError('status and body contract mismatch');
}''',source=TS+'narrowing.html')

add(39,
'''A state machine makes allowed transitions explicit. Instead of several independent booleans such as started, failed and done, a discriminated union represents one coherent state. An event requests a transition; a pure transition function either produces the next valid state or rejects an invalid event for the current state. This prevents combinations such as simultaneously running and completed from being expressible in ordinary checked code.

A functional core computes decisions without performing I/O. An outer shell can persist the decision, send a message or render it. Keeping the transition pure makes replay and failure analysis straightforward: the same initial state and event sequence should produce the same final state. It does not make external side effects automatically exactly once. The shell still needs a durable transaction and idempotency policy if it coordinates real storage or remote work.

The fixture models a bounded job lifecycle: queued, running, succeeded, failed or cancelled. Starting increments an attempt count. A failed job may retry only while fewer than three attempts have been started. Succeeded and cancelled are terminal. Cancellation is a state transition in this pure model; it does not physically stop a worker or cancel a socket. An integration layer must connect the decision to those operational actions and report their outcomes.

Readonly types express the intended consumer view. The tests also verify that transition does not mutate the input object, because static annotations alone do not prove runtime immutability. Invalid numeric results remain a runtime domain problem even when success carries a TypeScript number.''',
'''Each state has kind plus common id and attempt fields. Events form another closed union. switch narrows the event, and state guards define where it is legal. New objects are returned with spread or explicit fields. A never guard protects event exhaustiveness. replay uses reduce to apply the same transition repeatedly. The attempt invariant is checked before retrying, not after accidentally starting a fourth attempt.''',
[('State machine','A set of coherent states and allowed transitions between them.'),('Event','A request to transition under the current state.'),('Functional core','Pure decision logic separated from I/O effects.'),('Replay','Recomputing state from an initial value and an event sequence.')],[
ex('Complete one valid job lifecycle','Start a queued job and complete it with value 7.','succeeded with attempt 1 and value 7.',r'''const started = transition(initial(), { type: 'start' });
const completed = transition(started, { type: 'complete', value: 7 });
assert.deepEqual(completed, { id: 'A', attempt: 1, kind: 'succeeded', value: 7 });''','The transition sequence carries the attempt count forward. Completion is accepted only after a start established the running state.'),
ex('Reject a result arriving before start','Send complete directly to queued.','invalid transition error; original remains queued.',r'''const queued = initial();
assert.throws(() => transition(queued, { type: 'complete', value: 7 }), /invalid transition/u);
assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });''','An unexpected event is visible rather than silently ignored. Ignoring it could hide ordering or duplicate-delivery defects in an outer integration.'),
ex('Enforce the retry budget','Fail three started attempts and try to retry once more.','attempt 3 remains failed; further retry rejects.',r'''let state: State = initial();
for (let attempt = 1; attempt <= 3; attempt += 1) {
  state = transition(state, { type: 'start' });
  state = transition(state, { type: 'fail', reason: 'temporary' });
  if (attempt < 3) state = transition(state, { type: 'retry' });
}
assert.equal(state.attempt, 3);
assert.throws(() => transition(state, { type: 'retry' }), /retry budget/u);''','The limit counts actual starts rather than the number of failure messages. The final failed state remains available for diagnosis after the budget is exhausted.'),
ex('Keep cancellation terminal','Cancel a running job, then deliver a late completion.','cancelled state remains; late completion rejects.',r'''const cancelled = transition(transition(initial(), { type: 'start' }), { type: 'cancel', reason: 'user request' });
assert.equal(cancelled.kind, 'cancelled');
assert.throws(() => transition(cancelled, { type: 'complete', value: 2 }), /terminal/u);''','The model prevents a late event from reviving a terminal job. A real worker still needs a cancellation channel; this pure state decision does not stop it by itself.'),
ex('Replay deterministically from the same history','Replay start, failure, retry, start and completion twice.','both runs produce the same succeeded attempt-2 state.',r'''const events: Event[] = [{ type: 'start' }, { type: 'fail', reason: 'retryable' }, { type: 'retry' }, { type: 'start' }, { type: 'complete', value: 3 }];
const first = replay(initial(), events);
const second = replay(initial(), events);
assert.deepEqual(first, second);
assert.deepEqual(first, { id: 'A', attempt: 2, kind: 'succeeded', value: 3 });''','The event history is sufficient for this deterministic decision logic. Time, randomness or I/O would need explicit inputs rather than hidden dependencies inside transition.'),
ex('Preserve input state and validate success values','Compare input before and after a transition, then reject NaN as a result.','input unchanged; new object returned; NaN rejects.',r'''const queued = initial();
const before = structuredClone(queued);
const running = transition(queued, { type: 'start' });
assert.deepEqual(queued, before);
assert.notEqual(running, queued);
assert.throws(() => transition(running, { type: 'complete', value: NaN }), RangeError);''','The test checks actual non-mutation and numeric validity. A readonly number annotation would not establish either property by itself.')],helper='''type Base = { readonly id: string; readonly attempt: number };
type State = Base & ({ readonly kind: 'queued' } | { readonly kind: 'running' } | { readonly kind: 'succeeded'; readonly value: number } | { readonly kind: 'failed'; readonly reason: string } | { readonly kind: 'cancelled'; readonly reason: string });
type Event = { type: 'start' } | { type: 'complete'; value: number } | { type: 'fail'; reason: string } | { type: 'retry' } | { type: 'cancel'; reason: string };
function initial(): State { return { id: 'A', attempt: 0, kind: 'queued' }; }
function assertNever(value: never): never { throw new Error('unknown event: ' + JSON.stringify(value)); }
function transition(state: State, event: Event): State {
  if (state.kind === 'succeeded' || state.kind === 'cancelled') throw new Error('terminal state');
  switch (event.type) {
    case 'start':
      if (state.kind !== 'queued') throw new Error('invalid transition to running');
      return { id: state.id, attempt: state.attempt + 1, kind: 'running' };
    case 'complete':
      if (state.kind !== 'running') throw new Error('invalid transition to succeeded');
      if (!Number.isFinite(event.value)) throw new RangeError('finite result required');
      return { ...state, kind: 'succeeded', value: event.value };
    case 'fail':
      if (state.kind !== 'running') throw new Error('invalid transition to failed');
      return { ...state, kind: 'failed', reason: event.reason };
    case 'retry':
      if (state.kind !== 'failed') throw new Error('invalid transition to queued');
      if (state.attempt >= 3) throw new Error('retry budget exhausted');
      return { id: state.id, attempt: state.attempt, kind: 'queued' };
    case 'cancel': return { id: state.id, attempt: state.attempt, kind: 'cancelled', reason: event.reason };
    default: return assertNever(event);
  }
}
function replay(state: State, events: readonly Event[]): State { return events.reduce(transition, state); }''',source=TS+'narrowing.html')

add(41,
'''An analytics pipeline combines framing, parsing, validation and aggregation. Each layer has a different failure mode. Bytes can split UTF-8 characters, chunks can split lines, JSON can be malformed, and syntax-valid rows can violate a domain schema. Treating every line as a trusted typed record skips several independent boundaries. A useful diagnostic identifies the physical line and category without copying sensitive raw data into logs.

This fixture accepts newline-delimited JSON rows containing a group and a bounded integer value. A StringDecoder retains incomplete UTF-8 sequences across byte chunks. A line buffer retains incomplete records. The parser validates exact fields and returns a typed record or a compact diagnostic. Aggregation stores a count and sum per group. Invalid rows are quarantined as diagnostics; their values do not contribute to accepted totals.

The quarantine policy is a deliberate choice. A financial reconciliation or release gate might instead reject the entire input on any invalid row. This example returns accepted and rejected counts so a partial aggregate cannot be confused with a complete clean dataset. It does not infer that rejected data is statistically ignorable: missingness can bias the aggregate, so the downstream interpretation must consider why rows failed.

Streaming does not automatically mean bounded memory. The fixture caps total input bytes, line bytes and record lengths, and its tiny group set is controlled by the authored input. A production pipeline with unbounded unique groups needs a cardinality limit, spill strategy or external aggregation. The code demonstrates actual incremental decoding and validation, not a claim of constant memory for arbitrary datasets.''',
'''The byte source is an AsyncIterable<Uint8Array>. StringDecoder.write handles split characters, while end flushes remaining decoder state. A pending text buffer is split at newline characters and strips an optional preceding carriage return. Each physical line receives a one-based number. JSON.parse returns unknown at the boundary, and the validator checks its shape before constructing a fresh Row. Map aggregation updates only accepted rows and returns a separate diagnostics list.''',
[('Framing','Separating a byte/text stream into logical records.'),('Quarantine','Retaining failure diagnostics while excluding invalid rows from accepted aggregates.'),('Aggregation state','The per-group statistics retained while scanning records.'),('Resource budget','An explicit bound on input, records or retained state.')],[
ex('Aggregate valid split-byte input','Decode rows for groups A and B from three-byte chunks and aggregate their values.','A count 2 sum 5; B count 1 sum 4; zero rejected.',r'''const text = [{ group: 'A', value: 2 }, { group: 'B', value: 4 }, { group: 'A', value: 3 }].map(row => JSON.stringify(row)).join('\n');
const result = await analyze(chunks(text, 3));
assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum: 4 }]]);
assert.equal(result.accepted, 3);
assert.deepEqual(result.rejected, []);''','Chunk boundaries are independent of JSON record boundaries. The pipeline carries partial decoder and line state instead of parsing each chunk as a complete row.'),
ex('Quarantine syntax and domain failures with physical line numbers','Place malformed JSON and a string-valued amount after a valid row.','one accepted row; diagnostics at lines 2 and 3 with json/schema categories.',r'''const text = '{"group":"A","value":2}\n{broken\n{"group":"A","value":"wrong"}\n';
const result = await analyze(chunks(text, 2));
assert.equal(result.accepted, 1);
assert.deepEqual(result.rejected, [{ line: 2, code: 'json' }, { line: 3, code: 'schema' }]);
assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 });''','Rejected values never enter the aggregate. The diagnostic identifies where and why the row failed without reproducing the entire source payload.'),
ex('Preserve a multi-byte group name across single-byte chunks','Use an emoji group and split every UTF-8 byte.','group name remains intact with sum 7.',r'''const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));
assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 });
assert.equal(result.rejected.length, 0);''','A raw chunk.toString call per byte would introduce replacement characters. The decoder retains incomplete sequences until enough bytes arrive.'),
ex('Handle blank lines and a final line without newline','Supply blank lines, CRLF and one final valid row.','two accepted rows; no fabricated empty records.',r'''const text = '\n{"group":"A","value":1}\r\n\n{"group":"A","value":2}';
const result = await analyze(chunks(text, 4));
assert.equal(result.accepted, 2);
assert.deepEqual(result.groups.get('A'), { count: 2, sum: 3 });
assert.deepEqual(result.rejected, []);''','Blank lines are ignored under this declared format policy, while physical line numbering still advances. The final buffered record is processed even without a trailing newline.'),
ex('Enforce input and record budgets','Reject a line exceeding 1024 bytes and an input exceeding 16384 bytes.','RangeError for each resource-limit violation.',r'''await assert.rejects(analyze(chunks('x'.repeat(1025), 10)), RangeError);
await assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError);''','A budget violation aborts the stream rather than becoming a harmless row diagnostic. Continuing could retain or process more data than the application agreed to accept.'),
ex('Expose incomplete-data counts and empty input','Analyze one invalid row and no valid rows, then analyze an empty stream.','zero accepted with one rejected versus zero accepted with zero rejected.',r'''const invalid = await analyze(chunks('{"group":"A","value":null}', 5));
const empty = await analyze(chunks('', 5));
assert.equal(invalid.accepted, 0);
assert.equal(invalid.rejected.length, 1);
assert.equal(empty.accepted, 0);
assert.equal(empty.rejected.length, 0);
assert.equal(empty.groups.size, 0);''','An empty aggregate can arise from no data or from entirely rejected data. Reporting accepted and rejected counts preserves that crucial interpretation difference.')],helper='''type Row = { group: string; value: number };
type Diagnostic = { line: number; code: 'json' | 'schema' };
function row(value: unknown): Row | undefined {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return undefined;
  if (Object.keys(value).sort().join(',') !== 'group,value' || !('group' in value) || !('value' in value)) return undefined;
  if (typeof value.group !== 'string' || value.group.length === 0 || value.group.length > 40 || typeof value.value !== 'number' || !Number.isSafeInteger(value.value) || Math.abs(value.value) > 1000) return undefined;
  return { group: value.group, value: value.value };
}
async function* chunks(text: string, size: number): AsyncGenerator<Uint8Array> {
  const bytes = Buffer.from(text, 'utf8');
  for (let index = 0; index < bytes.length; index += size) yield bytes.subarray(index, index + size);
}
async function* lines(source: AsyncIterable<Uint8Array>): AsyncGenerator<{ line: number; text: string }> {
  const decoder = new StringDecoder('utf8');
  let pending = '';
  let total = 0;
  let line = 0;
  for await (const chunk of source) {
    total += chunk.byteLength;
    if (total > 16384) throw new RangeError('input byte budget exceeded');
    pending += decoder.write(Buffer.from(chunk));
    let boundary: number;
    while ((boundary = pending.indexOf('\\n')) >= 0) {
      const text = pending.slice(0, boundary).replace(/\\r$/u, '');
      pending = pending.slice(boundary + 1);
      if (Buffer.byteLength(text) > 1024) throw new RangeError('line byte budget exceeded');
      yield { line: ++line, text };
    }
    if (Buffer.byteLength(pending) > 1024) throw new RangeError('line byte budget exceeded');
  }
  pending += decoder.end();
  if (pending !== '') yield { line: ++line, text: pending.replace(/\\r$/u, '') };
}
async function analyze(source: AsyncIterable<Uint8Array>): Promise<{ groups: Map<string, { count: number; sum: number }>; accepted: number; rejected: Diagnostic[] }> {
  const groups = new Map<string, { count: number; sum: number }>();
  const rejected: Diagnostic[] = [];
  let accepted = 0;
  for await (const entry of lines(source)) {
    if (entry.text.trim() === '') continue;
    let value: unknown;
    try { value = JSON.parse(entry.text); }
    catch { rejected.push({ line: entry.line, code: 'json' }); continue; }
    const parsed = row(value);
    if (!parsed) { rejected.push({ line: entry.line, code: 'schema' }); continue; }
    const previous = groups.get(parsed.group) ?? { count: 0, sum: 0 };
    groups.set(parsed.group, { count: previous.count + 1, sum: previous.sum + parsed.value });
    accepted += 1;
  }
  return { groups, accepted, rejected };
}''',imports='''import { strict as assert } from 'node:assert';
import { StringDecoder } from 'node:string_decoder';''',source=NODE+'string_decoder.html')

add(40,
'''A local service combines transport handling with domain state and resource ownership. The HTTP handler should parse and validate a request before changing state, return a documented status, and finish every response. The domain operation here stores a small item with a unique id and bounded integer value. Duplicate creation returns a conflict without replacing the original item. This in-memory repository is lost when the process stops; it is not a database or a durable transaction system.

The fixture creates an actual HTTP server on an ephemeral 127.0.0.1 port and sends real fetch requests. Each exercise gets a fresh repository and server, preventing one scenario from making another pass through leftover state. The accepted body is JSON with an exact schema. A byte limit bounds retained request data, and unexpected media types or unsupported methods receive distinct errors. Client timeouts bound waiting, while finally closes active connections and the owned listener.

Observability records the operation\'s outcome without copying the full request. A generated request id is returned in a header and appears in a small event record with a normalized route and status. Unknown routes are logged as unknown rather than preserving arbitrary path text. This makes the evidence useful for correlating a request and its result while avoiding a second uncontrolled payload store in logs.

The service is an offline teaching fixture with no authentication, TLS, durable storage or public deployment claim. Loopback binding reduces exposure but does not establish a security sandbox. A production service would need those operational boundaries in addition to the contract and cleanup mechanisms demonstrated here. The reference\'s actual socket exchanges establish more than a pure handler unit test, but still only for the bounded local scenarios.''',
'''createServer delegates to an async dispatcher and captures unexpected rejections. Request bodies are read incrementally; only bytes within the configured cap are retained. JSON parsing and exact-field checks occur before Map insertion. Responses set application/json and an x-request-id header. The context tracks metrics after choosing a status. withService closes connections and awaits server.close in finally, even when a client assertion fails.''',
[('Transport integration','Testing actual request and response exchange through sockets.'),('Repository lifetime','The persistence scope of the state backing domain operations.'),('Conflict','A request that would violate an existing-state invariant.'),('Structured event','A bounded diagnostic record with named, intentionally selected fields.')],[
ex('Create and retrieve an item over real HTTP','POST item A with value 2, then GET the list.','201 created; subsequent 200 list contains exactly A.',r'''await withService(async context => {
  const created = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) });
  assert.equal(created.status, 201);
  assert.deepEqual(await created.json(), { id: 'A', value: 2 });
  const listed = await request(context, '/items');
  assert.equal(listed.status, 200);
  assert.deepEqual(await listed.json(), [{ id: 'A', value: 2 }]);
});''','The assertions cross the real transport boundary. A typed or pure handler result alone would not check serialization, headers, routing or socket cleanup.'),
ex('Reject malformed data before changing state','Send malformed JSON and a wrong-shaped object, then inspect the repository through GET.','both 400; list remains empty.',r'''await withService(async context => {
  for (const body of ['{broken', JSON.stringify({ id: 'A', value: 'wrong' })]) {
    const response = await request(context, '/items', { method: 'POST', body });
    assert.equal(response.status, 400);
    await response.text();
  }
  assert.deepEqual(await (await request(context, '/items')).json(), []);
});''','The failure is atomic relative to the in-memory mutation. No partial record is inserted before validation finishes.'),
ex('Preserve original state on duplicate creation','Create A with value 2, then try A with value 9.','second request 409; stored value remains 2.',r'''await withService(async context => {
  await (await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) })).text();
  const duplicate = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 9 }) });
  assert.equal(duplicate.status, 409);
  assert.deepEqual(await duplicate.json(), { error: 'duplicate_id' });
  assert.deepEqual(await (await request(context, '/items')).json(), [{ id: 'A', value: 2 }]);
});''','A duplicate business identifier is not an instruction to overwrite. The explicit conflict status preserves both the domain invariant and a diagnosable client outcome.'),
ex('Enforce body and media-type contracts','Send 513 body bytes, then a text/plain payload.','413 for size and 415 for media type.',r'''await withService(async context => {
  const large = await request(context, '/items', { method: 'POST', body: 'x'.repeat(513) });
  assert.equal(large.status, 413); await large.text();
  const wrongType = await request(context, '/items', { method: 'POST', body: '{}', headers: { 'content-type': 'text/plain' } });
  assert.equal(wrongType.status, 415); await wrongType.text();
});''','Representation size and representation format are separate boundaries. A JSON parser should not be used as a substitute for either policy.'),
ex('Distinguish unknown routes and unsupported methods','Request an absent path and DELETE on the item route.','404 and 405 respectively.',r'''await withService(async context => {
  const missing = await request(context, '/missing');
  assert.equal(missing.status, 404); await missing.text();
  const wrongMethod = await request(context, '/items', { method: 'DELETE' });
  assert.equal(wrongMethod.status, 405); await wrongMethod.text();
});''','A method is part of endpoint semantics. Returning one generic status would remove information needed by a client or operator to diagnose the request.'),
ex('Correlate safe events and prove listener cleanup','Request health, inspect its request id and event keys, then check the server after the helper exits.','matching id and status; server no longer listening.',r'''let owned;
await withService(async context => {
  owned = context.server;
  const response = await request(context, '/health');
  const id = response.headers.get('x-request-id');
  assert.deepEqual(await response.json(), { status: 'ready' });
  assert.equal(context.events[0].requestId, id);
  assert.deepEqual(Object.keys(context.events[0]).sort(), ['method', 'requestId', 'route', 'status']);
  assert.equal(context.events[0].status, 200);
});
assert.equal(owned.listening, false);''','The event records only selected metadata. Cleanup is observed after the helper completes, rather than inferred from the presence of a finally block.')],helper='''async function readBody(request) {
  const chunks = [];
  let bytes = 0;
  for await (const chunk of request) {
    bytes += chunk.length;
    if (bytes <= 512) chunks.push(chunk);
  }
  if (bytes > 512) throw Object.assign(new Error('body too large'), { status: 413 });
  return Buffer.concat(chunks).toString('utf8');
}
async function withService(use) {
  const items = new Map();
  const events = [];
  let sequence = 0;
  const server = createServer((incoming, response) => {
    const requestId = `R${++sequence}`;
    const path = new URL(incoming.url, 'http://127.0.0.1').pathname;
    const route = ['/items', '/health'].includes(path) ? path : 'unknown';
    function send(status, body) {
      events.push({ requestId, method: incoming.method, route, status });
      response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'x-request-id': requestId });
      response.end(JSON.stringify(body));
    }
    async function dispatch() {
      if (route === 'unknown') { incoming.resume(); send(404, { error: 'not_found' }); return; }
      if (path === '/health' && incoming.method === 'GET') { send(200, { status: 'ready' }); return; }
      if (path === '/items' && incoming.method === 'GET') { send(200, [...items.values()].sort((a, b) => a.id.localeCompare(b.id))); return; }
      if (path !== '/items' || incoming.method !== 'POST') { incoming.resume(); send(405, { error: 'method_not_allowed' }); return; }
      if (incoming.headers['content-type']?.split(';')[0] !== 'application/json') { incoming.resume(); send(415, { error: 'json_required' }); return; }
      let value;
      try { value = JSON.parse(await readBody(incoming)); }
      catch (error) { send(error.status === 413 ? 413 : 400, { error: error.status === 413 ? 'body_too_large' : 'invalid_json' }); return; }
      if (value === null || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join(',') !== 'id,value' || typeof value.id !== 'string' || !/^[A-Z]{1,8}$/u.test(value.id) || !Number.isSafeInteger(value.value) || Math.abs(value.value) > 1000) { send(400, { error: 'invalid_item' }); return; }
      if (items.has(value.id)) { send(409, { error: 'duplicate_id' }); return; }
      const accepted = { id: value.id, value: value.value };
      items.set(value.id, accepted);
      send(201, accepted);
    }
    dispatch().catch(() => { if (!response.headersSent) send(500, { error: 'internal_error' }); else response.destroy(); });
  });
  server.requestTimeout = 3000;
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  try {
    const address = server.address();
    if (address === null || typeof address === 'string') throw new Error('TCP address required');
    return await use({ base: `http://127.0.0.1:${address.port}`, server, events });
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}
function request(context, path, options = {}) {
  return fetch(new URL(path, context.base), { ...options, headers: { 'content-type': 'application/json', ...options.headers }, signal: AbortSignal.timeout(2000) });
}''',imports='''import { strict as assert } from 'node:assert';
import { createServer } from 'node:http';''',source=NODE+'http.html')

add(42,
'''A release is a specific artifact with a reproducible behavior contract, not merely a folder that once worked during development. A small release manifest can name the exact files, record their digests and declare a schema version. Verification should reject unexpected paths before reading files, compare expected byte identities and then execute a bounded smoke test in a fresh process. These checks answer different questions: identity, admissible layout and behavior.

The fixture builds a tiny command-line bundle in an owned temporary directory. Its application has a self-test command and a generic usage failure. The manifest names only app.mjs and package.json, so an altered manifest cannot make the verifier read an arbitrary path. The app\'s self-test checks real arithmetic behavior and reports the actual Node version. A compatibility gate accepts an explicitly supplied required major version; the course\'s prepared execution profile remains Node 24. Production policy may pin a full version and image digest rather than only a major.

Observability is part of the output contract. The application emits one result object to stdout and a small completion or failure event to stderr. It does not echo arbitrary command-line values in its error. The caller preserves those channels separately and includes them when a smoke test fails. A successful self-test proves only its covered cases, so the manifest and receipt must not be advertised as production acceptance or exhaustive compatibility.

Maintenance means keeping source, docs, tests, packaged bytes and runtime assumptions aligned. A source edit invalidates a digest and should trigger new execution evidence. Rollback requires retaining a known artifact and its compatible state assumptions; renaming a version label is not a rollback procedure. This lesson performs local packaging and smoke checks only. It does not publish a registry package, deploy a service or change learner state.''',
'''The manifest uses an explicit filename allowlist and SHA-256 digests. Paths are rejected before joining them to the bundle directory. The hash list excludes the manifest itself to avoid a self-reference. spawnSync runs the current Node executable with a fixed source path and argument list, bounded timeout and output size. stdout and stderr remain separate. Runtime qualification compares a reported actual major version with a caller-supplied policy rather than trusting package metadata alone.''',
[('Release artifact','The exact files intended to be distributed or executed.'),('Smoke test','A small fresh-process check of essential behavior.'),('Artifact verification','Checking allowed layout and expected byte identities.'),('Compatibility gate','An explicit rule comparing observed runtime evidence with release requirements.')],[
ex('Build, verify and execute a fresh bundle','Create the authored bundle, verify hashes and run its self-test in a child.','three checks passed; actual Node version reported.',r'''await withBundle(async directory => {
  await verifyBundle(directory);
  const result = runBundle(directory, ['--self-test']);
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.equal(receipt.checks, 3);
  assert.equal(receipt.status, 'passed');
  assert.equal(receipt.node, process.versions.node);
});''','The child executes the packaged bytes rather than an already imported development function. The receipt records the runtime that actually ran.'),
ex('Reject altered application bytes before execution','Append a harmless comment to the owned application after manifest creation.','digest verification fails.',r'''await withBundle(async directory => {
  await appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');
  await assert.rejects(verifyBundle(directory), /digest mismatch/u);
});''','Even a behavior-preserving edit changes artifact identity. The correct repair is to create a new reviewed manifest and rerun evidence, not ignore the mismatch.'),
ex('Reject a manifest path outside the allowlist','Replace one file entry with ../outside.txt.','path is rejected before any outside file is read.',r'''await withBundle(async directory => {
  const path = join(directory, 'manifest.json');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  manifest.files[0].path = '../outside.txt';
  await writeFile(path, JSON.stringify(manifest));
  await assert.rejects(verifyBundle(directory), /unapproved artifact path/u);
});''','A digest verifier should not treat a manifest as permission to traverse arbitrary files. The supported artifact surface is defined independently of the untrusted filename entry.'),
ex('Preserve result and diagnostic channels on failure','Invoke an unsupported argument containing a fake secret-like value.','nonzero child exit; stdout empty; generic stderr without the value.',r'''await withBundle(async directory => {
  const result = runBundle(directory, ['--fixture-secret-value']);
  assert.notEqual(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr.includes('fixture-secret-value'), false);
  const diagnostic = JSON.parse(result.stderr.trim());
  assert.equal(diagnostic.event, 'usage_error');
});''','The application reports a useful failure category without reflecting arbitrary arguments. A caller can preserve structured diagnostics without parsing a success-shaped stdout value.'),
ex('Derive stable content identity from unchanged files','Read and hash the same app twice and compare with its manifest entry.','equal digests and an unchanged manifest match.',r'''await withBundle(async directory => {
  const bytes = await readFile(join(directory, 'app.mjs'));
  const first = hash(bytes);
  const second = hash(await readFile(join(directory, 'app.mjs')));
  assert.equal(first, second);
  const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
  assert.equal(manifest.files.find(file => file.path === 'app.mjs').sha256, first);
});''','The digest is a deterministic function of file bytes. This claim does not imply that independent build systems would emit the same bytes without controlling their own inputs.'),
ex('Gate an observed runtime against explicit policy','Accept the current runtime major for the fixture and reject a different required major.','matching policy passes; mismatched policy throws.',r'''await withBundle(async directory => {
  const receipt = JSON.parse(runBundle(directory, ['--self-test']).stdout);
  const actual = Number(process.versions.node.split('.')[0]);
  assert.equal(qualifyRuntime(receipt, actual), true);
  assert.throws(() => qualifyRuntime(receipt, actual + 1), /runtime mismatch/u);
});''','The example tests the gate\'s mechanism with an observed value. The actual course policy is supplied by the prepared Node24 profile; accepting a development host in this fixture does not qualify it as that profile.')],helper=r'''const APP = String.raw`import { strict as assert } from 'node:assert';
const args = process.argv.slice(2);
if (args.length !== 1 || args[0] !== '--self-test') {
  process.stderr.write(JSON.stringify({ event: 'usage_error', message: 'Use --self-test' }) + '\n');
  process.exitCode = 2;
} else {
  assert.equal(2 + 3, 5);
  assert.equal([].reduce((sum, value) => sum + value, 0), 0);
  assert.equal(Number.isSafeInteger(Number.MAX_SAFE_INTEGER + 1), false);
  process.stdout.write(JSON.stringify({ status: 'passed', checks: 3, node: process.versions.node }) + '\n');
  process.stderr.write(JSON.stringify({ event: 'self_test_complete', checks: 3 }) + '\n');
}
`;
function hash(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
async function withBundle(use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-release-'));
  try {
    await writeFile(join(directory, 'app.mjs'), APP);
    await writeFile(join(directory, 'package.json'), JSON.stringify({ name: 'course-release', version: '1.0.0', type: 'module', private: true }));
    const files = [];
    for (const path of ['app.mjs', 'package.json']) files.push({ path, sha256: hash(await readFile(join(directory, path))) });
    await writeFile(join(directory, 'manifest.json'), JSON.stringify({ version: 1, files }));
    return await use(directory);
  } finally { await rm(directory, { recursive: true, force: true }); }
}
async function verifyBundle(directory) {
  const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
  if (manifest.version !== 1 || !Array.isArray(manifest.files) || manifest.files.length !== 2) throw new Error('invalid manifest');
  const allowed = new Set(['app.mjs', 'package.json']);
  const seen = new Set();
  for (const file of manifest.files) {
    if (!allowed.has(file.path) || seen.has(file.path)) throw new Error('unapproved artifact path');
    seen.add(file.path);
    if (hash(await readFile(join(directory, file.path))) !== file.sha256) throw new Error('digest mismatch');
  }
}
function runBundle(directory, args) {
  const result = spawnSync(process.execPath, [join(directory, 'app.mjs'), ...args], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return result;
}
function qualifyRuntime(receipt, requiredMajor) {
  if (receipt.status !== 'passed' || Number(receipt.node.split('.')[0]) !== requiredMajor) throw new Error('runtime mismatch');
  return true;
}''',imports='''import { strict as assert } from 'node:assert';
import { mkdtemp, writeFile, readFile, appendFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';''',source=NODE+'child_process.html')
