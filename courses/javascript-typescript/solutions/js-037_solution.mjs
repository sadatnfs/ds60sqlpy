import { strict as assert } from 'node:assert';
import { setTimeout as delay } from 'node:timers/promises';

async function retry(operation, { attempts = 3, base = 100, cap = 1000, random = Math.random, wait = (milliseconds, signal) => delay(milliseconds, undefined, { signal }), signal = new AbortController().signal } = {}) {
  if (!Number.isInteger(attempts) || attempts < 1 || attempts > 5) throw new RangeError('attempts from 1 to 5 required');
  if (!Number.isFinite(base) || !Number.isFinite(cap) || base < 0 || cap < 0 || cap > 10000) throw new RangeError('finite nonnegative backoff with cap at most 10000 required');
  for (let index = 0; index < attempts; index += 1) {
    signal.throwIfAborted();
    try { return await operation(signal); }
    catch (error) {
      if (!error || error.transient !== true || index + 1 === attempts) throw error;
      signal.throwIfAborted();
      const sample = random();
      if (!(sample >= 0 && sample < 1)) throw new RangeError('random sample must be in [0,1)');
      await wait(Math.floor(Math.min(cap, base * 2 ** index) * sample), signal);
    }
  }
  throw new Error('unreachable retry state');
}
class IdempotentStore {
  records = new Map();
  effects = 0;
  apply(key, payload) {
    if (typeof key !== 'string' || !key || !Number.isSafeInteger(payload.amount) || payload.amount <= 0) throw new TypeError('valid key and amount required');
    const canonical = JSON.stringify({ amount: payload.amount });
    const previous = this.records.get(key);
    if (previous) {
      if (previous.canonical !== canonical) throw new Error('idempotency key conflict');
      return { ...previous.result };
    }
    this.effects += 1;
    const result = { sequence: this.effects, amount: payload.amount };
    this.records.set(key, { canonical, result });
    return { ...result };
  }
}
async function mapBounded(values, limit, operation) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 8) throw new RangeError('limit from 1 to 8 required');
  const results = new Array(values.length);
  let next = 0;
  let failed = false;
  let failure;
  async function worker() {
    while (!failed && next < values.length) {
      const index = next++;
      try { results[index] = await operation(values[index], index); }
      catch (error) { if (!failed) { failed = true; failure = error; } }
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, values.length) }, worker));
  if (failed) throw failure;
  return results;
}

export async function verify() {
  // Exercise 1: Retry transient failures with deterministic full jitter
  {
    let attempts = 0;
    const waits = [];
    const result = await retry(async () => { attempts += 1; if (attempts < 3) throw Object.assign(new Error('temporary'), { transient: true }); return 'ready'; }, { wait: async value => { waits.push(value); }, random: () => 0.5 });
    assert.equal(result, 'ready');
    assert.equal(attempts, 3);
    assert.deepEqual(waits, [50, 100]);
  }

  // Exercise 2: Stop on permanent failure and on exhausted attempts
  {
    let permanent = 0;
    await assert.rejects(retry(async () => { permanent += 1; throw new Error('permanent'); }), /permanent/u);
    assert.equal(permanent, 1);
    let transient = 0;
    await assert.rejects(retry(async () => { transient += 1; throw Object.assign(new Error('still unavailable'), { transient: true }); }, { wait: async () => {} }), /still unavailable/u);
    assert.equal(transient, 3);
  }

  // Exercise 3: Reuse a completed idempotent result
  {
    const store = new IdempotentStore();
    const first = store.apply('request-A', { amount: 5 });
    const second = store.apply('request-A', { amount: 5 });
    assert.deepEqual(second, first);
    assert.equal(store.effects, 1);
  }

  // Exercise 4: Reject conflicting reuse of an idempotency key
  {
    const store = new IdempotentStore();
    store.apply('request-A', { amount: 5 });
    assert.throws(() => store.apply('request-A', { amount: 7 }), /key conflict/u);
    assert.equal(store.effects, 1);
  }

  // Exercise 5: Bound active work while preserving input order
  {
    let active = 0;
    let peak = 0;
    const result = await mapBounded([1, 2, 3, 4], 2, async value => {
      active += 1; peak = Math.max(peak, active);
      try { await delay(1); return value * 2; }
      finally { active -= 1; }
    });
    assert.deepEqual(result, [2, 4, 6, 8]);
    assert.ok(peak <= 2 && peak > 0);
    assert.equal(active, 0);
    const started = [];
    await assert.rejects(mapBounded([1, 2, 3, 4], 2, async value => {
      started.push(value); active += 1;
      try { if (value === 2) throw new Error('controlled failure'); await delay(1); return value; }
      finally { active -= 1; }
    }), /controlled failure/u);
    assert.deepEqual(started, [1, 2]);
    assert.equal(active, 0);
    assert.deepEqual(await mapBounded([], 2, async value => value), []);
  }

  // Exercise 6: Honor cancellation before the first attempt
  {
    const controller = new AbortController();
    const reason = new Error('cancelled before start');
    controller.abort(reason);
    let attempts = 0;
    await assert.rejects(retry(async () => { attempts += 1; return 1; }, { signal: controller.signal }), error => error === reason);
    assert.equal(attempts, 0);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
