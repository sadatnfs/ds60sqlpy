# js-039: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

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

## Exercise 1: Complete one valid job lifecycle

Task: Start a queued job and complete it with value 7.

The transition sequence carries the attempt count forward. Completion is accepted only after a start established the running state.

```typescript
const started = transition(initial(), { type: 'start' });
const completed = transition(started, { type: 'complete', value: 7 });
assert.deepEqual(completed, { id: 'A', attempt: 1, kind: 'succeeded', value: 7 });
```

**Expected:** succeeded with attempt 1 and value 7.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject a result arriving before start

Task: Send complete directly to queued.

An unexpected event is visible rather than silently ignored. Ignoring it could hide ordering or duplicate-delivery defects in an outer integration.

```typescript
const queued = initial();
assert.throws(() => transition(queued, { type: 'complete', value: 7 }), /invalid transition/u);
assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });
```

**Expected:** invalid transition error; original remains queued.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
