# js-032: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A stream transports chunks incrementally between a producer and a consumer. Chunks are not necessarily logical records, and reading incrementally does not guarantee bounded memory if the application stores every chunk. Backpressure communicates that a consumer has enough queued work and the producer should pause. Ignoring that signal can turn a fast producer and slow consumer into an ever-growing buffer.

Writable.write returns a Boolean indicating whether the producer should continue. A false return does not mean the chunk was rejected; it was accepted into the writable machinery, but the producer should wait for drain before supplying more. highWaterMark is a buffering threshold, not a hard cap on total process memory. In byte mode the relevant accounting is bytes; in object mode it counts objects, regardless of how large each object's reachable data is.

pipeline connects stages, forwards errors and coordinates teardown. A transform must call its callback exactly once per chunk, with either an error or transformed output. Calling it twice or never calling it breaks progress. An error after some output has been consumed does not roll those effects back. A pipeline writing an external destination needs an explicit transactional or temporary-output strategy if partial results must not become visible.

Cancellation also needs cooperation from asynchronous generators or other work outside the stream's immediate buffer. Passing the same signal to an awaited operation lets that work stop rather than keeping a generator suspended after the pipeline has been aborted. These examples use tiny chunks and controlled gates to prove lifecycle behavior without relying on a timing benchmark.

**Backpressure:** A signal that the producer should pause because the consumer has queued enough work.

**High-water mark:** A buffering threshold, not a universal memory cap.

**Pipeline:** Connected stages with coordinated completion and error handling.

**Partial output:** Results already consumed before a later failure occurs.

## Reading the implementation

Readable.from adapts an iterable. Transform receives chunks through transform(chunk, encoding, callback). Writable owns each write until its callback signals completion. The promise-based pipeline resolves only after completion or rejects on failure. Install the drain listener before releasing a controlled write callback so the event cannot be missed. finished observes stream completion after end. Object mode deliberately changes the unit of highWaterMark.

## Exercise 1: Run an actual transform pipeline: change one input

Task: Copy Example A into a scratch `main.mjs` and change `await pipeline(Readable.from(['ab', 'cd']), upper, sink);` to `await pipeline(Readable.from(['ab!', 'cd']), upper, sink);`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The result is observed after pipeline resolves, so every stage has completed. A print before awaiting completion could report an incomplete collection.

The unchanged code is the exercise block of Example A:

```javascript
const output = [];
const upper = new Transform({
  transform(chunk, encoding, callback) {
    callback(null, chunk.toString('utf8').toUpperCase());
  },
});
const sink = new Writable({
  write(chunk, encoding, callback) {
    output.push(chunk.toString());
    callback();
  },
});
await pipeline(Readable.from(['ab', 'cd']), upper, sink);
assert.equal(output.join(''), 'ABCD');
assert.equal(sink.writableFinished, true);
```

**Expected:** The changed run fails with an `AssertionError` at `assert.equal(output.join(''), 'ABCD')`. Restoring `await pipeline(Readable.from(['ab', 'cd']), upper, sink);` brings back: ABCD after successful pipeline completion.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(output.join(''), 'ABCD')` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Observe false write and drain without guessing timing: debug a regression

Task: A regression changed one token in Example B, so one line now reads `highWaterMark: 3,`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

False means pause, not retry the same chunk. Retrying it would duplicate data because the original write was already accepted.

The unchanged code is the exercise block of Example B:

```javascript
let release;
const sink = new Writable({
  highWaterMark: 2,
  write(chunk, encoding, callback) {
    release = callback;
  },
});
assert.equal(sink.write(Buffer.from('ab')), false);
assert.equal(sink.writableNeedDrain, true);
const drained = once(sink, 'drain');
release();
await drained;
sink.end();
await finished(sink);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(sink.write(Buffer.from('ab')), false)`. Restoring `highWaterMark: 2,` brings back: write returns false; drain follows release; stream finishes.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.equal(sink.write(Buffer.from('ab')), false)` for this input.

## Exercise 3: Propagate a producer failure and destroy the sink

Task: Use an async source that yields once then throws.

A failure may occur after earlier chunks reached the destination. Destruction releases resources but does not undo side effects the consumer already performed.

```javascript
async function* source() {
  yield 'first';
  throw new Error('source failed');
}
const sink = new Writable({
  write(chunk, encoding, callback) {
    callback();
  },
});
await assert.rejects(pipeline(Readable.from(source()), sink), /source failed/u);
assert.equal(sink.destroyed, true);
```

**Expected:** pipeline rejects with source failed; sink is destroyed.

**Verify:** Keep a check equivalent to `assert.equal(sink.destroyed, true)`. As a control, change `assert.equal(sink.destroyed, true);` to `assert.equal(sink.destroyed, false);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 4: Reject an invalid object in a transform

Task: Process numeric objects but reject a negative value through the callback.

The transform reports the error through its callback exactly once. Throwing from an unrelated later callback or hiding the error would break pipeline's error contract.

```javascript
const checked = new Transform({
  objectMode: true,
  transform(value, encoding, callback) {
    if (value < 0) callback(new RangeError('negative item'));
    else callback(null, value * 2);
  },
});
const sink = new Writable({
  objectMode: true,
  write(value, encoding, callback) {
    callback();
  },
});
await assert.rejects(pipeline(Readable.from([1, -1]), checked, sink), RangeError);
```

**Expected:** pipeline rejects with RangeError.

**Verify:** Keep a check equivalent to `assert.rejects(pipeline(Readable.from([1, -1]), checked, sink), RangeError)`. As a control, change `objectMode: true,` to `objectMode: false,`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Measure an object-mode threshold in objects

Task: Write one large-payload object to a writable with object-mode highWaterMark 1.

One object can retain a large graph. An object count threshold does not establish a byte-memory budget for arbitrary payloads.

```javascript
let release;
const sink = new Writable({
  objectMode: true,
  highWaterMark: 1,
  write(value, encoding, callback) {
    release = callback;
  },
});
assert.equal(sink.write({ payload: 'x'.repeat(1000) }), false);
assert.equal(sink.writableLength, 1);
const drained = once(sink, 'drain');
release();
await drained;
sink.end();
await finished(sink);
```

**Expected:** write false and writableLength 1, irrespective of payload string length.

**Verify:** Keep a check equivalent to `assert.equal(sink.write({ payload: 'x'.repeat(1000) }), false)`. As a control, change `highWaterMark: 1,` to `highWaterMark: 2,`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 6: Abort a generator and its awaited timer

Task: Start a source, await its readiness signal, then abort the shared signal.

The timer observes the same cancellation signal as the pipeline. Aborting only the outer wait could leave the generator's underlying operation alive.

```javascript
const controller = new AbortController();
let announce;
const ready = new Promise((resolve) => {
  announce = resolve;
});
let closed = false;
async function* source() {
  try {
    announce();
    await delay(1000, undefined, { signal: controller.signal });
    yield 'late';
  } finally {
    closed = true;
  }
}
const sink = new Writable({
  write(chunk, encoding, callback) {
    callback();
  },
});
const pending = pipeline(Readable.from(source()), sink, { signal: controller.signal });
await ready;
controller.abort();
await assert.rejects(pending, (error) => error.name === 'AbortError');
assert.equal(closed, true);
```

**Expected:** pipeline rejects with AbortError; generator finally runs.

**Verify:** Keep a check equivalent to `assert.equal(closed, true)`. As a control, change `finally { closed = true; }` to `finally { closed = false; }`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
