# js-037: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A retry is a new attempt after an uncertain or failed operation. It can improve resilience to transient failures, but it also multiplies load and may repeat side effects. Retrying every exception hides programming errors and permanent rejections. An operation needs a retry classification, maximum attempts, delay policy, cancellation behavior and a final failure result. A deadline limits waiting; it does not prove that a remote write did not occur.

Exponential backoff grows the delay between attempts. Full jitter chooses a delay uniformly from zero to a capped exponential bound, spreading clients that would otherwise retry simultaneously. The examples inject the random source and waiting function so expected delays are deterministic. They test a retry policy around a controlled transport fixture, not a real network outage or production recovery claim.

Idempotency associates repeated attempts with one intended operation. A key alone is insufficient if a caller reuses it with different request data. The fixture stores a canonical request representation and its completed result; matching retries reuse that result, while conflicting reuse rejects. Its Map is only in-memory and single-process. It does not survive crashes or solve distributed coordination; a durable service needs a transactionally enforced key/payload/result policy.

Bounded concurrency limits simultaneous owned work. Promise.all over a huge input starts all mapped operations immediately unless scheduling is controlled. The provided worker-loop scheduler starts at most the configured limit and preserves result order. On failure it stops scheduling new work, awaits already started work, then rejects. That is cleanup discipline, not cancellation of external side effects already underway.

**Retry classification:** The policy selecting failures eligible for another attempt.

**Backoff with jitter:** A growing delay bound with randomized spacing inside it.

**Idempotency key:** An identifier linking retries to one intended operation and payload.

**Bounded concurrency:** A limit on simultaneously active owned operations.

## Reading the implementation

retry receives an operation, an injected wait, an injected random function and an AbortSignal. It checks cancellation before each attempt, retries only the explicit transient category and throws the final error on exhaustion. The delay bound is min(cap, base times 2 to the attempt index), and jitter scales it by a sample in [0,1). The bounded map shares a synchronous next-index counter across async workers; each takes an index before awaiting its operation, so no two workers claim the same item.

## Exercise 1: Retry transient failures with deterministic full jitter: change one input

Task: In a scratch copy of Example A, change `let attempts = 0;` to `let attempts = 1;`. Which check fails, and what value does it see?

The injected wait records policy without sleeping. The result demonstrates classification and arithmetic, not elapsed network latency or a live outage recovery.

The unchanged code is the exercise block of Example A:

```javascript
let attempts = 0;
const waits = [];
const result = await retry(
  async () => {
    attempts += 1;
    if (attempts < 3) throw Object.assign(new Error('temporary'), { transient: true });
    return 'ready';
  },
  {
    wait: async (value) => {
      waits.push(value);
    },
    random: () => 0.5,
  },
);
assert.equal(result, 'ready');
assert.equal(attempts, 3);
assert.deepEqual(waits, [50, 100]);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual(waits, [50, 100])`. Restoring `let attempts = 0;` brings back: three attempts; delays 50 and 100; result ready.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `let attempts = 0;`.

## Exercise 2: Stop on permanent failure and on exhausted attempts: diagnose an edited check

Task: Example B's check was edited to read `async () => { transient -= 1`. Run it, explain the failure and restore the original.

A retry policy must retain a bounded final failure. Converting exhaustion into a default success would erase the operation's actual outcome.

The unchanged code is the exercise block of Example B:

