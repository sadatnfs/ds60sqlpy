from render import add, ex

NODE = "https://nodejs.org/docs/latest-v24.x/api/"

add(
    10,
    """A module is both a namespace and a dependency boundary. An ES module declares imports and exports before its body executes. The loader resolves dependencies, links the bindings, then evaluates the graph. An imported binding observes the exporting module\'s current binding; it is not a copied snapshot. Importing the same resolved module URL again normally returns the cached module namespace and does not repeat its initialization.

Node uses .mjs to select ES module syntax explicitly. Relative imports require the intended filename extension. Bare package names use package resolution rules; node: names identify built-in modules. CommonJS uses a different export object and loading model. Interoperability is useful, but guessing that an arbitrary CommonJS property will become a named ES export is fragile. This lesson imports a CommonJS default export deliberately and keeps ESM bindings explicit.

The fixtures create tiny source files in a newly allocated temporary directory, import them, and remove only that directory afterward. They do not install a package or edit the repository. Unique directory URLs avoid accidental cache sharing between exercises. A production module should usually avoid expensive side effects at import time: top-level file writes, network requests or background listeners make dependency loading itself operational work.""",
    """An export declaration exposes a binding. import() returns a Promise for the module namespace, so asynchronous loading must be awaited. pathToFileURL converts a platform filesystem path to a correctly encoded file URL; concatenating file: with a raw path fails for spaces and reserved characters. A namespace property cannot be reassigned by the importer, although exported functions may update their own module state. finally runs cleanup after success and after an import rejection.""",
    [
        ("Live binding", "An imported name observes updates made to the exporting binding."),
        ("Module namespace", "The read-only view of a module's exported bindings."),
        ("Resolution", "Mapping a module specifier to the module that will be loaded."),
        ("Module cache", "Reuse of an already loaded module for its resolved identity."),
    ],
    [
        ex(
            "Observe a live binding",
            "Import a mutable counter and its increment function, then inspect the count before and after incrementing.",
            "count changes from 0 to 1 through the imported namespace.",
            r"""await withModules({ 'counter.mjs': 'export let count = 0; export function increment() { count += 1; }' }, async directory => {
  const module = await import(pathToFileURL(join(directory, 'counter.mjs')).href);
  assert.equal(module.count, 0);
  module.increment();
  assert.equal(module.count, 1);
});""",
            "The importer receives a binding view. Copying count into a local number would instead preserve the value read at that moment. The distinction becomes visible only after the exporter changes state.",
        ),
        ex(
            "Resolve a relative dependency",
            "Create a main module importing twice from ./math.mjs, then call its export.",
            "answer equals 8.",
            r"""await withModules({ 'math.mjs': 'export const twice = value => 2 * value;', 'main.mjs': "import { twice } from './math.mjs'; export const answer = twice(4);" }, async directory => {
  const module = await import(pathToFileURL(join(directory, 'main.mjs')).href);
  assert.equal(module.answer, 8);
});""",
            "The relative path is resolved from the importing file, not from the process working directory. Naming the .mjs extension makes the loader contract explicit.",
        ),
        ex(
            "Prove cached module identity",
            "Import one URL twice and compare the namespace and exported object.",
            "both namespace and object identities are shared.",
            r"""await withModules({ 'state.mjs': 'export const state = { visits: 0 };' }, async directory => {
  const url = pathToFileURL(join(directory, 'state.mjs')).href;
  const first = await import(url);
  const second = await import(url);
  assert.equal(first, second);
  assert.equal(first.state, second.state);
});""",
            "A module is not a factory that automatically resets on each import. For independent instances, export a factory function and call it explicitly.",
        ),
        ex(
            "Inspect CommonJS interoperability",
            "Import a .cjs file exporting an object through its default binding.",
            "default.label equals legacy.",
            r"""await withModules({ 'legacy.cjs': "module.exports = { label: 'legacy' };" }, async directory => {
  const module = await import(pathToFileURL(join(directory, 'legacy.cjs')).href);
  assert.equal(module.default.label, 'legacy');
});""",
            "The default binding is the intentional CommonJS export-object boundary here. This example does not depend on heuristic named-export detection.",
        ),
        ex(
            "Reject a missing dependency",
            "Import a module with a nonexistent relative dependency and preserve the loader error code.",
            "ERR_MODULE_NOT_FOUND.",
            r"""await withModules({ 'broken.mjs': "import './missing.mjs';" }, async directory => {
  await assert.rejects(import(pathToFileURL(join(directory, 'broken.mjs')).href), error => error.code === 'ERR_MODULE_NOT_FOUND');
});""",
            "Missing dependency resolution is a loader failure before useful module evaluation. Catching every import error and returning an empty object would disguise a broken dependency graph.",
        ),
        ex(
            "Respect namespace ownership",
            "Attempt to assign an exported binding from the importer.",
            "TypeError; exported value remains 3.",
            r"""await withModules({ 'fixed.mjs': 'export let value = 3;' }, async directory => {
  const module = await import(pathToFileURL(join(directory, 'fixed.mjs')).href);
  assert.throws(() => { module.value = 9; }, TypeError);
  assert.equal(module.value, 3);
});""",
            "Live does not mean writable from every importer. The exporter owns assignment to its binding. Expose a deliberate operation when mutation is part of the public contract.",
        ),
    ],
    helper="""async function withModules(files, use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-modules-'));
  try {
    for (const [name, source] of Object.entries(files)) await writeFile(join(directory, name), source, 'utf8');
    return await use(directory);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { mkdtemp, writeFile, rm } from 'node:fs/promises';\nimport { tmpdir } from 'node:os';\nimport { join } from 'node:path';\nimport { pathToFileURL } from 'node:url';",
    source=NODE + "esm.html",
)

add(
    11,
    """An iterable describes how to obtain an iterator. An iterator describes how to ask for the next value. A generator function is a convenient state machine implementing this protocol: calling it creates a suspended generator, next() advances execution to a yield, and the result reports value plus done. The generator body does not run merely because the generator object was created.

Laziness allows a consumer to stop before computing every possible value. It does not make an expensive step cheap, and converting a huge iterable with spread still materializes every value in memory. A generator object is usually a one-use cursor; a generator function can create a fresh cursor each time. This matters when a second pass unexpectedly produces no rows.

Early termination is also a resource question. for...of invokes the iterator\'s return method when a break leaves the loop. A generator\'s finally block then runs if execution has entered its try block. Code that manually calls next() and abandons the iterator must explicitly close it when it owns resources. The examples record lifecycle events so cleanup is an observed state transition, not a comment promising eventual cleanup.""",
    """The star in function* declares a generator; yield produces a value and suspends the local execution state. A return ends iteration and may supply a final result, but that result is not another yielded item. yield* delegates to another iterable. Calling next(value) sends a value back into the suspended yield expression. The first next argument has no waiting yield to receive it. for...of reads yielded values and stops on done true.""",
    [
        ("Iterable", "An object with a Symbol.iterator method producing an iterator."),
        ("Iterator", "An object whose next method returns a value/done record."),
        ("Suspension", "Preserving local execution state between requests."),
        (
            "Iterator closing",
            "Calling return to terminate an iterator and release owned resources.",
        ),
    ],
    [
        ex(
            "Trace lazy execution",
            "Create a generator, inspect its trace, then request one value.",
            "trace is empty before next; then started, with value 2.",
            r"""const trace = [];
function* values() { trace.push('started'); yield 2; trace.push('continued'); yield 4; }
const cursor = values();
assert.deepEqual(trace, []);
assert.deepEqual(cursor.next(), { value: 2, done: false });
assert.deepEqual(trace, ['started']);
cursor.return();""",
            "Creating the cursor and executing its body are separate events. The trace distinguishes laziness from eager construction of an array.",
        ),
        ex(
            "Close on an early break",
            "Iterate one value from a generator protected by finally, then break.",
            "trace records opened, value 1, closed.",
            r"""const trace = [];
function* rows() { try { trace.push('opened'); yield 1; yield 2; } finally { trace.push('closed'); } }
for (const value of rows()) { trace.push(value); break; }
assert.deepEqual(trace, ['opened', 1, 'closed']);""",
            "The loop performs iterator closing when control exits through break. Resource-owning iterators should place cleanup in finally instead of assuming every consumer reaches the end.",
        ),
        ex(
            "Distinguish a cursor from a fresh iterable",
            "Consume one generator twice, then create a second generator.",
            "first pass is 0,1,2; second is empty; fresh pass repeats 0,1,2.",
            r"""const cursor = range(3);
assert.deepEqual([...cursor], [0, 1, 2]);
assert.deepEqual([...cursor], []);
assert.deepEqual([...range(3)], [0, 1, 2]);""",
            "The exhausted cursor retains its completion state. Reusing it does not restart the function; the caller must create a new generator.",
        ),
        ex(
            "Inspect the final return value",
            "Read a generator yielding 1 and returning 9, then compare spread.",
            "next records value 1/done false then 9/done true; spread contains only 1.",
            r"""function* sample() { yield 1; return 9; }
const cursor = sample();
assert.deepEqual(cursor.next(), { value: 1, done: false });
assert.deepEqual(cursor.next(), { value: 9, done: true });
assert.deepEqual([...sample()], [1]);""",
            "A final return value belongs to the completion record. Treating it as another ordinary item would change the data stream.",
        ),
        ex(
            "Send a value into a suspended generator",
            "Suspend at a request, then send 4 to produce its double.",
            "request, then 8.",
            r"""function* conversation() { const answer = yield 'request'; yield answer * 2; }
const cursor = conversation();
assert.equal(cursor.next().value, 'request');
assert.equal(cursor.next(4).value, 8);
cursor.return();""",
            "The second next call resolves the suspended yield expression to 4. This is a two-way protocol, though simple data pipelines often need only one-way yielding.",
        ),
        ex(
            "Bound the range and validate configuration",
            "Produce an empty range and reject negative or fractional lengths.",
            "empty array for 0; RangeError for -1 and 1.5.",
            r"""assert.deepEqual([...range(0)], []);
assert.throws(() => [...range(-1)], RangeError);
assert.throws(() => [...range(1.5)], RangeError);""",
            "Validation inside a generator runs when iteration begins, not when its object is created. The assertions therefore consume the generator to observe the failure.",
        ),
    ],
    helper="""function* range(length) {
  if (!Number.isInteger(length) || length < 0 || length > 1000) throw new RangeError('length must be an integer from 0 to 1000');
  for (let value = 0; value < length; value += 1) yield value;
}""",
    source="https://tc39.es/ecma262/multipage/control-abstraction-objects.html",
)

