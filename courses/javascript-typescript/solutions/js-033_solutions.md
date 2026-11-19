# js-033: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

An async function does not automatically move CPU work off the main JavaScript thread. A long synchronous loop inside an async function still blocks that thread until it yields or completes. Worker threads provide separate JavaScript execution contexts for CPU work. They are useful when the computation is large enough to justify startup, messaging and coordination costs. They do not make ordinary asynchronous file or network I/O inherently faster.

Messages normally use structured cloning. The receiver obtains its own copy of supported values, so mutating a received object does not change the sender's original object. Some values, such as functions, cannot be cloned. A transfer list can instead move ownership of an ArrayBuffer: the sender's buffer is detached, and the receiver gains access to its bytes. Transfer is an ownership change, not a shared mutable alias. SharedArrayBuffer has different synchronization requirements and is not used here.

A worker's lifecycle includes message, error and exit events. Receiving a result is not by itself proof that a worker has stopped. The helper terminates its owned worker in finally and applies a waiting timeout. A worker that exits without producing a result is a failure under this helper's contract. The examples use small fixed authored worker programs; eval:true is used only to keep those trusted fixtures self-contained. It must not be supplied with untrusted source text.

Workers share a process-level trust context and available host capabilities. They are not a security sandbox for arbitrary hostile JavaScript. Resource limits constrain selected V8 resources, not every possible process or external allocation. These tests establish actual thread messaging, ownership and teardown, not a speedup claim.

**Worker thread:** A separate JavaScript execution context for concurrent work.

**Structured clone:** Copying supported data across a message boundary.

**Transfer:** Moving ownership of a transferable object and detaching the sender view.

**Worker lifecycle:** Startup, messaging, errors, completion and termination ownership.

## Reading the implementation

new Worker creates the thread. workerData supplies a cloned or transferred initial payload. parentPort sends the result to the parent. A transferList names the exact ArrayBuffer ownership to move. Parent code listens for result, error and premature exit, then cleans up listeners and terminates the worker. Use process and thread identifiers only as observations of the actual run, not as fixed expected numbers.

## Exercise 1: Perform bounded CPU work in a real worker: change one input

Task: Copy Example A into a scratch `main.mjs` and change `10000,` to `10001,`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The result came through an actual worker message. The tiny workload illustrates mechanics and may be slower than a direct loop because startup costs dominate.

The unchanged code is the exercise block of Example A:

```javascript
const result = await runWorker(
  `const { parentPort, workerData, threadId } = require('node:worker_threads');
let sum = 0; for (let value = 1; value <= workerData; value += 1) sum += value;
parentPort.postMessage({ sum, threadId });`,
  10000,
);
assert.equal(result.sum, 50005000);
assert.ok(result.threadId > 0);
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal(result.sum, 50005000)`. Restoring the original line brings back the worked observation: sum 50005000; worker thread id positive.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(result.sum, 50005000)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Transfer a buffer and observe detachment: debug a regression

Task: A regression changed one token in Example B, so one line now reads `const buffer = Uint8Array.from([1, 3, 3]).buffer;`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

The sender loses access because ownership moved. Treating a detached buffer as still usable would create an invalid lifetime assumption.

The unchanged code is the exercise block of Example B:

```javascript
const buffer = Uint8Array.from([1, 2, 3]).buffer;
const result = await runWorker(
  `const { parentPort, workerData } = require('node:worker_threads');
const bytes = new Uint8Array(workerData); bytes[0] = 9; parentPort.postMessage([...bytes]);`,
  buffer,
  [buffer],
);
assert.equal(buffer.byteLength, 0);
assert.deepEqual(result, [9, 2, 3]);
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.deepEqual(result, [9, 2, 3])`; after it the line reads `const buffer = Uint8Array.from([1, 2, 3]).buffer;` again and parent byteLength 0; returned bytes 9,2,3.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.deepEqual(result, [9, 2, 3])` for this input.

## Exercise 3: Distinguish cloning from shared mutation

Task: Send an object, mutate the worker copy and compare the original.

Ordinary message data is cloned. This prevents accidental aliasing but can add copying cost for large payloads.

```javascript
const original = { value: 1 };
const result = await runWorker(
  `const { parentPort, workerData } = require('node:worker_threads');
workerData.value = 9; parentPort.postMessage(workerData.value);`,
  original,
);
assert.equal(result, 9);
assert.equal(original.value, 1);
```

**Expected:** worker returns 9; parent remains 1.

**Verify:** Keep a check equivalent to `assert.equal(original.value, 1)`. As a control, change `const original = { value: 1 };` to `const original = { value: 2 };`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Propagate an actual worker exception

Task: Run an authored worker that throws a fixture error.

Worker exceptions arrive through the error event. A parent that listens only for messages could wait forever for a result that cannot arrive.

```javascript
await assert.rejects(
  runWorker(`throw new Error('worker fixture failed');`, null),
  /worker fixture failed/u,
);
```

**Expected:** parent Promise rejects with worker fixture failed.

**Verify:** Keep a check equivalent to ``assert.rejects(runWorker(`throw new Error('worker fixture failed');`, null), /worker fixture failed/u)`` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## Exercise 5: Terminate an owned worker that remains alive

Task: Start a worker that reports ready and keeps an interval open, then terminate it.

A ready message does not close active handles. Explicit termination releases the owned worker and its interval; the test does not leave background work running.

```javascript
const worker = new Worker(
  `const { parentPort } = require('node:worker_threads'); setInterval(() => {}, 1000); parentPort.postMessage('ready');`,
  { eval: true },
);
try {
  assert.equal(
    await new Promise((resolve, reject) => {
      worker.once('message', resolve);
      worker.once('error', reject);
    }),
    'ready',
  );
} finally {
  const code = await worker.terminate();
  assert.equal(typeof code, 'number');
}
```

**Expected:** ready observed; terminate resolves with an exit code.

**Verify:** Keep a check equivalent to `assert.equal(typeof code, 'number')`. As a control, change `worker.once('error', reject); }), 'ready'` to `worker.once('error', reject); }), 'ready!'` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Reject data that cannot be cloned

Task: Try to pass a function through workerData.

Functions carry executable behavior and closure state, not supported cloneable message data. Define a data protocol and keep worker implementation separate.

```javascript
await assert.rejects(
  runWorker(
    `const { parentPort } = require('node:worker_threads'); parentPort.postMessage('unused');`,
    { callback: () => 1 },
  ),
  (error) => error.name === 'DataCloneError',
);
```

**Expected:** DataCloneError before useful worker execution.

**Verify:** Keep a check equivalent to ``assert.rejects(runWorker(`const { parentPort } = require('node:worker_threads'); parentPort.postMessage('unused');`, { callback: () => 1 }), (error) => error.name === 'DataCloneError')``. As a control, change `error => error.name === 'DataCloneError'` to `error => error.name !== 'DataCloneError'` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
