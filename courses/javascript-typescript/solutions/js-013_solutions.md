# js-013: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

Cancellation is a request communicated to cooperating code. It is not the same as a rejected Promise, a timeout observation, or forcibly rolling back work that already happened. AbortController owns the request; its signal can be passed to operations supporting cancellation. A signal records whether it was aborted and the reason. Repeating abort does not replace the first reason.

Check a signal before starting work, then arrange to observe it while waiting. A listener installed without a pre-check can miss an abort that already happened. Remove listeners after either success or failure to avoid keeping closures and resources alive. A timer-backed operation must clear its timer when cancelled; merely rejecting a wrapper Promise leaves the underlying timer running.

Timeouts express a waiting policy. A timeout does not establish that an external side effect failed to occur. Retrying a payment or write after a timeout requires an idempotency policy, introduced later. These examples own only small timers and trace arrays, making cancellation effects deterministic and reversible. No wall-clock speed claim is inferred from a one-millisecond delay.

**Cooperative cancellation:** An operation checks and acts on a cancellation request.

**Abort signal:** A read-only notification channel carrying abort state and reason.

**Deadline:** A policy limiting how long a caller is willing to wait.

**Cleanup ownership:** Responsibility for cancelling timers and removing listeners.

**Disposable:** An object whose Symbol.dispose or Symbol.asyncDispose method releases what it owns at block exit.

## Reading the implementation

controller.abort(reason) changes signal.aborted and signal.reason. signal.throwIfAborted throws the stored reason immediately. AbortSignal.any combines signals with a first-abort policy. Node's timers/promises delay accepts a signal and rejects with AbortError, retaining the caller's reason as cause. That wrapper error and the original reason are distinct objects. A custom API should document which cancellation shape it returns.

A using declaration binds an object whose Symbol.dispose method runs when the enclosing block exits, whether it completes or throws; await using does the same with an asynchronous Symbol.asyncDispose method. Node 24 runs both declarations natively. When several disposables share a block, they are released in reverse order of declaration.

## Exercise 1: Cancel a pending timer: predict an edited check

Task: In a scratch copy of Example A, change `await assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);` to `await assert.rejects(pending, error => error.name === 'AbortError!' && error.cause === reason);` inside its check. Does the check still pass?

The timer API cooperates with the signal and cancels its pending timer. The rejection shape is the API contract, not an arbitrary string comparison.

The unchanged code is the exercise block of Example A:

```javascript
const controller = new AbortController();
const reason = new Error('learner cancelled');
const pending = delay(1000, 'unused', { signal: controller.signal });
controller.abort(reason);
await assert.rejects(pending, (error) => error.name === 'AbortError' && error.cause === reason);
```

**Expected:** The edited run fails with an `AssertionError` at `await assert.rejects(pending, error => error.name === 'AbortError!' && error.cause === reason);`. Restoring `await assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);` brings back: abortError with the original reason as cause.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `await assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);`.

## Exercise 2: Reject an already aborted request before work: diagnose an edited check

Task: Example B's check was edited to read `await assert.rejects(cancellableValue(7, controller.signal, trace), error => error !== reason);`. Run it, explain the failure and restore the original.

The pre-check prevents side effects from beginning after cancellation was already known. It also handles an abort event that occurred before any listener was installed.

The unchanged code is the exercise block of Example B:

```javascript
const controller = new AbortController();
const reason = new Error('already stopped');
controller.abort(reason);
const trace = [];
await assert.rejects(cancellableValue(7, controller.signal, trace), (error) => error === reason);
assert.deepEqual(trace, []);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `await assert.rejects(cancellableValue(7, controller.signal, trace), error => error !== reason);`. Restoring `await assert.rejects(cancellableValue(7, controller.signal, trace), error => error === reason);` brings back: the exact reason is rejected; no timer starts.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Complete normally and clean up once

Task: Run the custom operation without aborting, then abort its signal after completion.

Completion removes the listener, so a later abort cannot mutate the finished operation's trace. A settled Promise alone would not remove an event listener.

```javascript
const controller = new AbortController();
const trace = [];
assert.equal(await cancellableValue(7, controller.signal, trace), 7);
controller.abort(new Error('too late'));
assert.deepEqual(trace, ['started', 'completed', 'cleaned']);
```

**Expected:** value 7; trace `started`, `completed`, `cleaned`, with cleanup exactly once.

**Verify:** Keep `assert.equal(await cancellableValue(7, controller.signal, trace), 7)`. Control: editing it to `assert.equal(await cancellableValue(8, controller.signal, trace), 7);` must make the check fail; then restore it.

## Exercise 4: Cancel custom work and release its timer

Task: Start the custom operation and immediately abort.

The abort handler clears the actual timer before rejecting. This checks the owned operation's lifecycle rather than only the consumer's wait.

```javascript
const controller = new AbortController();
const trace = [];
const reason = new Error('stop');
const pending = cancellableValue(7, controller.signal, trace);
controller.abort(reason);
await assert.rejects(pending, (error) => error === reason);
assert.deepEqual(trace, ['started', 'aborted', 'cleaned']);
```

**Expected:** rejected reason; trace `started`, `aborted`, `cleaned`.

**Verify:** Keep `assert.deepEqual(trace, ['started', 'aborted', 'cleaned'])`. Control: editing it to `assert.deepEqual(trace, ['started!', 'aborted', 'cleaned']);` must make the check fail; then restore it.

## Exercise 5: Keep the first abort reason

Task: Abort a controller twice and call throwIfAborted.

Abort state is a one-way transition. The first reason should be retained for diagnosis rather than overwritten by a later cleanup attempt.

```javascript
const controller = new AbortController();
const first = new Error('first');
controller.abort(first);
controller.abort(new Error('second'));
assert.equal(controller.signal.reason, first);
assert.throws(
  () => controller.signal.throwIfAborted(),
  (error) => error === first,
);
```

**Expected:** the first reason remains authoritative.

**Verify:** Keep `assert.throws(() => controller.signal.throwIfAborted(), (error) => error === first)`. Control: editing it to `assert.throws(() => controller.signal.throwIfAborted(), error => error !== first);` must make the check fail; then restore it.

## Exercise 6: Combine caller and deadline signals

Task: Combine a caller signal with a disposable one-second deadline, abort the caller first, then leave the block that owns the deadline.

Combining signals observes either source without aborting the other controller, so the deadline signal stays unaborted. The using declaration calls the deadline's Symbol.dispose method as soon as its block ends, so the one-second timer is cleared instead of keeping the process alive. Without it, every early exit, including an exception, would need its own clearTimeout call.

```javascript
const caller = new AbortController();
const trace = [];
const reason = new Error('caller stopped');
{
  using deadline = deadlineSignal(1000, trace);
  const combined = AbortSignal.any([caller.signal, deadline.signal]);
  caller.abort(reason);
  assert.equal(combined.reason, reason);
  assert.equal(deadline.signal.aborted, false);
}
assert.deepEqual(trace, ['deadline cleared']);
```

**Expected:** combined signal carries the caller reason; the deadline stays unaborted and its timer is cleared once when the block ends.

**Verify:** Keep `assert.deepEqual(trace, ['deadline cleared'])`. Control: editing it to `assert.deepEqual(trace, ['deadline cleared!']);` must make the check fail; then restore it.

## After comparison

Fresh case: write `withDeadline(work, ms)` that rejects with the deadline reason after `ms` but clears its timer when `work` settles first. Predict the trace for a fast job, a slow job and a caller abort that arrives before either finishes. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
