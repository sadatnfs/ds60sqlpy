# js-013: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Cancellation is a request communicated to cooperating code. It is not the same as a rejected Promise, a timeout observation, or forcibly rolling back work that already happened. AbortController owns the request; its signal can be passed to operations supporting cancellation. A signal records whether it was aborted and the reason. Repeating abort does not replace the first reason.

Check a signal before starting work, then arrange to observe it while waiting. A listener installed without a pre-check can miss an abort that already happened. Remove listeners after either success or failure to avoid keeping closures and resources alive. A timer-backed operation must clear its timer when cancelled; merely rejecting a wrapper Promise leaves the underlying timer running.

Timeouts express a waiting policy. A timeout does not establish that an external side effect failed to occur. Retrying a payment or write after a timeout requires an idempotency policy, introduced later. These examples own only small timers and trace arrays, making cancellation effects deterministic and reversible. No wall-clock speed claim is inferred from a one-millisecond delay.

**Cooperative cancellation:** An operation checks and acts on a cancellation request.

**Abort signal:** A read-only notification channel carrying abort state and reason.

**Deadline:** A policy limiting how long a caller is willing to wait.

**Cleanup ownership:** Responsibility for cancelling timers and removing listeners.

## Reading the implementation

controller.abort(reason) changes signal.aborted and signal.reason. signal.throwIfAborted throws the stored reason immediately. AbortSignal.any combines signals with a first-abort policy. Node's timers/promises delay accepts a signal and rejects with AbortError, retaining the caller's reason as cause. That wrapper error and the original reason are distinct objects. A custom API should document which cancellation shape it returns.

## Exercise 1: Cancel a pending timer

Task: Start a timer with a signal, abort it, and inspect the rejection.

The timer API cooperates with the signal and cancels its pending timer. The rejection shape is the API contract, not an arbitrary string comparison.

```javascript
const controller = new AbortController();
const reason = new Error('learner cancelled');
const pending = delay(1000, 'unused', { signal: controller.signal });
controller.abort(reason);
await assert.rejects(pending, (error) => error.name === 'AbortError' && error.cause === reason);
```

**Expected:** AbortError with the original reason as cause.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject an already aborted request before work

Task: Abort before calling the custom operation.

The pre-check prevents side effects from beginning after cancellation was already known. It also handles an abort event that occurred before any listener was installed.

```javascript
const controller = new AbortController();
const reason = new Error('already stopped');
controller.abort(reason);
const trace = [];
await assert.rejects(cancellableValue(7, controller.signal, trace), (error) => error === reason);
assert.deepEqual(trace, []);
```

**Expected:** the exact reason is rejected; no timer starts.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Expected:** value 7; started,completed,cleaned exactly once.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Expected:** rejected reason; started,aborted,cleaned.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Combine caller and deadline signals

Task: Combine two controllers and abort the deadline controller.

Combining signals observes either source without aborting the other controller. The example triggers the deadline explicitly to keep the test independent of scheduler speed.

```javascript
const caller = new AbortController();
const deadline = new AbortController();
const combined = AbortSignal.any([caller.signal, deadline.signal]);
const reason = new Error('deadline');
deadline.abort(reason);
assert.equal(combined.aborted, true);
assert.equal(combined.reason, reason);
assert.equal(caller.signal.aborted, false);
```

**Expected:** combined signal is aborted with deadline reason.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
