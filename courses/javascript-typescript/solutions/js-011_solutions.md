# js-011: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

An iterable describes how to obtain an iterator. An iterator describes how to ask for the next value. A generator function is a convenient state machine implementing this protocol: calling it creates a suspended generator, next() advances execution to a yield, and the result reports value plus done. The generator body does not run merely because the generator object was created.

Laziness allows a consumer to stop before computing every possible value. It does not make an expensive step cheap, and converting a huge iterable with spread still materializes every value in memory. A generator object is usually a one-use cursor; a generator function can create a fresh cursor each time. This matters when a second pass unexpectedly produces no rows.

Early termination is also a resource question. for...of invokes the iterator's return method when a break leaves the loop. A generator's finally block then runs if execution has entered its try block. Code that manually calls next() and abandons the iterator must explicitly close it when it owns resources. The examples record lifecycle events so cleanup is an observed state transition, not a comment promising eventual cleanup.

**Iterable:** An object with a Symbol.iterator method producing an iterator.

**Iterator:** An object whose next method returns a value/done record.

**Suspension:** Preserving local execution state between requests.

**Iterator closing:** Calling return to terminate an iterator and release owned resources.

## Reading the implementation

The star in function* declares a generator; yield produces a value and suspends the local execution state. A return ends iteration and may supply a final result, but that result is not another yielded item. yield* delegates to another iterable. Calling next(value) sends a value back into the suspended yield expression. The first next argument has no waiting yield to receive it. for...of reads yielded values and stops on done true.

## Exercise 1: Trace lazy execution

Task: Create a generator, inspect its trace, then request one value.

Creating the cursor and executing its body are separate events. The trace distinguishes laziness from eager construction of an array.

```javascript
const trace = [];
function* values() {
  trace.push('started');
  yield 2;
  trace.push('continued');
  yield 4;
}
const cursor = values();
assert.deepEqual(trace, []);
assert.deepEqual(cursor.next(), { value: 2, done: false });
assert.deepEqual(trace, ['started']);
cursor.return();
```

**Expected:** trace is empty before next; then started, with value 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Close on an early break

Task: Iterate one value from a generator protected by finally, then break.

The loop performs iterator closing when control exits through break. Resource-owning iterators should place cleanup in finally instead of assuming every consumer reaches the end.

```javascript
const trace = [];
function* rows() {
  try {
    trace.push('opened');
    yield 1;
    yield 2;
  } finally {
    trace.push('closed');
  }
}
for (const value of rows()) {
  trace.push(value);
  break;
}
assert.deepEqual(trace, ['opened', 1, 'closed']);
```

**Expected:** trace records opened, value 1, closed.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Distinguish a cursor from a fresh iterable

Task: Consume one generator twice, then create a second generator.

The exhausted cursor retains its completion state. Reusing it does not restart the function; the caller must create a new generator.

```javascript
const cursor = range(3);
assert.deepEqual([...cursor], [0, 1, 2]);
assert.deepEqual([...cursor], []);
assert.deepEqual([...range(3)], [0, 1, 2]);
```

**Expected:** first pass is 0,1,2; second is empty; fresh pass repeats 0,1,2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Inspect the final return value

Task: Read a generator yielding 1 and returning 9, then compare spread.

A final return value belongs to the completion record. Treating it as another ordinary item would change the data stream.

```javascript
function* sample() {
  yield 1;
  return 9;
}
const cursor = sample();
assert.deepEqual(cursor.next(), { value: 1, done: false });
assert.deepEqual(cursor.next(), { value: 9, done: true });
assert.deepEqual([...sample()], [1]);
```

**Expected:** next records value 1/done false then 9/done true; spread contains only 1.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Send a value into a suspended generator

Task: Suspend at a request, then send 4 to produce its double.

The second next call resolves the suspended yield expression to 4. This is a two-way protocol, though simple data pipelines often need only one-way yielding.

```javascript
function* conversation() {
  const answer = yield 'request';
  yield answer * 2;
}
const cursor = conversation();
assert.equal(cursor.next().value, 'request');
assert.equal(cursor.next(4).value, 8);
cursor.return();
```

**Expected:** request, then 8.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Bound the range and validate configuration

Task: Produce an empty range and reject negative or fractional lengths.

Validation inside a generator runs when iteration begins, not when its object is created. The assertions therefore consume the generator to observe the failure.

```javascript
assert.deepEqual([...range(0)], []);
assert.throws(() => [...range(-1)], RangeError);
assert.throws(() => [...range(1.5)], RangeError);
```

**Expected:** empty array for 0; RangeError for -1 and 1.5.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
