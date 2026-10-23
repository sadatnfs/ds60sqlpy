import { strict as assert } from 'node:assert';
import { createServer } from 'node:http';

async function readBody(request) {
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
}

export async function verify() {
  // Exercise 1: Create and retrieve an item over real HTTP
  {
    await withService(async context => {
      const created = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) });
      assert.equal(created.status, 201);
      assert.deepEqual(await created.json(), { id: 'A', value: 2 });
      const listed = await request(context, '/items');
      assert.equal(listed.status, 200);
      assert.deepEqual(await listed.json(), [{ id: 'A', value: 2 }]);
    });
  }

  // Exercise 2: Reject malformed data before changing state
  {
    await withService(async context => {
      for (const body of ['{broken', JSON.stringify({ id: 'A', value: 'wrong' })]) {
        const response = await request(context, '/items', { method: 'POST', body });
        assert.equal(response.status, 400);
        await response.text();
      }
      assert.deepEqual(await (await request(context, '/items')).json(), []);
    });
  }

  // Exercise 3: Preserve original state on duplicate creation
  {
    await withService(async context => {
      await (await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 2 }) })).text();
      const duplicate = await request(context, '/items', { method: 'POST', body: JSON.stringify({ id: 'A', value: 9 }) });
      assert.equal(duplicate.status, 409);
      assert.deepEqual(await duplicate.json(), { error: 'duplicate_id' });
      assert.deepEqual(await (await request(context, '/items')).json(), [{ id: 'A', value: 2 }]);
    });
  }

  // Exercise 4: Enforce body and media-type contracts
  {
    await withService(async context => {
      const large = await request(context, '/items', { method: 'POST', body: 'x'.repeat(513) });
      assert.equal(large.status, 413); await large.text();
      const wrongType = await request(context, '/items', { method: 'POST', body: '{}', headers: { 'content-type': 'text/plain' } });
      assert.equal(wrongType.status, 415); await wrongType.text();
    });
  }

  // Exercise 5: Distinguish unknown routes and unsupported methods
  {
    await withService(async context => {
      const missing = await request(context, '/missing');
      assert.equal(missing.status, 404); await missing.text();
      const wrongMethod = await request(context, '/items', { method: 'DELETE' });
      assert.equal(wrongMethod.status, 405); await wrongMethod.text();
    });
  }

  // Exercise 6: Correlate safe events and prove listener cleanup
  {
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
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
