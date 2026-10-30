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

## Exercise 1: Await and narrow a result

Task: Look up a known id and an absent id.

Await establishes completion; the discriminant establishes domain success. Both conditions are needed before accessing the payload.

```typescript
const present = await lookup('A');
if (!present.ok) throw new Error(present.error);
assert.equal(present.value, 7);
assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });
```

**Expected:** known value 7; absent error not_found.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Show a failure result does not invoke catch

Task: Attach catch to a lookup returning a not_found value.

A result value is ordinary fulfilled data even when it describes a domain failure. The caller must branch on it explicitly.

```typescript
let caught = 0;
const result = await lookup('missing').catch(() => {
  caught += 1;
  return { ok: false as const, error: 'operational' as const };
});
assert.equal(caught, 0);
assert.deepEqual(result, { ok: false, error: 'not_found' });
```

**Expected:** catch count 0; result still not_found.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Expected:** value:2 and error:offline.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