```javascript
let permanent = 0;
await assert.rejects(
  retry(async () => {
    permanent += 1;
    throw new Error('permanent');
  }),
  /permanent/u,
);
assert.equal(permanent, 1);
let transient = 0;
await assert.rejects(
  retry(
    async () => {
      transient += 1;
      throw Object.assign(new Error('still unavailable'), { transient: true });
    },
    { wait: async () => {} },
  ),
  /still unavailable/u,
);
assert.equal(transient, 3);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `async () => { transient -= 1`. Restoring `async () => { transient += 1` brings back: permanent attempted once; transient attempted three times and still rejects.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Reuse a completed idempotent result

Task: Submit the same key and payload twice to the local store.

A matching retry reads the stored result rather than repeating the side effect. The example is intentionally limited to completed operations in one process.

```javascript
const store = new IdempotentStore();
const first = store.apply('request-A', { amount: 5 });
const second = store.apply('request-A', { amount: 5 });
assert.deepEqual(second, first);
assert.equal(store.effects, 1);
```

**Expected:** one side effect; identical returned receipt.

**Verify:** Keep `assert.deepEqual(second, first)`. Control: changing `const first = store.apply('request-A', { amount: 5 });` to `const first = store.apply('request-A!', { amount: 5 });` must make that check fail; then restore it.

## Exercise 4: Reject conflicting reuse of an idempotency key

Task: Reuse one key for amounts 5 and 7.

A key must identify an operation payload, not grant permission to replace its meaning. Accepting a changed payload could return an unrelated earlier result.

```javascript
const store = new IdempotentStore();
store.apply('request-A', { amount: 5 });
assert.throws(() => store.apply('request-A', { amount: 7 }), /key conflict/u);
assert.equal(store.effects, 1);
```

**Expected:** conflict error; effects remains 1.

**Verify:** Keep `assert.throws(() => store.apply('request-A', { amount: 7 }), /key conflict/u)`. Control: changing `store.apply('request-A', { amount: 5 });` to `store.apply('request-A!', { amount: 5 });` must make that check fail; then restore it.

## Exercise 5: Bound active work while preserving input order

Task: Map four values with concurrency 2 and observe active-operation counts.

The scheduler limits started operations, not merely the size of a Promise result array. Returning results by original index makes completion order independent of output order.

```javascript
let active = 0;
let peak = 0;
const result = await mapBounded([1, 2, 3, 4], 2, async (value) => {
  active += 1;
  peak = Math.max(peak, active);
  try {
    await delay(1);
    return value * 2;
  } finally {
    active -= 1;
  }
});
assert.deepEqual(result, [2, 4, 6, 8]);
assert.ok(peak <= 2 && peak > 0);
assert.equal(active, 0);
const started = [];
await assert.rejects(
  mapBounded([1, 2, 3, 4], 2, async (value) => {
    started.push(value);
    active += 1;
    try {
      if (value === 2) throw new Error('controlled failure');
      await delay(1);
      return value;
    } finally {
      active -= 1;
    }
  }),
  /controlled failure/u,
);
assert.deepEqual(started, [1, 2]);
assert.equal(active, 0);
assert.deepEqual(await mapBounded([], 2, async (value) => value), []);
```

**Expected:** results 2,4,6,8; peak active at most 2; active returns to 0.

**Verify:** Keep `assert.ok(peak <= 2 && peak > 0)`. Control: changing `active += 1; peak = Math.max(peak, active);` to `active -= 1; peak = Math.max(peak, active);` must make that check fail; then restore it.

## Exercise 6: Honor cancellation before the first attempt

Task: Abort a signal before calling retry and track attempted work.

The pre-check prevents starting known-cancelled work. Cancellation during an actual external operation also requires that operation's own cooperative signal support.

```javascript
const controller = new AbortController();
const reason = new Error('cancelled before start');
controller.abort(reason);
let attempts = 0;
await assert.rejects(
  retry(
    async () => {
      attempts += 1;
      return 1;
    },
    { signal: controller.signal },
  ),
  (error) => error === reason,
);
assert.equal(attempts, 0);
```

**Expected:** original reason rejects; attempts remain 0.

**Verify:** Keep `assert.equal(attempts, 0)`. Control: changing `let attempts = 0;` to `let attempts = 1;` must make that check fail; then restore it.

## After comparison

Fresh case: cap the backoff at 150. Predict the delays for four failed attempts with random value 1, and decide which errors your classifier treats as transient. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