add(
    12,
    """A Promise records one eventual settlement: fulfillment with a value or rejection with a reason. Creating a Promise does not schedule its executor for later; the executor runs immediately. Reactions registered with then run asynchronously after the current synchronous work. This distinction explains why a log inside an executor can precede a log after construction while a then reaction follows both.

Node combines ECMAScript Promise jobs with host scheduling. This lesson proves only orderings that its setup establishes: synchronous statements finish before registered Promise reactions, and an awaited timer completes before code that follows that await. It deliberately avoids asserting a universal order between setTimeout and setImmediate, whose relative execution depends on context. Microtasks can delay other work if they continually schedule more microtasks.

Promise.all preserves input order in its result, even when operations finish in another order. Its rejection does not cancel the other operations. allSettled preserves both successes and failures when the application needs a complete outcome report. Await every owned operation or attach an intentional rejection handler. A fire-and-forget task is still running work with potential failure and cleanup responsibilities.""",
    """new Promise(executor) invokes executor immediately. resolve settles a value, adopting a supplied Promise\'s eventual state when relevant. then returns a new Promise; returning a value fulfills that chain and throwing rejects it. await suspends only the current async function, not the entire process. finally observes completion without replacing the original result unless it throws or returns a rejected Promise. A missing return in a then callback can lose an intended nested dependency.""",
    [
        ("Settlement", "The transition to fulfilled or rejected state."),
        ("Reaction", "A handler scheduled after Promise settlement."),
        ("Microtask", "A queued job processed at a microtask checkpoint."),
        (
            "Promise composition",
            "Combining multiple eventual results under a defined failure policy.",
        ),
    ],
    [
        ex(
            "Trace executor and reaction ordering",
            "Record executor, synchronous continuation and then reaction.",
            "executor, sync, reaction.",
            r"""const trace = [];
const pending = new Promise(resolve => { trace.push('executor'); resolve(3); });
const observed = pending.then(value => { trace.push('reaction'); return value; });
trace.push('sync');
assert.deepEqual(trace, ['executor', 'sync']);
assert.equal(await observed, 3);
assert.deepEqual(trace, ['executor', 'sync', 'reaction']);""",
            "The executor is synchronous; the registered reaction is not. The intermediate assertion makes that distinction visible before the await resumes.",
        ),
        ex(
            "Compose values and rejection recovery",
            "Double a value, throw an error, then recover through catch.",
            "recovered message is bad value 8.",
            r"""const result = await Promise.resolve(4)
  .then(value => value * 2)
  .then(value => { throw new Error(`bad value ${value}`); })
  .catch(error => error.message);
assert.equal(result, 'bad value 8');""",
            "Throwing inside a reaction rejects the Promise returned by then. catch is a rejection reaction; its returned string fulfills the next Promise rather than rethrowing the failure.",
        ),
        ex(
            "Preserve input order in Promise.all",
            "Resolve the second deferred Promise first, then the first.",
            "result remains first,second.",
            r"""let resolveFirst;
let resolveSecond;
const first = new Promise(resolve => { resolveFirst = resolve; });
const second = new Promise(resolve => { resolveSecond = resolve; });
const result = Promise.all([first, second]);
resolveSecond('second');
resolveFirst('first');
assert.deepEqual(await result, ['first', 'second']);""",
            "Completion order and result indexing are separate. all associates each result with its original input position.",
        ),
        ex(
            "Inspect every outcome with allSettled",
            "Combine fulfillment 2 with rejection offline.",
            "statuses fulfilled/rejected with their original value and reason.",
            r"""const error = new Error('offline');
const outcomes = await Promise.allSettled([Promise.resolve(2), Promise.reject(error)]);
assert.deepEqual(outcomes[0], { status: 'fulfilled', value: 2 });
assert.equal(outcomes[1].status, 'rejected');
assert.equal(outcomes[1].reason, error);""",
            "allSettled creates an outcome record for each input. It does not convert a rejected operation into valid domain data; callers must branch on the status.",
        ),
        ex(
            "Demonstrate that race does not cancel losers",
            "Race an already fulfilled result against a deferred operation, then settle the deferred operation.",
            "winner fast; deferred operation still completes later.",
            r"""let finish;
const trace = [];
const slow = new Promise(resolve => { finish = resolve; }).then(value => { trace.push(value); return value; });
assert.equal(await Promise.race([Promise.resolve('fast'), slow]), 'fast');
finish('late');
assert.equal(await slow, 'late');
assert.deepEqual(trace, ['late']);""",
            "A selection combinator is not a cancellation protocol. If the losing task owns a socket or worker, the application still needs a supported cancellation and cleanup path.",
        ),
        ex(
            "Observe FIFO microtasks before an awaited timer",
            "Queue one Promise reaction and one queueMicrotask callback, then await a timer.",
            "sync,promise,microtask,timer.",
            r"""const trace = [];
Promise.resolve().then(() => trace.push('promise'));
queueMicrotask(() => trace.push('microtask'));
trace.push('sync');
await delay(1);
trace.push('timer');
assert.deepEqual(trace, ['sync', 'promise', 'microtask', 'timer']);""",
            "Both callbacks are queued in the stated order during one synchronous segment. The timer assertion is about this controlled trace, not a timing guarantee in milliseconds.",
        ),
    ],
    imports="import { strict as assert } from 'node:assert';\nimport { setTimeout as delay } from 'node:timers/promises';",
    source=NODE + "timers.html",
)

