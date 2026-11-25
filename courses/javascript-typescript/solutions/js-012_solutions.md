# js-012: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A Promise records one eventual settlement: fulfillment with a value or rejection with a reason. Creating a Promise does not schedule its executor for later; the executor runs immediately. Reactions registered with then run asynchronously after the current synchronous work. This distinction explains why a log inside an executor can precede a log after construction while a then reaction follows both.

Node combines ECMAScript Promise jobs with host scheduling. This lesson proves only orderings that its setup establishes: synchronous statements finish before registered Promise reactions, and an awaited timer completes before code that follows that await. It deliberately avoids asserting a universal order between setTimeout and setImmediate, whose relative execution depends on context. Microtasks can delay other work if they continually schedule more microtasks.

Promise.all preserves input order in its result, even when operations finish in another order. Its rejection does not cancel the other operations. allSettled preserves both successes and failures when the application needs a complete outcome report. Await every owned operation or attach an intentional rejection handler. A fire-and-forget task is still running work with potential failure and cleanup responsibilities.

**Settlement:** The transition to fulfilled or rejected state.

**Reaction:** A handler scheduled after Promise settlement.

**Microtask:** A queued job processed at a microtask checkpoint.

**Promise composition:** Combining multiple eventual results under a defined failure policy.

## Reading the implementation

new Promise(executor) invokes executor immediately. resolve settles a value, adopting a supplied Promise's eventual state when relevant. then returns a new Promise; returning a value fulfills that chain and throwing rejects it. await suspends only the current async function, not the entire process. finally observes completion without replacing the original result unless it throws or returns a rejected Promise. A missing return in a then callback can lose an intended nested dependency.

## Exercise 1: Trace executor and reaction ordering: change one input

Task: In a scratch copy of Example A, change `const observed = pending.then(value => { trace.push('reaction'); return value; });` to `const observed = pending.then(value => { trace.push('reaction!'); return value; });`. Which check fails, and what value does it see?

The executor is synchronous; the registered reaction is not. The intermediate assertion makes that distinction visible before the await resumes.

The unchanged code is the exercise block of Example A:

```javascript
const trace = [];
const pending = new Promise((resolve) => {
  trace.push('executor');
  resolve(3);
});
const observed = pending.then((value) => {
  trace.push('reaction');
  return value;
});
trace.push('sync');
assert.deepEqual(trace, ['executor', 'sync']);
assert.equal(await observed, 3);
assert.deepEqual(trace, ['executor', 'sync', 'reaction']);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual(trace, ['executor', 'sync', 'reaction'])`. Restoring `const observed = pending.then(value => { trace.push('reaction'); return value; });` brings back: executor, sync, reaction.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const observed = pending.then(value => { trace.push('reaction'); return value; });`.

## Exercise 2: Compose values and rejection recovery: debug a regression

Task: A regression made one Example B line read `.then(value => value + 2)`. Locate and repair it without editing the check.

Throwing inside a reaction rejects the Promise returned by then. catch is a rejection reaction; its returned string fulfills the next Promise rather than rethrowing the failure.

The unchanged code is the exercise block of Example B:

```javascript
const result = await Promise.resolve(4)
  .then((value) => value * 2)
  .then((value) => {
    throw new Error(`bad value ${value}`);
  })
  .catch((error) => error.message);
assert.equal(result, 'bad value 8');
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(result, 'bad value 8')`. Restoring `.then(value => value * 2)` brings back: recovered message is bad value 8.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Preserve input order in Promise.all

Task: Resolve the second deferred Promise first, then the first.

Completion order and result indexing are separate. all associates each result with its original input position.

```javascript
let resolveFirst;
let resolveSecond;
const first = new Promise((resolve) => {
  resolveFirst = resolve;
});
const second = new Promise((resolve) => {
  resolveSecond = resolve;
});
const result = Promise.all([first, second]);
resolveSecond('second');
resolveFirst('first');
assert.deepEqual(await result, ['first', 'second']);
```

**Expected:** result remains `['first', 'second']`.

**Verify:** Keep `assert.deepEqual(await result, ['first', 'second'])`. Control: changing `resolveSecond('second');` to `resolveSecond('second!');` must make that check fail; then restore it.

## Exercise 4: Inspect every outcome with allSettled

Task: Combine fulfillment 2 with rejection offline.

allSettled creates an outcome record for each input. It does not convert a rejected operation into valid domain data; callers must branch on the status.

```javascript
const error = new Error('offline');
const outcomes = await Promise.allSettled([Promise.resolve(2), Promise.reject(error)]);
assert.deepEqual(outcomes[0], { status: 'fulfilled', value: 2 });
assert.equal(outcomes[1].status, 'rejected');
assert.equal(outcomes[1].reason, error);
```

**Expected:** statuses fulfilled/rejected with their original value and reason.

**Verify:** Keep `assert.deepEqual(outcomes[0], { status: 'fulfilled', value: 2 })`. Control: changing `const outcomes = await Promise.allSettled([Promise.resolve(2), Promise.reject(error)]);` to `const outcomes = await Promise.allSettled([Promise.resolve(3), Promise.reject(error)]);` must make that check fail; then restore it.

## Exercise 5: Demonstrate that race does not cancel losers

Task: Race an already fulfilled result against a deferred operation, then settle the deferred operation.

A selection combinator is not a cancellation protocol. If the losing task owns a socket or worker, the application still needs a supported cancellation and cleanup path.

```javascript
let finish;
const trace = [];
const slow = new Promise((resolve) => {
  finish = resolve;
}).then((value) => {
  trace.push(value);
  return value;
});
assert.equal(await Promise.race([Promise.resolve('fast'), slow]), 'fast');
finish('late');
assert.equal(await slow, 'late');
assert.deepEqual(trace, ['late']);
```

**Expected:** winner fast; deferred operation still completes later.

**Verify:** Keep `assert.equal(await Promise.race([Promise.resolve('fast'), slow]), 'fast')`. Control: editing it to `assert.equal(await Promise.race([Promise.resolve('fast!'), slow]), 'fast');` must make the check fail; then restore it.

## Exercise 6: Observe FIFO microtasks before an awaited timer

Task: Queue one Promise reaction and one queueMicrotask callback, then await a timer.

Both callbacks are queued in the stated order during one synchronous segment. The timer assertion is about this controlled trace, not a timing guarantee in milliseconds.

```javascript
const trace = [];
Promise.resolve().then(() => trace.push('promise'));
queueMicrotask(() => trace.push('microtask'));
trace.push('sync');
await delay(1);
trace.push('timer');
assert.deepEqual(trace, ['sync', 'promise', 'microtask', 'timer']);
```

**Expected:** trace `sync`, `promise`, `microtask`, `timer` in that order.

**Verify:** Keep `assert.deepEqual(trace, ['sync', 'promise', 'microtask', 'timer'])`. Control: changing `Promise.resolve().then(() => trace.push('promise'));` to `Promise.resolve().then(() => trace.push('promise!'));` must make that check fail; then restore it.

## After comparison

Fresh case: predict the trace for `Promise.resolve().then(() => log('a')).then(() => log('c')); queueMicrotask(() => log('b'));`. Each `then` waits for the previous reaction to finish, so the microtasks interleave as a, b, c. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
