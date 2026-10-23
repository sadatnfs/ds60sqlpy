import { strict as assert } from 'node:assert';

type ErrorCode = 'bad_request' | 'not_found' | 'method_not_allowed';
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
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Handle and decode a successful request
  {
    const reply = handle({ method: 'POST', path: '/sum', requestId: 'R1', body: { a: 2, b: 3 } });
    const decoded = decodeReply(JSON.parse(JSON.stringify(reply)));
    assert.equal(decoded.status, 200);
    if (!decoded.body.ok) throw new Error(decoded.body.error.message);
    assert.equal(decoded.body.data.total, 5);
  }

  // Exercise 2: Return a stable invalid-input envelope
  {
    const reply = handle({ method: 'POST', path: '/sum', requestId: 'R2', body: { a: '2', b: 3 } });
    assert.equal(reply.status, 400);
    if (reply.body.ok) throw new Error('expected failure');
    assert.equal(reply.body.error.code, 'bad_request');
    assert.equal(reply.body.requestId, 'R2');
  }

  // Exercise 3: Distinguish route and method failures
  {
    assert.equal(handle({ method: 'POST', path: '/missing', requestId: 'R3', body: null }).status, 404);
    assert.equal(handle({ method: 'GET', path: '/sum', requestId: 'R4', body: null }).status, 405);
  }

  // Exercise 4: Reject version or status/body disagreement
  {
    const valid = handle({ method: 'POST', path: '/sum', requestId: 'R5', body: { a: 1, b: 1 } });
    assert.throws(() => decodeReply({ ...valid, body: { ...valid.body, version: 2 } }), TypeError);
    assert.throws(() => decodeReply({ ...valid, status: 400 }), TypeError);
  }

  // Exercise 5: Require success narrowing in checked client code
  {
    function negativeTypeCheck(envelope: Envelope): void {
      // @ts-expect-error Failure envelopes do not contain data.
      void envelope.data.total;
    }
    void negativeTypeCheck;
    assert.equal(decodeReply(handle({ method: 'POST', path: '/sum', requestId: 'R6', body: { a: 0, b: 0 } })).status, 200);
  }

  // Exercise 6: Keep invalid payload details out of response errors
  {
    const reply = handle({ method: 'POST', path: '/sum', requestId: 'R7', body: { a: 1, b: 2, token: 'fixture-secret-value' } });
    assert.equal(reply.status, 400);
    assert.equal(JSON.stringify(reply).includes('fixture-secret-value'), false);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