add(
    13,
    """Cancellation is a request communicated to cooperating code. It is not the same as a rejected Promise, a timeout observation, or forcibly rolling back work that already happened. AbortController owns the request; its signal can be passed to operations supporting cancellation. A signal records whether it was aborted and the reason. Repeating abort does not replace the first reason.

Check a signal before starting work, then arrange to observe it while waiting. A listener installed without a pre-check can miss an abort that already happened. Remove listeners after either success or failure to avoid keeping closures and resources alive. A timer-backed operation must clear its timer when cancelled; merely rejecting a wrapper Promise leaves the underlying timer running.

Timeouts express a waiting policy. A timeout does not establish that an external side effect failed to occur. Retrying a payment or write after a timeout requires an idempotency policy, introduced later. These examples own only small timers and trace arrays, making cancellation effects deterministic and reversible. No wall-clock speed claim is inferred from a one-millisecond delay.""",
    """controller.abort(reason) changes signal.aborted and signal.reason. signal.throwIfAborted throws the stored reason immediately. AbortSignal.any combines signals with a first-abort policy. Node\'s timers/promises delay accepts a signal and rejects with AbortError, retaining the caller\'s reason as cause. That wrapper error and the original reason are distinct objects. A custom API should document which cancellation shape it returns.""",
    [
        ("Cooperative cancellation", "An operation checks and acts on a cancellation request."),
        ("Abort signal", "A read-only notification channel carrying abort state and reason."),
        ("Deadline", "A policy limiting how long a caller is willing to wait."),
        ("Cleanup ownership", "Responsibility for cancelling timers and removing listeners."),
    ],
    [
        ex(
            "Cancel a pending timer",
            "Start a timer with a signal, abort it, and inspect the rejection.",
            "AbortError with the original reason as cause.",
            r"""const controller = new AbortController();
const reason = new Error('learner cancelled');
const pending = delay(1000, 'unused', { signal: controller.signal });
controller.abort(reason);
await assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);""",
            "The timer API cooperates with the signal and cancels its pending timer. The rejection shape is the API contract, not an arbitrary string comparison.",
        ),
        ex(
            "Reject an already aborted request before work",
            "Abort before calling the custom operation.",
            "the exact reason is rejected; no timer starts.",
            r"""const controller = new AbortController();
const reason = new Error('already stopped');
controller.abort(reason);
const trace = [];
await assert.rejects(cancellableValue(7, controller.signal, trace), error => error === reason);
assert.deepEqual(trace, []);""",
            "The pre-check prevents side effects from beginning after cancellation was already known. It also handles an abort event that occurred before any listener was installed.",
        ),
        ex(
            "Complete normally and clean up once",
            "Run the custom operation without aborting, then abort its signal after completion.",
            "value 7; started,completed,cleaned exactly once.",
            r"""const controller = new AbortController();
const trace = [];
assert.equal(await cancellableValue(7, controller.signal, trace), 7);
controller.abort(new Error('too late'));
assert.deepEqual(trace, ['started', 'completed', 'cleaned']);""",
            "Completion removes the listener, so a later abort cannot mutate the finished operation's trace. A settled Promise alone would not remove an event listener.",
        ),
        ex(
            "Cancel custom work and release its timer",
            "Start the custom operation and immediately abort.",
            "rejected reason; started,aborted,cleaned.",
            r"""const controller = new AbortController();
const trace = [];
const reason = new Error('stop');
const pending = cancellableValue(7, controller.signal, trace);
controller.abort(reason);
await assert.rejects(pending, error => error === reason);
assert.deepEqual(trace, ['started', 'aborted', 'cleaned']);""",
            "The abort handler clears the actual timer before rejecting. This checks the owned operation's lifecycle rather than only the consumer's wait.",
        ),
        ex(
            "Keep the first abort reason",
            "Abort a controller twice and call throwIfAborted.",
            "the first reason remains authoritative.",
            r"""const controller = new AbortController();
const first = new Error('first');
controller.abort(first);
controller.abort(new Error('second'));
assert.equal(controller.signal.reason, first);
assert.throws(() => controller.signal.throwIfAborted(), error => error === first);""",
            "Abort state is a one-way transition. The first reason should be retained for diagnosis rather than overwritten by a later cleanup attempt.",
        ),
        ex(
            "Combine caller and deadline signals",
            "Combine two controllers and abort the deadline controller.",
            "combined signal is aborted with deadline reason.",
            r"""const caller = new AbortController();
const deadline = new AbortController();
const combined = AbortSignal.any([caller.signal, deadline.signal]);
const reason = new Error('deadline');
deadline.abort(reason);
assert.equal(combined.aborted, true);
assert.equal(combined.reason, reason);
assert.equal(caller.signal.aborted, false);""",
            "Combining signals observes either source without aborting the other controller. The example triggers the deadline explicitly to keep the test independent of scheduler speed.",
        ),
    ],
    helper="""function cancellableValue(value, signal, trace) {
  return new Promise((resolve, reject) => {
    if (signal.aborted) { reject(signal.reason); return; }
    trace.push('started');
    let timer;
    function cleanup() {
      clearTimeout(timer);
      signal.removeEventListener('abort', onAbort);
      trace.push('cleaned');
    }
    function onAbort() {
      trace.push('aborted');
      cleanup();
      reject(signal.reason);
    }
    signal.addEventListener('abort', onAbort, { once: true });
    timer = setTimeout(() => {
      trace.push('completed');
      cleanup();
      resolve(value);
    }, 1);
  });
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { setTimeout as delay } from 'node:timers/promises';",
    source=NODE + "globals.html",
)

add(
    14,
    """An algorithm is a rule for transforming an input into a result; complexity describes how its required work grows with input size. Counting comparisons on controlled inputs explains a growth claim better than a single timing measurement. Linear search may inspect every item. Binary search discards approximately half of a sorted interval at each step, requiring logarithmically many comparisons. Sorting or building an index also has a cost, so binary search is not automatically the best choice for one lookup in unsorted data.

This lesson implements lower_bound: the first position at which a target could be inserted without breaking sorted order. The half-open interval [low, high) always contains the answer. If values[mid] is less than the target, all positions through mid are too early, so low becomes mid+1. Otherwise high becomes mid. The interval shrinks on every iteration, preventing a duplicate value from trapping the loop.

A Map can index records by key when repeated lookups justify an extra structure. Duplicate-key policy must be explicit because silently overwriting records loses information. A binary min-heap supports repeated access to the smallest item without fully sorting every update. Its shape is an array-backed complete tree; the parent of index i is floor((i-1)/2), and children are 2i+1 and 2i+2. Restoring the parent-before-child invariant takes logarithmic height. Map performance guarantees are implementation dependent, so this lesson does not promise worst-case constant time for every lookup.""",
    """lowerBound returns an insertion position from 0 through length, including length when the target exceeds all values. Finding equality requires a separate comparison at that position. Heap push bubbles a new value toward its parent; pop moves the last value to the root and sinks it toward the smaller child. An empty heap returns undefined under this API. The algorithms assume finite numeric values and sorted search input; accepting NaN would break the ordering relation.""",
    [
        ("Complexity", "How operation count or storage grows with input size."),
        ("Search invariant", "A property keeping the possible answer inside a shrinking interval."),
        ("Index", "A structure trading construction and storage for later lookup convenience."),
        ("Heap invariant", "Every parent is no larger than either child in a min-heap."),
    ],
    [
        ex(
            "Trace lower bound with duplicates",
            "Find the first insertion position for 4 in 1,4,4,8 and inspect the visited intervals.",
            "index 1; intervals shrink to the first duplicate.",
            r"""const trace = [];
assert.equal(lowerBound([1, 4, 4, 8], 4, trace), 1);
assert.deepEqual(trace, [[0, 4, 2], [0, 2, 1], [0, 1, 0]]);""",
            "The equality branch moves high leftward rather than returning an arbitrary match. That is why lower bound finds the first duplicate and remains useful for insertion and range queries.",
        ),
        ex(
            "Use a heap for repeated minimum extraction",
            "Insert 5,1,3,1 and remove all values.",
            "pops 1,1,3,5, then undefined.",
            r"""const heap = new MinHeap();
for (const value of [5, 1, 3, 1]) heap.push(value);
assert.deepEqual([heap.pop(), heap.pop(), heap.pop(), heap.pop()], [1, 1, 3, 5]);
assert.equal(heap.pop(), undefined);""",
            "The heap maintains only the order needed at its root, not a fully sorted array. Equal priorities remain valid, but this numeric heap does not promise stable ordering among associated records.",
        ),
        ex(
            "Cover empty and outside search boundaries",
            "Search empty input, then targets below and above a sorted input.",
            "positions 0,0,3.",
            r"""assert.equal(lowerBound([], 4), 0);
assert.equal(lowerBound([2, 4, 6], 1), 0);
assert.equal(lowerBound([2, 4, 6], 9), 3);""",
            "Returning length is a valid insertion answer, not a valid array element. A caller must check position < length before testing equality.",
        ),
        ex(
            "Measure comparisons without a timing claim",
            "Search 1024 even integers for a missing value between two entries.",
            "insertion position 501 with no more than 11 comparisons.",
            r"""const values = Array.from({ length: 1024 }, (_, index) => index * 2);
const trace = [];
assert.equal(lowerBound(values, 1001, trace), 501);
assert.ok(trace.length <= 11);
assert.equal(values.includes(1001), false);""",
            "An operation count exposes logarithmic interval reduction independent of machine speed. It does not account for the cost of first sorting or materializing the input.",
        ),
        ex(
            "Reject duplicate index keys",
            "Build a Map keyed by id and reject repeated ids rather than silently replacing a row.",
            "valid lookup returns 7; duplicate id throws.",
            r"""const index = uniqueIndex([{ id: 'A', value: 7 }, { id: 'B', value: 9 }]);
assert.equal(index.get('A').value, 7);
assert.throws(() => uniqueIndex([{ id: 'A' }, { id: 'A' }]), /duplicate/u);""",
            "Index construction is a data-quality boundary. An overwritten record could make later lookup appear correct while silently dropping an input row.",
        ),
        ex(
            "Check the heap invariant after every update",
            "Push descending values and check each parent/child relation; reject NaN.",
            "all invariants hold; invalid value throws.",
            r"""const heap = new MinHeap();
for (const value of [6, 5, 4, 3, 2, 1]) {
  heap.push(value);
  for (let index = 1; index < heap.values.length; index += 1) {
    assert.ok(heap.values[Math.floor((index - 1) / 2)] <= heap.values[index]);
  }
}
assert.throws(() => heap.push(NaN), TypeError);""",
            "Inspecting the invariant catches a broken bubble-up implementation before it happens to return a wrong minimum. NaN lacks the total ordering this implementation requires.",
        ),
    ],
    helper="""function lowerBound(values, target, trace = []) {
  let low = 0;
  let high = values.length;
  while (low < high) {
    const middle = low + Math.floor((high - low) / 2);
    trace.push([low, high, middle]);
    if (values[middle] < target) low = middle + 1;
    else high = middle;
  }
  return low;
}
function uniqueIndex(rows) {
  const index = new Map();
  for (const row of rows) {
    if (index.has(row.id)) throw new Error(`duplicate id ${row.id}`);
    index.set(row.id, row);
  }
  return index;
}
class MinHeap {
  values = [];
  push(value) {
    if (!Number.isFinite(value)) throw new TypeError('finite value required');
    const values = this.values;
    values.push(value);
    let index = values.length - 1;
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (values[parent] <= values[index]) break;
      [values[parent], values[index]] = [values[index], values[parent]];
      index = parent;
    }
  }
  pop() {
    const values = this.values;
    if (values.length === 0) return undefined;
    const minimum = values[0];
    const last = values.pop();
    if (values.length === 0) return minimum;
    values[0] = last;
    let index = 0;
    while (2 * index + 1 < values.length) {
      let child = 2 * index + 1;
      if (child + 1 < values.length && values[child + 1] < values[child]) child += 1;
      if (values[index] <= values[child]) break;
      [values[index], values[child]] = [values[child], values[index]];
      index = child;
    }
    return minimum;
  }
}""",
    source="https://tc39.es/ecma262/multipage/keyed-collections.html",
    notes="""### Choosing the structure

