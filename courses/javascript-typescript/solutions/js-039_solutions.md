# js-039: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A state machine makes allowed transitions explicit. Instead of several independent booleans such as started, failed and done, a discriminated union represents one coherent state. An event requests a transition; a pure transition function either produces the next valid state or rejects an invalid event for the current state. This prevents combinations such as simultaneously running and completed from being expressible in ordinary checked code.

A functional core computes decisions without performing I/O. An outer shell can persist the decision, send a message or render it. Keeping the transition pure makes replay and failure analysis straightforward: the same initial state and event sequence should produce the same final state. It does not make external side effects automatically exactly once. The shell still needs a durable transaction and idempotency policy if it coordinates real storage or remote work.

The fixture models a bounded job lifecycle: queued, running, succeeded, failed or cancelled. Starting increments an attempt count. A failed job may retry only while fewer than three attempts have been started. Succeeded and cancelled are terminal. Cancellation is a state transition in this pure model; it does not physically stop a worker or cancel a socket. An integration layer must connect the decision to those operational actions and report their outcomes.

Readonly types express the intended consumer view. The tests also verify that transition does not mutate the input object, because static annotations alone do not prove runtime immutability. Invalid numeric results remain a runtime domain problem even when success carries a TypeScript number.

**State machine:** A set of coherent states and allowed transitions between them.

**Event:** A request to transition under the current state.

**Functional core:** Pure decision logic separated from I/O effects.

**Replay:** Recomputing state from an initial value and an event sequence.

## Reading the implementation

Each state has kind plus common id and attempt fields. Events form another closed union. switch narrows the event, and state guards define where it is legal. New objects are returned with spread or explicit fields. A never guard protects event exhaustiveness. replay uses reduce to apply the same transition repeatedly. The attempt invariant is checked before retrying, not after accidentally starting a fourth attempt.

## Exercise 1: Complete one valid job lifecycle: change one input

Task: In a scratch copy of Example A, change `const completed = transition(started, { type: 'complete', value: 7 });` to `const completed = transition(started, { type: 'complete', value: 8 });`. Which check fails, and what value does it see?

The transition sequence carries the attempt count forward. Completion is accepted only after a start established the running state.

The unchanged code is the exercise block of Example A:

```typescript
const started = transition(initial(), { type: 'start' });
const completed = transition(started, { type: 'complete', value: 7 });
assert.deepEqual(completed, { id: 'A', attempt: 1, kind: 'succeeded', value: 7 });
```

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual(completed, { id: 'A', attempt: 1, kind: 'succeeded', value: 7 })`. Restoring `const completed = transition(started, { type: 'complete', value: 7 });` brings back: succeeded with attempt 1 and value 7.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const completed = transition(started, { type: 'complete', value: 7 });`.

## Exercise 2: Reject a result arriving before start: diagnose an edited check

Task: Example B's check was edited to read `assert.deepEqual(queued, { id: 'A', attempt: 1, kind: 'queued' });`. Run it, explain the failure and restore the original.

An unexpected event is visible rather than silently ignored. Ignoring it could hide ordering or duplicate-delivery defects in an outer integration.

The unchanged code is the exercise block of Example B:

```typescript
const queued = initial();
assert.throws(() => transition(queued, { type: 'complete', value: 7 }), /invalid transition/u);
assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.deepEqual(queued, { id: 'A', attempt: 1, kind: 'queued' });`. Restoring `assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });` brings back: invalid transition error; original remains queued.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Enforce the retry budget

Task: Fail three started attempts and try to retry once more.

The limit counts actual starts rather than the number of failure messages. The final failed state remains available for diagnosis after the budget is exhausted.

```typescript
let state: State = initial();
for (let attempt = 1; attempt <= 3; attempt += 1) {
  state = transition(state, { type: 'start' });
  state = transition(state, { type: 'fail', reason: 'temporary' });
  if (attempt < 3) state = transition(state, { type: 'retry' });
}
assert.equal(state.attempt, 3);
assert.throws(() => transition(state, { type: 'retry' }), /retry budget/u);
```

**Expected:** attempt 3 remains failed; further retry rejects.

**Verify:** Keep `assert.equal(state.attempt, 3)`. Control: changing `for (let attempt = 1; attempt <= 3; attempt += 1) {` to `for (let attempt = 1; attempt < 3; attempt += 1) {` must make that check fail; then restore it.

## Exercise 4: Keep cancellation terminal

Task: Cancel a running job, then deliver a late completion.

The model prevents a late event from reviving a terminal job. A real worker still needs a cancellation channel; this pure state decision does not stop it by itself.

```typescript
const cancelled = transition(transition(initial(), { type: 'start' }), {
  type: 'cancel',
  reason: 'user request',
});
assert.equal(cancelled.kind, 'cancelled');
assert.throws(() => transition(cancelled, { type: 'complete', value: 2 }), /terminal/u);
```

**Expected:** cancelled state remains; late completion rejects.

**Verify:** Keep `assert.equal(cancelled.kind, 'cancelled')`. Control: editing it to `assert.equal(cancelled.kind, 'cancelled!');` must make the check fail; then restore it.

## Exercise 5: Replay deterministically from the same history

Task: Replay start, failure, retry, start and completion twice.

The event history is sufficient for this deterministic decision logic. Time, randomness or I/O would need explicit inputs rather than hidden dependencies inside transition.

```typescript
const events: Event[] = [
  { type: 'start' },
  { type: 'fail', reason: 'retryable' },
  { type: 'retry' },
  { type: 'start' },
  { type: 'complete', value: 3 },
];
const first = replay(initial(), events);
const second = replay(initial(), events);
assert.deepEqual(first, second);
assert.deepEqual(first, { id: 'A', attempt: 2, kind: 'succeeded', value: 3 });
```

**Expected:** both runs produce the same succeeded attempt-2 state.

**Verify:** Keep `assert.deepEqual(first, { id: 'A', attempt: 2, kind: 'succeeded', value: 3 })`. Control: changing `{ type: 'complete', value: 3 },` to `{ type: 'complete', value: 4 },` must make that check fail; then restore it.

## Exercise 6: Preserve input state and validate success values

Task: Compare input before and after a transition, then reject NaN as a result.

The test checks actual non-mutation and numeric validity. A readonly number annotation would not establish either property by itself.

```typescript
const queued = initial();
const before = structuredClone(queued);
const running = transition(queued, { type: 'start' });
assert.deepEqual(queued, before);
assert.notEqual(running, queued);
assert.throws(() => transition(running, { type: 'complete', value: NaN }), RangeError);
```

**Expected:** input unchanged; new object returned; NaN rejects.

**Verify:** Keep the check `assert.throws(() => transition(running, { type: 'complete', value: NaN }), RangeError)`; name an input that would make it fail and the value that changes.

## After comparison

Fresh case: add a `paused` state reachable only from `running`. Predict which events become valid or invalid, then replay a history that pauses and resumes twice and confirm both runs agree. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
