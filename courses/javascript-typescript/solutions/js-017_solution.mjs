import { strict as assert } from 'node:assert';
import { createServer } from 'node:http';

function sendJson(response, status, body, extra = {}) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', ...extra });
  response.end(JSON.stringify(body));
}
function integerParameter(parameters, name) {
  const values = parameters.getAll(name);
  if (values.length !== 1 || !/^-?(0|[1-9][0-9]*)$/u.test(values[0])) return undefined;
  const value = Number(values[0]);
  return Number.isSafeInteger(value) ? value : undefined;
}
function handle(request, response) {
  const url = new URL(request.url, 'http://127.0.0.1');
  if (url.pathname !== '/sum') { sendJson(response, 404, { error: 'not_found' }); return; }
  if (request.method !== 'GET') { sendJson(response, 405, { error: 'method_not_allowed' }, { allow: 'GET' }); return; }
  const a = integerParameter(url.searchParams, 'a');
  const b = integerParameter(url.searchParams, 'b');
  if (a === undefined || b === undefined || [...url.searchParams.keys()].some(key => !['a', 'b'].includes(key))) {
    sendJson(response, 400, { error: 'invalid_parameters' }); return;
  }
  const total = a + b;
  if (!Number.isSafeInteger(total)) { sendJson(response, 400, { error: 'unsafe_total' }); return; }
  sendJson(response, 200, { total });
}
async function withServer(use) {
  const server = createServer(handle);
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  try {
    const address = server.address();
    if (address === null || typeof address === 'string') throw new Error('expected TCP listener');
    return await use(`http://127.0.0.1:${address.port}`);
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}

export async function verify() {
  // Exercise 1: Request a valid local calculation
  {
    await withServer(async base => {
      const response = await fetch(new URL('/sum?a=2&b=3', base), { signal: AbortSignal.timeout(2000) });
      assert.equal(response.status, 200);
      assert.match(response.headers.get('content-type'), /application\/json/u);
      assert.deepEqual(await response.json(), { total: 5 });
    });
  }

  // Exercise 2: Inspect an HTTP error without expecting fetch rejection
  {
    await withServer(async base => {
      const response = await fetch(new URL('/missing', base), { signal: AbortSignal.timeout(2000) });
      assert.equal(response.status, 404);
      assert.equal(response.ok, false);
      assert.deepEqual(await response.json(), { error: 'not_found' });
    });
  }

  // Exercise 3: Encode query values through the URL API
  {
    const url = new URL('http://127.0.0.1/search');
    url.searchParams.set('q', 'a & b=c');
    assert.equal(url.searchParams.get('q'), 'a & b=c');
    assert.equal([...url.searchParams].length, 1);
    assert.ok(url.href.includes('%26'));
  }

  // Exercise 4: Reject repeated or invalid parameters
  {
    await withServer(async base => {
      for (const path of ['/sum?a=1&a=2&b=3', '/sum?a=1&b=hello']) {
        const response = await fetch(new URL(path, base), { signal: AbortSignal.timeout(2000) });
        assert.equal(response.status, 400);
        assert.deepEqual(await response.json(), { error: 'invalid_parameters' });
      }
    });
  }

  // Exercise 5: Reject an unsupported method
  {
    await withServer(async base => {
      const response = await fetch(new URL('/sum?a=1&b=2', base), { method: 'POST', signal: AbortSignal.timeout(2000) });
      assert.equal(response.status, 405);
      assert.equal(response.headers.get('allow'), 'GET');
      assert.deepEqual(await response.json(), { error: 'method_not_allowed' });
    });
  }

  // Exercise 6: Guard arithmetic overflow after parsing
  {
    await withServer(async base => {
      const url = new URL('/sum', base);
      url.searchParams.set('a', String(Number.MAX_SAFE_INTEGER));
      url.searchParams.set('b', '1');
      const response = await fetch(url, { signal: AbortSignal.timeout(2000) });
      assert.equal(response.status, 400);
      assert.deepEqual(await response.json(), { error: 'unsafe_total' });
    });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