For one lookup in ten unsorted rows, a linear scan is often clearest. For repeated lookups in stable sorted data, binary search avoids building another index. For keyed mutable records, a Map can simplify retrieval, provided updates keep the index consistent. For a scheduler that repeatedly removes the next smallest priority, a heap avoids sorting the entire queue after each insertion. Count both maintained structures and invalidation responsibilities when comparing designs. These examples are algorithm demonstrations, not microbenchmarks of a particular JavaScript engine.""",
)

add(
    15,
    """Tests make a behavioral claim executable. A useful test fails when a plausible implementation error is introduced. Merely calling a function without checking the result is weak evidence. Node supplies an assertion library and a built-in test runner, so this lesson needs no package installation. The runner discovers declared tests, awaits returned asynchronous work, reports failures, and sets a nonzero process exit status when a test fails.

A test should distinguish setup, action and observation. Fixtures should be small enough to explain the expected result independently. Check a normal case, an empty or boundary case, and a controlled failure. Avoid asserting incidental details such as an entire stack trace or machine-specific duration unless those details are themselves the contract. A failure message should name the behavior that broke.

Async tests must return or await their work. A Promise started and forgotten can outlive its test and create misleading results. Failure testing also needs the right assertion: throws inspects synchronous exceptions; rejects awaits a rejection. This lesson starts an actual node --test child for each exercise, preserving stdout and stderr separately and checking the child status. That proves the runner detected both deliberately passing and deliberately failing fixtures, instead of printing an invented test summary.""",
    """import test from node:test declares tests, while node:assert/strict provides exact assertions. test(name, async () => ...) awaits the returned Promise. assert.deepEqual compares structured values; assert.throws and assert.rejects check distinct failure channels. The child runner uses process.execPath, a fixed argument array and shell:false through spawnSync. A temporary source file belongs to the exercise and is removed in finally. A nonzero child result is expected only in the deliberately broken fixture.""",
    [
        ("Test oracle", "An independent expectation used to judge behavior."),
        ("Negative test", "A test asserting the intended handling of an invalid or failing case."),
        ("Regression", "A previously repaired behavior breaking again."),
        (
            "Async test lifetime",
            "The work the runner can observe through the returned or awaited Promise.",
        ),
    ],
    [
        ex(
            "Run a passing pure-function test",
            "Start a real node --test process asserting add(2,3)=5.",
            "child exit status 0; one passing test.",
            r"""const result = await runTests("test('addition', () => { assert.equal(2 + 3, 5); });");
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 1/u);""",
            "The child actually evaluates an assertion through the built-in runner. Process status supplies a machine-readable success signal; text is retained for diagnosis.",
        ),
        ex(
            "Prove a wrong result fails the runner",
            "Deliberately assert 2+3=6 in a child fixture.",
            "nonzero child exit; one failing test.",
            r"""const result = await runTests("test('deliberate regression', () => { assert.equal(2 + 3, 6); });");
