# js-027: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

Promise<T> describes a fulfilled value. JavaScript rejection reasons are not captured by a second built-in error type parameter, so caught failures must still be inspected. Expected domain failures can instead be represented as a discriminated Result value. Unexpected operational failures may continue to reject. An API must explain which failure channel it uses, especially if it uses both.

Promise<Result<T>> introduces two decisions: await completion, then inspect the result. A failed Result is a fulfilled Promise containing an explicit failure value. It does not trigger catch. Conversely, a rejected Promise does not become a Result unless implementation code catches and translates it. Failing to distinguish these channels can turn an expected missing record into an unhandled rejection or turn a genuine programming error into misleading business data.

Cancellation remains a runtime cooperation protocol. A signal annotation proves that a compatible object was supplied, not that the operation observes it. The examples cancel a real timer and translate only its documented AbortError category. Batch operations must also choose whether to stop at the first rejection or retain every outcome. allSettled preserves outcome records, but rejected records must not be mistaken for valid values.

**Result channel:** An explicit success/failure value.

**Rejection channel:** A Promise failure propagated through throw or reject.

**Error translation:** Mapping a recognized failure into a documented result.

**Batch outcome policy:** The treatment of partial success and failure across several operations.

## Reading the implementation

A Result union carries either ok:true with value or ok:false with an error category. Narrow ok before reading the payload. An async function wraps a returned result in a Promise. Catch variables are unknown under strict checking. instanceof Error permits reading message, while matching a documented name or code determines whether translation is appropriate. Re-throw unrecognized failures to retain diagnosis.

## Exercise 1: Await and narrow a result: predict an edited check

Task: In a scratch copy of Example A, change `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });` to `assert.deepEqual(await lookup('missing'), { ok: true, error: 'not_found' });` inside its check. Does the check still pass?

Await establishes completion; the discriminant establishes domain success. Both conditions are needed before accessing the payload.

The unchanged code is the exercise block of Example A:

```typescript
const present = await lookup('A');
if (!present.ok) throw new Error(present.error);
assert.equal(present.value, 7);
assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });
```

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual(await lookup('missing'), { ok: true, error: 'not_found' });`. Restoring `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });` brings back: known value 7; absent error not_found.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });`.

## Exercise 2: Show a failure result does not invoke catch: debug a regression

Task: A regression made one Example B line read `let caught = 1;`. Locate and repair it without editing the check.

A result value is ordinary fulfilled data even when it describes a domain failure. The caller must branch on it explicitly.

The unchanged code is the exercise block of Example B:

```typescript
let caught = 0;
const result = await lookup('missing').catch(() => {
  caught += 1;
  return { ok: false as const, error: 'operational' as const };
});
assert.equal(caught, 0);
assert.deepEqual(result, { ok: false, error: 'not_found' });
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(caught, 0)`. Restoring `let caught = 0;` brings back: catch count 0; result still not_found.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Translate recognized cancellation

Task: Abort a real timer-backed operation.

The timer cooperates with the signal. Only its recognized abort error is translated; unrelated exceptions remain visible through rejection.

```typescript
const controller = new AbortController();
const pending = waitForValue(controller.signal);
controller.abort(new Error('stop'));
assert.deepEqual(await pending, { ok: false, error: 'cancelled' });
```

**Expected:** failure result cancelled.

**Verify:** Keep `assert.deepEqual(await pending, { ok: false, error: 'cancelled' })`. Control: editing it to `assert.deepEqual(await pending, { ok: true, error: 'cancelled' });` must make the check fail; then restore it.

## Exercise 4: Inspect an unknown rejection reason

Task: Reject with a string and normalize it at a reporting boundary.

Any JavaScript value can be a rejection reason. Assuming it always has a message property risks a second failure while reporting the first.

```typescript
function message(error: unknown): string {
  return error instanceof Error ? error.message : 'unclassified failure';
}
try {
  await Promise.reject('not an Error');
} catch (error: unknown) {
  assert.equal(message(error), 'unclassified failure');
}
```

**Expected:** diagnostic unclassified failure.

**Verify:** Keep `assert.equal(message(error), 'unclassified failure')`. Control: changing `return error instanceof Error ? error.message : 'unclassified failure';` to `return error instanceof Error ? error.message : 'unclassified failure!';` must make that check fail; then restore it.

## Exercise 5: Preserve every batch outcome

Task: Summarize one fulfilled value and one rejected task.

The status discriminant selects the outcome payload. Treating rejection data as unknown keeps the application boundary honest even when library declarations expose a broader type.

```typescript
const outcomes = await Promise.allSettled([
  Promise.resolve(2),
  Promise.reject(new Error('offline')),
]);
const summaries = outcomes.map((outcome) => {
  if (outcome.status === 'fulfilled') return `value:${outcome.value}`;
  const reason: unknown = outcome.reason;
  return `error:${reason instanceof Error ? reason.message : 'unknown'}`;
});
assert.deepEqual(summaries, ['value:2', 'error:offline']);
```

**Expected:** `value:2` and `error:offline`.

**Verify:** Keep `assert.deepEqual(summaries, ['value:2', 'error:offline'])`. Control: changing `Promise.resolve(2),` to `Promise.resolve(3),` must make that check fail; then restore it.

## Exercise 6: Reject unresolved and unnarrowed access

Task: Demonstrate both errors in an uncalled compile-time check.

These are distinct boundaries. Adding await fixes only the asynchronous layer; success narrowing is still required afterward.

```typescript
function negativeTypeCheck(result: Result<number>): void {
  // @ts-expect-error The failure alternative has no value.
  void result.value;
  // @ts-expect-error lookup returns a Promise, not an immediate payload.
  void lookup('A').value;
}
void negativeTypeCheck;
assert.deepEqual(await lookup('A'), { ok: true, value: 7 });
```

**Expected:** expected diagnostics for value before await or before narrowing.

**Verify:** Keep `assert.deepEqual(await lookup('A'), { ok: true, value: 7 })`. Control: editing it to `assert.deepEqual(await lookup('A!'), { ok: true, value: 7 });` must make the check fail; then restore it.

## After comparison

Fresh case: wrap a lookup that can resolve, return `not_found` or reject with a `TypeError`. Predict the normalized result for each path, then add a deadline that produces `cancelled` without hiding the other two outcomes. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
