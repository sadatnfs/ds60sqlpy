# js-027: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

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

Task: Copy Example A into a scratch `main.mts` and change `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });` to `assert.deepEqual(await lookup('missing'), { ok: true, error: 'not_found' });` inside its check. Before running it, predict whether the check still passes and explain why; then restore it.

Await establishes completion; the discriminant establishes domain success. Both conditions are needed before accessing the payload.

The unchanged code is the exercise block of Example A:

```typescript
const present = await lookup('A');
if (!present.ok) throw new Error(present.error);
assert.equal(present.value, 7);
assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });
```

**Expected:** The changed run fails with an `AssertionError` at `assert.deepEqual(await lookup('missing'), { ok: true, error: 'not_found' });`. Restoring `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });` brings back: known value 7; absent error not_found.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and explain why the edited check rejects the values that `assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' })` accepts. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Show a failure result does not invoke catch: debug a regression

Task: A regression changed one token in Example B, so one line now reads `let caught = 1;`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

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

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.equal(caught, 0)` for this input.

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

**Verify:** Keep a check equivalent to `assert.deepEqual(await pending, { ok: false, error: 'cancelled' })`. As a control, change `assert.deepEqual(await pending, { ok: false, error: 'cancelled' });` to `assert.deepEqual(await pending, { ok: true, error: 'cancelled' });` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

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

**Verify:** Keep a check equivalent to `assert.equal(message(error), 'unclassified failure')`. As a control, change `return error instanceof Error ? error.message : 'unclassified failure';` to `return error instanceof Error ? error.message : 'unclassified failure!';`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

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

**Verify:** Keep a check equivalent to `assert.deepEqual(summaries, ['value:2', 'error:offline'])`. As a control, change `Promise.resolve(2),` to `Promise.resolve(3),`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

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

**Verify:** Keep a check equivalent to `assert.deepEqual(await lookup('A'), { ok: true, value: 7 })`. As a control, change `assert.deepEqual(await lookup('A'), { ok: true, value: 7 });` to `assert.deepEqual(await lookup('A!'), { ok: true, value: 7 });` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