assert.notEqual(result.status, 0);
assert.match(result.stdout, /# fail 1/u);
assert.match(result.stdout, /AssertionError/u);""",
            "A test suite that never fails cannot establish that its checks are connected. This controlled mutation proves that the assertion reaches the runner and influences the exit result.",
        ),
        ex(
            "Await an asynchronous test",
            "Declare an async test that awaits Promise resolution before checking the value.",
            "child exit status 0.",
            r"""const result = await runTests("test('awaited value', async () => { const value = await Promise.resolve(7); assert.equal(value, 7); });");
assert.equal(result.status, 0, result.stderr + result.stdout);""",
            "Returning the async function Promise gives the runner ownership of its lifetime. A detached Promise would need separate handling and could escape the intended observation window.",
        ),
        ex(
            "Check rejection with rejects",
            "Assert that an async operation rejects with a RangeError.",
            "child exit status 0.",
            r"""const result = await runTests("test('async boundary', async () => { await assert.rejects(async () => { throw new RangeError('negative'); }, RangeError); });");
assert.equal(result.status, 0, result.stderr + result.stdout);""",
            "An async function converts its thrown error into Promise rejection. assert.throws would inspect only the immediate call and therefore test the wrong channel.",
        ),
        ex(
            "Cover a table of boundary cases",
            "Use a table for sums of empty, singleton and signed arrays.",
            "three passing child tests.",
            r"""const body = `for (const [name, values, expected] of [['empty', [], 0], ['one', [4], 4], ['signed', [-2, 2], 0]]) {
  test(name, () => assert.equal(values.reduce((sum, value) => sum + value, 0), expected));
}`;
const result = await runTests(body);
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 3/u);""",
            "The cases share a mechanism but target different failure boundaries. An explicit reduction identity makes the empty case valid rather than silently excluding it from coverage.",
        ),
        ex(
            "Keep fixtures independent",
            "Create a fresh array inside each test and mutate it in only one test.",
            "two tests pass without shared mutable state.",
            r"""const result = await runTests("test('mutate local', () => { const rows = [1]; rows.push(2); assert.deepEqual(rows, [1,2]); });\ntest('fresh local', () => { const rows = [1]; assert.deepEqual(rows, [1]); });");
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 2/u);""",
            "A fresh fixture prevents one test from making another pass or fail through leftover state. Ordering assumptions often conceal a shared-state defect rather than a product requirement.",
        ),
    ],
    helper="""async function runTests(body) {
  const directory = await mkdtemp(join(tmpdir(), 'course-tests-'));
  try {
    const path = join(directory, 'fixture.test.mjs');
    await writeFile(path, "import test from 'node:test';\\nimport { strict as assert } from 'node:assert';\\n" + body, 'utf8');
    const result = spawnSync(process.execPath, ['--test', '--test-reporter=tap', path], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
    if (result.error) throw result.error;
    if (result.signal) throw new Error(`test process terminated by ${result.signal}`);
    return result;
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { mkdtemp, writeFile, rm } from 'node:fs/promises';\nimport { tmpdir } from 'node:os';\nimport { join } from 'node:path';\nimport { spawnSync } from 'node:child_process';",
    source=NODE + "test.html",
)

add(
    16,
    """A filesystem path names a resource in a host filesystem. Its interpretation is separate from a file URL and from the bytes stored in the file. Use path utilities rather than concatenating platform separators. A process working directory is mutable process state, so relative paths should have a deliberate base. This lesson owns only a newly created temporary directory and never overwrites a repository or learner file.

Text is encoded as bytes. UTF-8 characters can span multiple bytes, and a stream chunk can end in the middle of a character or a line. Splitting each raw chunk into lines independently can corrupt characters and split records. Node\'s stream decoder and readline interface preserve the needed partial state across chunks. We deliberately use two-byte chunks with a four-byte emoji to expose this boundary.

Reading a whole small file is straightforward. Streaming allows incremental processing, but memory still grows if the application pushes every record into a result array. A maximum byte or record policy must be enforced where data enters. The fixture has a tiny known size; its decoder and line framing are reusable mechanisms, not a claim of constant memory for arbitrary records. Filesystem errors retain codes such as ENOENT and EEXIST so callers can distinguish absence, exclusive-create conflicts and other failures.""",
    """mkdtemp allocates a unique directory under tmpdir. writeFile with flag wx rejects an existing file instead of replacing it. readFile with utf8 decodes text; without an encoding it returns bytes. createReadStream with encoding utf8 retains incomplete character sequences between chunks. createInterface with crlfDelay:Infinity treats CRLF consistently across chunks. for await consumes lines until completion, and finally closes both the interface and stream. Path containment based only on resolve does not defend against symlink races, so the lesson\'s lexical name check is scoped to files it creates itself.""",
    [
        ("Encoding", "The mapping between text characters and stored bytes."),
        (
            "Chunk boundary",
            "An arbitrary split in delivered bytes, independent of character or record boundaries.",
        ),
        ("Exclusive creation", "Creating a new file only if it does not already exist."),
        (
            "Resource lifetime",
            "The interval during which a file handle, stream or interface is owned.",
        ),
    ],
    [
        ex(
            "Read a small UTF-8 file",
            "Write one line containing an emoji, then compare text length and byte length.",
            "text round-trips; UTF-8 byte length exceeds code-unit length.",
            r"""await withDirectory(async directory => {
  const path = join(directory, 'message.txt');
  const text = 'A😀B\n';
  await writeFile(path, text, { encoding: 'utf8', flag: 'wx' });
  assert.equal(await readFile(path, 'utf8'), text);
  assert.equal((await readFile(path)).length, 7);
  assert.equal(text.length, 5);
});""",
            "The emoji occupies four UTF-8 bytes and two UTF-16 code units. Neither byte count nor JavaScript string length is a universal count of user-perceived characters.",
        ),
        ex(
            "Preserve characters and lines across chunks",
            "Stream two lines with a two-byte highWaterMark and decode using readline.",
            "lines are A😀B and second, without a corrupt replacement character.",
            r"""await withDirectory(async directory => {
  const path = join(directory, 'lines.txt');
  await writeFile(path, 'A😀B\r\nsecond\n', 'utf8');
  assert.deepEqual(await readLines(path), ['A😀B', 'second']);
});""",
            "The stream decoder retains incomplete UTF-8 sequences, while readline retains incomplete lines. Chunk size is not a record size or a guarantee about the bytes held by every layer.",
        ),
        ex(
            "Refuse accidental overwrite",
            "Create a file exclusively twice and inspect its unchanged content.",
            "second creation rejects with EEXIST; original first remains.",
            r"""await withDirectory(async directory => {
  const path = join(directory, 'owned.txt');
  await writeFile(path, 'first', { flag: 'wx' });
  await assert.rejects(writeFile(path, 'second', { flag: 'wx' }), error => error.code === 'EEXIST');
  assert.equal(await readFile(path, 'utf8'), 'first');
});""",
            "Checking existence before writing introduces a race. Exclusive creation combines the check and creation at the filesystem operation boundary.",
        ),
        ex(
            "Distinguish a missing file",
            "Read a path known not to exist in the fresh directory.",
            "ENOENT rejection.",
            r"""await withDirectory(async directory => {
  await assert.rejects(readFile(join(directory, 'missing.txt')), error => error.code === 'ENOENT');
});""",
            "A missing file can have an intentional application policy, but a catch-all empty result would also hide permission and I/O errors. Match the specific failure you intend to handle.",
        ),
        ex(
            "Restrict a learner-supplied fixture name",
            "Accept report.txt but reject traversal, separators and an absolute path.",
            "only report.txt is accepted.",
            r"""assert.equal(fixtureName('report.txt'), 'report.txt');
for (const name of ['../report.txt', '/tmp/report.txt', 'a/b.txt', 'a\\b.txt']) {
  assert.throws(() => fixtureName(name), TypeError);
}""",
            "This allowlist accepts a single simple filename, avoiding platform-dependent separator interpretation. It is deliberately narrower than a general path sanitizer and makes no symlink-security claim.",
        ),
        ex(
            "Handle an empty text stream",
            "Stream an empty file with the same decoder and line interface.",
            "no lines.",
            r"""await withDirectory(async directory => {
  const path = join(directory, 'empty.txt');
  await writeFile(path, '');
  assert.deepEqual(await readLines(path), []);
});""",
            "The absence of bytes means no records. Adding a fabricated empty line would change aggregation counts and confuse empty input with one empty record.",
        ),
    ],
    helper="""async function withDirectory(use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-files-'));
  try { return await use(directory); }
  finally { await rm(directory, { recursive: true, force: true }); }
}
async function readLines(path) {
  const input = createReadStream(path, { encoding: 'utf8', highWaterMark: 2 });
  const lines = createInterface({ input, crlfDelay: Infinity });
  const result = [];
  try { for await (const line of lines) result.push(line); }
  finally { lines.close(); input.destroy(); }
  return result;
}
function fixtureName(name) {
  if (typeof name !== 'string' || !/^[A-Za-z0-9_-]+\\.txt$/u.test(name)) throw new TypeError('simple .txt filename required');
  return name;
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';\nimport { createReadStream } from 'node:fs';\nimport { createInterface } from 'node:readline';\nimport { tmpdir } from 'node:os';\nimport { join } from 'node:path';",
    source=NODE + "fs.html",
)

add(
    17,
    """HTTP transfers representations between a client and a server using a method, target, headers, status and body. A successful TCP exchange is not the same as a successful application response. fetch resolves for HTTP error statuses such as 404; callers must inspect status or ok. Parsing JSON is another separate stage, and schema validation remains necessary after successful parsing.

A URL parser separates the path, query and origin using defined encoding rules. Constructing query strings by concatenating user text can change the meaning of characters such as ampersand or equals. URLSearchParams encodes values and supports repeated keys. Applications must decide whether repeated parameters are allowed, rejected or combined instead of silently choosing a surprising value.

This lesson runs a real local HTTP server on an ephemeral port bound only to 127.0.0.1. The server handles a tiny read-only sum endpoint. It validates the method, exact parameter multiplicity and safe integer domain before calculating. The client sends actual requests and reads actual responses. The fixture has no authentication, persistence, TLS, rate limiting or public deployment claim. Loopback-only binding and a tiny bounded response make it appropriate for learning the protocol boundary.""",
    """createServer receives request and response objects. Construct new URL(request.url, a known base) to parse the target. searchParams.getAll lets the handler check duplicate parameters. writeHead selects the status and content type; end finishes the body. server.listen(0, '127.0.0.1') asks the OS for an available local port. fetch uses AbortSignal.timeout as a waiting bound. In finally, closeAllConnections and close ensure the fixture releases its listener even if an assertion fails.""",
    [
        ("HTTP status", "The server's protocol-level result code."),
        ("Representation", "The bytes and media type describing a resource or result."),
        ("Query encoding", "Escaping values so delimiters retain their structural meaning."),
        (
            "Application validation",
            "Checking parsed values against the endpoint's domain contract.",
        ),
    ],
    [
        ex(
            "Request a valid local calculation",
            "GET /sum with a=2 and b=3 and inspect status, content type and JSON.",
            "status 200; application/json; total 5.",
            r"""await withServer(async base => {
  const response = await fetch(new URL('/sum?a=2&b=3', base), { signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /application\/json/u);
  assert.deepEqual(await response.json(), { total: 5 });
});""",
            "The checks distinguish transport completion, protocol success and representation content. An endpoint can respond successfully at one layer while violating another layer's contract.",
        ),
        ex(
            "Inspect an HTTP error without expecting fetch rejection",
            "Request an unknown route and inspect the actual response.",
            "fetch resolves; status 404, ok false, error not_found.",
            r"""await withServer(async base => {
  const response = await fetch(new URL('/missing', base), { signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 404);
  assert.equal(response.ok, false);
  assert.deepEqual(await response.json(), { error: 'not_found' });
});""",
            "fetch rejects for failures such as network errors or aborts, not simply because the server sent a 404. A client that only catches rejection may mistakenly treat a protocol error body as success data.",
        ),
        ex(
            "Encode query values through the URL API",
            "Round-trip a query containing spaces, ampersand and equals without contacting a server.",
            "the value round-trips as one parameter.",
            r"""const url = new URL('http://127.0.0.1/search');
url.searchParams.set('q', 'a & b=c');
assert.equal(url.searchParams.get('q'), 'a & b=c');
assert.equal([...url.searchParams].length, 1);
assert.ok(url.href.includes('%26'));""",
            "URLSearchParams preserves delimiters as data by encoding them. This is URL encoding, not HTML escaping or SQL parameter binding; each boundary has its own rules.",
        ),
        ex(
            "Reject repeated or invalid parameters",
            "Request repeated a values and a non-integer b value.",
            "both responses are 400 with invalid_parameters.",
            r"""await withServer(async base => {
  for (const path of ['/sum?a=1&a=2&b=3', '/sum?a=1&b=hello']) {
    const response = await fetch(new URL(path, base), { signal: AbortSignal.timeout(2000) });
    assert.equal(response.status, 400);
    assert.deepEqual(await response.json(), { error: 'invalid_parameters' });
  }
});""",
            "Checking getAll length prevents an ambiguous duplicate-parameter policy. The numeric parser rejects strings that JavaScript Number might otherwise coerce in unintended ways.",
        ),
        ex(
            "Reject an unsupported method",
            "POST to the read-only sum route without a body.",
            "status 405 and Allow: GET.",
            r"""await withServer(async base => {
  const response = await fetch(new URL('/sum?a=1&b=2', base), { method: 'POST', signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 405);
  assert.equal(response.headers.get('allow'), 'GET');
  assert.deepEqual(await response.json(), { error: 'method_not_allowed' });
});""",
            "A route includes method semantics, not just its path. Explicit method rejection prevents an accidental write-looking request from being accepted as an ordinary read.",
        ),
        ex(
            "Guard arithmetic overflow after parsing",
            "Add one to Number.MAX_SAFE_INTEGER through the endpoint.",
            "status 400 rather than a rounded success value.",
            r"""await withServer(async base => {
  const url = new URL('/sum', base);
  url.searchParams.set('a', String(Number.MAX_SAFE_INTEGER));
  url.searchParams.set('b', '1');
  const response = await fetch(url, { signal: AbortSignal.timeout(2000) });
  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), { error: 'unsafe_total' });
});""",
            "Each input can be a safe integer while the result is outside the safe range. Validate derived output invariants as well as input syntax.",
        ),
    ],
    helper="""function sendJson(response, status, body, extra = {}) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', ...extra });
  response.end(JSON.stringify(body));
}
function integerParameter(parameters, name) {
  const values = parameters.getAll(name);
  if (values.length !== 1 || !/^-?(0|[1-9][0-9]*)$/u.test(values[0])) return undefined;
  const value = Number(values[0]);
  return Number.isSafeInteger(value) ? value : undefined;
}
function handle(request, response) {
  const url = new URL(request.url, 'http://127.0.0.1');
  if (url.pathname !== '/sum') { sendJson(response, 404, { error: 'not_found' }); return; }
  if (request.method !== 'GET') { sendJson(response, 405, { error: 'method_not_allowed' }, { allow: 'GET' }); return; }
  const a = integerParameter(url.searchParams, 'a');
  const b = integerParameter(url.searchParams, 'b');
  if (a === undefined || b === undefined || [...url.searchParams.keys()].some(key => !['a', 'b'].includes(key))) {
    sendJson(response, 400, { error: 'invalid_parameters' }); return;
  }
  const total = a + b;
  if (!Number.isSafeInteger(total)) { sendJson(response, 400, { error: 'unsafe_total' }); return; }
  sendJson(response, 200, { total });
}
async function withServer(use) {
  const server = createServer(handle);
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  try {
    const address = server.address();
    if (address === null || typeof address === 'string') throw new Error('expected TCP listener');
    return await use(`http://127.0.0.1:${address.port}`);
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { createServer } from 'node:http';",
    source=NODE + "http.html",
)

add(
    18,
    """A reliable command-line program has an input contract, an output contract and a failure contract. Arguments select behavior, standard input supplies data, standard output carries machine-readable results, and standard error carries diagnostics. Exit status lets another process distinguish successful completion from invalid input or operational failure without parsing prose. Mixing a friendly banner into JSON stdout can break a downstream consumer even though a human finds the output readable.

The capstone is a small offline order aggregation tool. It accepts only --sum, reads bounded newline-delimited JSON from stdin, validates each row and rejects duplicate ids, then prints one JSON result. Blank lines are ignored under an explicit policy. Quantities and prices use safe integer units. It emits no partial aggregate on an invalid row, so a consumer cannot accidentally use an incomplete result as if it covered all input.

The reference launches the actual CLI as a fresh Node process with fixed arguments, bounded input, a timeout and separate stdout/stderr. All source files live in an owned temporary directory. Tests exercise successful totals, invalid arguments, malformed input, duplicates, empty input and the byte cap. This is a small single-process tool, not a general CSV parser, database transaction or production ingestion service. Later typed and streaming chapters extend the same separation of pure transformation and process I/O.""",
    """process.argv.slice(2) exposes user arguments after the executable and script paths. for await over process.stdin receives byte chunks. A byte budget is checked before retaining another chunk. Buffer.concat followed by UTF-8 decoding is appropriate only because this fixture enforces a small total input bound. Parsing attaches a one-based line number to validation errors. The program writes its JSON result only after every row passes, and sets process.exitCode on failure so pending diagnostic writes can finish.""",
    [
        ("CLI contract", "The documented arguments, input format, outputs and exit behavior."),
        ("NDJSON", "One independent JSON value per nonblank line under this fixture policy."),
        (
            "Failure atomicity",
            "No partial successful result is exposed when an input fails validation.",
        ),
        (
            "Process boundary",
            "The interface between a program and its caller through arguments, streams and exit status.",
        ),
    ],
    [
        ex(
            "Aggregate valid rows through a real child process",
            "Send two rows worth 250 and 300 cents to the CLI.",
            "exit 0; stdout is exactly one JSON result with 2 rows and 550 cents; stderr empty.",
            r"""const input = [{ id: 'A', quantity: 2, priceCents: 125 }, { id: 'B', quantity: 3, priceCents: 100 }].map(JSON.stringify).join('\n');
const result = await runCli(['--sum'], input);
assert.equal(result.status, 0, result.stderr);
assert.deepEqual(JSON.parse(result.stdout), { rows: 2, totalCents: 550 });
assert.equal(result.stderr, '');
assert.equal(result.stdout.trim().split('\n').length, 1);""",
            "The check uses the actual process contract, not a direct call to an internal aggregate function. Exact separation of result data and diagnostics makes the tool composable with another program.",
        ),
        ex(
            "Reject unknown arguments before consuming data",
            "Invoke the tool with --unknown.",
            "exit 2; stdout empty; stderr includes usage.",
            r"""const result = await runCli(['--unknown'], '');
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /usage/u);""",
            "A strict argument contract catches misspellings. Silently ignoring an unknown option can make a caller believe an important behavior was enabled when it was not.",
        ),
        ex(
            "Report the first invalid row without a partial result",
            "Send a valid first row and malformed JSON on line 2.",
            "exit 2; stdout empty; stderr identifies line 2.",
            r"""const result = await runCli(['--sum'], '{"id":"A","quantity":1,"priceCents":5}\n{broken');
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /line 2/u);""",
            "The first valid row does not authorize publishing a partial total. The output is committed only after validation of the whole bounded input.",
        ),
        ex(
            "Reject duplicate business identifiers",
            "Send two valid rows with the same id.",
            "exit 2 with duplicate id diagnostic.",
            r"""const row = JSON.stringify({ id: 'A', quantity: 1, priceCents: 5 });
const result = await runCli(['--sum'], row + '\n' + row);
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /duplicate id/u);""",
            "Syntactic and numeric validity do not establish uniqueness. A Set records the accepted ids and makes duplicate handling explicit instead of double counting by accident.",
        ),
        ex(
            "Define empty input deliberately",
            "Send whitespace and empty lines only.",
            "exit 0 with rows 0 and totalCents 0.",
            r"""const result = await runCli(['--sum'], '\n  \n');
assert.equal(result.status, 0, result.stderr);
assert.deepEqual(JSON.parse(result.stdout), { rows: 0, totalCents: 0 });""",
            "The empty aggregate follows from the additive identity and the declared blank-line policy. It is not a fallback applied to parse failures, which remain errors.",
        ),
        ex(
            "Enforce an input budget before retaining all data",
            "Send 4097 bytes to a CLI whose cap is 4096.",
            "exit 2 with input limit diagnostic; stdout empty.",
            r"""const result = await runCli(['--sum'], 'x'.repeat(4097));
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /input limit/u);""",
            "The budget is measured in bytes at the stream boundary, before concatenation. This caps the fixture input buffer; it does not claim a precise cap on all process memory.",
        ),
    ],
    helper=r"""const CLI_SOURCE = String.raw`
async function main() {
  if (process.argv.slice(2).join(' ') !== '--sum') throw new Error('usage: main.mjs --sum');
  const chunks = [];
  let bytes = 0;
  for await (const chunk of process.stdin) {
    bytes += chunk.length;
    if (bytes > 4096) throw new Error('input limit: 4096 bytes');
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString('utf8');
  const ids = new Set();
  let rows = 0;
  let totalCents = 0;
  for (const [index, line] of text.split(/\r?\n/u).entries()) {
    if (line.trim() === '') continue;
    try {
      const row = JSON.parse(line);
      if (row === null || typeof row !== 'object' || Array.isArray(row)) throw new Error('object required');
      if (Object.keys(row).sort().join(',') !== 'id,priceCents,quantity') throw new Error('exact schema required');
      if (typeof row.id !== 'string' || row.id === '') throw new Error('id required');
      if (!Number.isSafeInteger(row.quantity) || row.quantity <= 0 || !Number.isSafeInteger(row.priceCents) || row.priceCents < 0) throw new Error('invalid integer units');
      if (ids.has(row.id)) throw new Error('duplicate id');
      const contribution = row.quantity * row.priceCents;
      if (!Number.isSafeInteger(contribution) || !Number.isSafeInteger(totalCents + contribution)) throw new Error('unsafe total');
      ids.add(row.id);
      totalCents += contribution;
      rows += 1;
    } catch (error) {
      throw new Error('line ' + (index + 1) + ': ' + error.message, { cause: error });
    }
  }
  process.stdout.write(JSON.stringify({ rows, totalCents }) + '\n');
}
main().catch(error => { process.stderr.write(error.message + '\n'); process.exitCode = 2; });
`;
async function runCli(args, input) {
  const directory = await mkdtemp(join(tmpdir(), 'course-cli-'));
  try {
    const path = join(directory, 'main.mjs');
    await writeFile(path, CLI_SOURCE, 'utf8');
    const result = spawnSync(process.execPath, [path, ...args], { input, encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
    if (result.error) throw result.error;
    if (result.signal) throw new Error(`CLI terminated by ${result.signal}`);
    return result;
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}""",
    imports="import { strict as assert } from 'node:assert';\nimport { mkdtemp, writeFile, rm } from 'node:fs/promises';\nimport { tmpdir } from 'node:os';\nimport { join } from 'node:path';\nimport { spawnSync } from 'node:child_process';",
    source=NODE + "process.html",
)
