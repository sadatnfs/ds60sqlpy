# js-012: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

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

## Exercise 1: Trace executor and reaction ordering

Task: Record executor, synchronous continuation and then reaction.

The executor is synchronous; the registered reaction is not. The intermediate assertion makes that distinction visible before the await resumes.

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

**Expected:** executor, sync, reaction.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Compose values and rejection recovery

Task: Double a value, throw an error, then recover through catch.

Throwing inside a reaction rejects the Promise returned by then. catch is a rejection reaction; its returned string fulfills the next Promise rather than rethrowing the failure.

```javascript
const result = await Promise.resolve(4)
  .then((value) => value * 2)
  .then((value) => {
    throw new Error(`bad value ${value}`);
  })
  .catch((error) => error.message);
assert.equal(result, 'bad value 8');
```

**Expected:** recovered message is bad value 8.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Expected:** result remains first,second.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Expected:** sync,promise,microtask,timer.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
