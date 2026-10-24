from render import add, ex

NODE = "https://nodejs.org/download/release/v24.11.0/docs/api/"

add(
    32,
    """A stream transports chunks incrementally between a producer and a consumer. Chunks are not necessarily logical records, and reading incrementally does not guarantee bounded memory if the application stores every chunk. Backpressure communicates that a consumer has enough queued work and the producer should pause. Ignoring that signal can turn a fast producer and slow consumer into an ever-growing buffer.

Writable.write returns a Boolean indicating whether the producer should continue. A false return does not mean the chunk was rejected; it was accepted into the writable machinery, but the producer should wait for drain before supplying more. highWaterMark is a buffering threshold, not a hard cap on total process memory. In byte mode the relevant accounting is bytes; in object mode it counts objects, regardless of how large each object\'s reachable data is.

pipeline connects stages, forwards errors and coordinates teardown. A transform must call its callback exactly once per chunk, with either an error or transformed output. Calling it twice or never calling it breaks progress. An error after some output has been consumed does not roll those effects back. A pipeline writing an external destination needs an explicit transactional or temporary-output strategy if partial results must not become visible.

Cancellation also needs cooperation from asynchronous generators or other work outside the stream\'s immediate buffer. Passing the same signal to an awaited operation lets that work stop rather than keeping a generator suspended after the pipeline has been aborted. These examples use tiny chunks and controlled gates to prove lifecycle behavior without relying on a timing benchmark.""",
    """Readable.from adapts an iterable. Transform receives chunks through transform(chunk, encoding, callback). Writable owns each write until its callback signals completion. The promise-based pipeline resolves only after completion or rejects on failure. Install the drain listener before releasing a controlled write callback so the event cannot be missed. finished observes stream completion after end. Object mode deliberately changes the unit of highWaterMark.""",
    [
        (
            "Backpressure",
            "A signal that the producer should pause because the consumer has queued enough work.",
        ),
        ("High-water mark", "A buffering threshold, not a universal memory cap."),
        ("Pipeline", "Connected stages with coordinated completion and error handling."),
        ("Partial output", "Results already consumed before a later failure occurs."),
    ],
    [
        ex(
            "Run an actual transform pipeline",
            "Uppercase two byte chunks and collect the transformed output.",
            "ABCD after successful pipeline completion.",
            r"""const output = [];
const upper = new Transform({ transform(chunk, encoding, callback) { callback(null, chunk.toString('utf8').toUpperCase()); } });
const sink = new Writable({ write(chunk, encoding, callback) { output.push(chunk.toString()); callback(); } });
await pipeline(Readable.from(['ab', 'cd']), upper, sink);
assert.equal(output.join(''), 'ABCD');
assert.equal(sink.writableFinished, true);""",
            "The result is observed after pipeline resolves, so every stage has completed. A print before awaiting completion could report an incomplete collection.",
        ),
        ex(
            "Observe false write and drain without guessing timing",
            "Hold a write callback at a two-byte threshold, inspect write(), then release it.",
            "write returns false; drain follows release; stream finishes.",
            r"""let release;
const sink = new Writable({ highWaterMark: 2, write(chunk, encoding, callback) { release = callback; } });
assert.equal(sink.write(Buffer.from('ab')), false);
assert.equal(sink.writableNeedDrain, true);
const drained = once(sink, 'drain');
release();
await drained;
sink.end();
await finished(sink);""",
            "False means pause, not retry the same chunk. Retrying it would duplicate data because the original write was already accepted.",
        ),
        ex(
            "Propagate a producer failure and destroy the sink",
            "Use an async source that yields once then throws.",
            "pipeline rejects with source failed; sink is destroyed.",
            r"""async function* source() { yield 'first'; throw new Error('source failed'); }
const sink = new Writable({ write(chunk, encoding, callback) { callback(); } });
await assert.rejects(pipeline(Readable.from(source()), sink), /source failed/u);
assert.equal(sink.destroyed, true);""",
            "A failure may occur after earlier chunks reached the destination. Destruction releases resources but does not undo side effects the consumer already performed.",
        ),
        ex(
            "Reject an invalid object in a transform",
            "Process numeric objects but reject a negative value through the callback.",
            "pipeline rejects with RangeError.",
            r"""const checked = new Transform({ objectMode: true, transform(value, encoding, callback) {
  if (value < 0) callback(new RangeError('negative item'));
  else callback(null, value * 2);
} });
const sink = new Writable({ objectMode: true, write(value, encoding, callback) { callback(); } });
await assert.rejects(pipeline(Readable.from([1, -1]), checked, sink), RangeError);""",
            "The transform reports the error through its callback exactly once. Throwing from an unrelated later callback or hiding the error would break pipeline's error contract.",
        ),
        ex(
            "Measure an object-mode threshold in objects",
            "Write one large-payload object to a writable with object-mode highWaterMark 1.",
            "write false and writableLength 1, irrespective of payload string length.",
            r"""let release;
const sink = new Writable({ objectMode: true, highWaterMark: 1, write(value, encoding, callback) { release = callback; } });
assert.equal(sink.write({ payload: 'x'.repeat(1000) }), false);
assert.equal(sink.writableLength, 1);
const drained = once(sink, 'drain');
release();
await drained;
sink.end();
await finished(sink);""",
            "One object can retain a large graph. An object count threshold does not establish a byte-memory budget for arbitrary payloads.",
        ),
        ex(
            "Abort a generator and its awaited timer",
            "Start a source, await its readiness signal, then abort the shared signal.",
            "pipeline rejects with AbortError; generator finally runs.",
            r"""const controller = new AbortController();
let announce;
const ready = new Promise(resolve => { announce = resolve; });
let closed = false;
async function* source() {
  try { announce(); await delay(1000, undefined, { signal: controller.signal }); yield 'late'; }
  finally { closed = true; }
}
const sink = new Writable({ write(chunk, encoding, callback) { callback(); } });
const pending = pipeline(Readable.from(source()), sink, { signal: controller.signal });
await ready;
controller.abort();
await assert.rejects(pending, error => error.name === 'AbortError');
assert.equal(closed, true);""",
            "The timer observes the same cancellation signal as the pipeline. Aborting only the outer wait could leave the generator's underlying operation alive.",
        ),
    ],
    imports="""import { strict as assert } from 'node:assert';
import { Readable, Transform, Writable } from 'node:stream';
import { pipeline, finished } from 'node:stream/promises';
import { once } from 'node:events';
import { setTimeout as delay } from 'node:timers/promises';""",
    source=NODE + "stream.html",
)

add(
    33,
    """An async function does not automatically move CPU work off the main JavaScript thread. A long synchronous loop inside an async function still blocks that thread until it yields or completes. Worker threads provide separate JavaScript execution contexts for CPU work. They are useful when the computation is large enough to justify startup, messaging and coordination costs. They do not make ordinary asynchronous file or network I/O inherently faster.

Messages normally use structured cloning. The receiver obtains its own copy of supported values, so mutating a received object does not change the sender\'s original object. Some values, such as functions, cannot be cloned. A transfer list can instead move ownership of an ArrayBuffer: the sender\'s buffer is detached, and the receiver gains access to its bytes. Transfer is an ownership change, not a shared mutable alias. SharedArrayBuffer has different synchronization requirements and is not used here.

A worker\'s lifecycle includes message, error and exit events. Receiving a result is not by itself proof that a worker has stopped. The helper terminates its owned worker in finally and applies a waiting timeout. A worker that exits without producing a result is a failure under this helper\'s contract. The examples use small fixed authored worker programs; eval:true is used only to keep those trusted fixtures self-contained. It must not be supplied with untrusted source text.

Workers share a process-level trust context and available host capabilities. They are not a security sandbox for arbitrary hostile JavaScript. Resource limits constrain selected V8 resources, not every possible process or external allocation. These tests establish actual thread messaging, ownership and teardown, not a speedup claim.""",
    """new Worker creates the thread. workerData supplies a cloned or transferred initial payload. parentPort sends the result to the parent. A transferList names the exact ArrayBuffer ownership to move. Parent code listens for result, error and premature exit, then cleans up listeners and terminates the worker. Use process and thread identifiers only as observations of the actual run, not as fixed expected numbers.""",
    [
        ("Worker thread", "A separate JavaScript execution context for concurrent work."),
        ("Structured clone", "Copying supported data across a message boundary."),
        ("Transfer", "Moving ownership of a transferable object and detaching the sender view."),
        ("Worker lifecycle", "Startup, messaging, errors, completion and termination ownership."),
    ],
    [
        ex(
            "Perform bounded CPU work in a real worker",
            "Sum integers 1 through 10000 in a worker and inspect its thread id.",
            "sum 50005000; worker thread id positive.",
            r"""const result = await runWorker(`const { parentPort, workerData, threadId } = require('node:worker_threads');
let sum = 0; for (let value = 1; value <= workerData; value += 1) sum += value;
parentPort.postMessage({ sum, threadId });`, 10000);
assert.equal(result.sum, 50005000);
assert.ok(result.threadId > 0);""",
            "The result came through an actual worker message. The tiny workload illustrates mechanics and may be slower than a direct loop because startup costs dominate.",
        ),
        ex(
            "Transfer a buffer and observe detachment",
            "Send an ArrayBuffer by transfer list, modify its first byte in the worker and return the bytes.",
            "parent byteLength 0; returned bytes 9,2,3.",
            r"""const buffer = Uint8Array.from([1, 2, 3]).buffer;
const result = await runWorker(`const { parentPort, workerData } = require('node:worker_threads');
const bytes = new Uint8Array(workerData); bytes[0] = 9; parentPort.postMessage([...bytes]);`, buffer, [buffer]);
assert.equal(buffer.byteLength, 0);
assert.deepEqual(result, [9, 2, 3]);""",
            "The sender loses access because ownership moved. Treating a detached buffer as still usable would create an invalid lifetime assumption.",
        ),
        ex(
            "Distinguish cloning from shared mutation",
            "Send an object, mutate the worker copy and compare the original.",
            "worker returns 9; parent remains 1.",
            r"""const original = { value: 1 };
const result = await runWorker(`const { parentPort, workerData } = require('node:worker_threads');
workerData.value = 9; parentPort.postMessage(workerData.value);`, original);
assert.equal(result, 9);
assert.equal(original.value, 1);""",
            "Ordinary message data is cloned. This prevents accidental aliasing but can add copying cost for large payloads.",
        ),
        ex(
            "Propagate an actual worker exception",
            "Run an authored worker that throws a fixture error.",
            "parent Promise rejects with worker fixture failed.",
            r"""await assert.rejects(runWorker(`throw new Error('worker fixture failed');`, null), /worker fixture failed/u);""",
            "Worker exceptions arrive through the error event. A parent that listens only for messages could wait forever for a result that cannot arrive.",
        ),
        ex(
            "Terminate an owned worker that remains alive",
            "Start a worker that reports ready and keeps an interval open, then terminate it.",
            "ready observed; terminate resolves with an exit code.",
            r"""const worker = new Worker(`const { parentPort } = require('node:worker_threads'); setInterval(() => {}, 1000); parentPort.postMessage('ready');`, { eval: true });
try {
  assert.equal(await new Promise((resolve, reject) => { worker.once('message', resolve); worker.once('error', reject); }), 'ready');
} finally {
  const code = await worker.terminate();
  assert.equal(typeof code, 'number');
}""",
            "A ready message does not close active handles. Explicit termination releases the owned worker and its interval; the test does not leave background work running.",
        ),
        ex(
            "Reject data that cannot be cloned",
            "Try to pass a function through workerData.",
            "DataCloneError before useful worker execution.",
            r"""await assert.rejects(runWorker(`const { parentPort } = require('node:worker_threads'); parentPort.postMessage('unused');`, { callback: () => 1 }), error => error.name === 'DataCloneError');""",
            "Functions carry executable behavior and closure state, not supported cloneable message data. Define a data protocol and keep worker implementation separate.",
        ),
    ],
    helper="""async function runWorker(source, data, transferList = []) {
  const worker = new Worker(source, { eval: true, workerData: data, transferList, resourceLimits: { maxOldGenerationSizeMb: 32 } });
  let timer;
  try {
    return await new Promise((resolve, reject) => {
      timer = setTimeout(() => reject(new Error('worker result timeout')), 10000);
      worker.once('message', resolve);
      worker.once('error', reject);
      worker.once('exit', code => reject(new Error(`worker exited without a result: ${code}`)));
    });
  } finally {
    clearTimeout(timer);
    await worker.terminate();
  }
}""",
    imports="""import { strict as assert } from 'node:assert';
import { Worker } from 'node:worker_threads';""",
    source=NODE + "worker_threads.html",
)

add(
    34,
    """Performance measurement begins with a correctness contract and a question. A faster implementation that computes a different answer is not an improvement. Wall-clock duration includes scheduling, warmup, JIT compilation, garbage collection and surrounding system load. A single tiny measurement cannot establish a robust speed ranking. Use repeated observations, representative inputs and clearly defined boundaries; retain raw samples instead of reporting only an attractive minimum.

performance.now provides a monotonic clock suitable for elapsed intervals. Date.now measures wall-clock time and can change when the system clock is adjusted. Named marks and measures help identify phases, but their entries also occupy a timeline until cleared. A library should clear only the marks it owns, not another component\'s measurements.

Memory counters describe different domains. heapUsed concerns managed JavaScript heap use, external and arrayBuffers describe other tracked allocations, and rss concerns resident process memory. Clearing a Map removes its references but does not guarantee immediate garbage collection or a visible drop in rss. A retained-reference count can prove an ownership change without pretending it measures reclaimed physical memory.

Event-loop utilization and delay measure related but distinct behavior. Utilization estimates active versus idle event-loop time under its API definition; delay measures how late scheduled monitoring callbacks run. Neither directly states CPU usage for every worker or the cause of a stall. This lesson records bounded real observations and asserts their shape and validity, not platform-specific performance thresholds. Profiling is a separate investigation after a reproducible workload identifies the problem.""",
    """Measure a known-correct function using start/end performance.now values. Summarize repeated samples with a declared statistic such as median while preserving all samples. process.memoryUsage returns byte counters that should not be subtracted indiscriminately as independent categories. performance.mark and measure use unique names and finally cleanup. monitorEventLoopDelay must be enabled and later disabled; a short or heavily delayed run may have too few samples, which is an evidence limit rather than a reason to invent a result.""",
    [
        ("Measurement boundary", "The exact work included in a recorded interval."),
        ("Monotonic clock", "A clock suited to elapsed time without wall-clock adjustments."),
        ("Retention", "References that keep objects reachable."),
        ("Event-loop delay", "Observed lateness in scheduled loop activity."),
    ],
    [
        ex(
            "Measure only a checked computation",
            "Sum a fixed numeric range and record elapsed duration.",
            "correct sum 50005000; finite nonnegative elapsed time.",
            r"""const start = performance.now();
const result = sumTo(10000);
const elapsed = performance.now() - start;
assert.equal(result, 50005000);
assert.ok(Number.isFinite(elapsed) && elapsed >= 0);
console.log(JSON.stringify({ operation: 'sumTo10000', elapsedMs: elapsed }));""",
            "Correctness is checked independently of the measured time. No assertion says the operation must be faster than a machine-dependent threshold.",
        ),
        ex(
            "Preserve repeated samples and summarize them",
            "Measure five checked runs and compute their median.",
            "five finite samples; median lies between minimum and maximum.",
            r"""const samples = [];
for (let trial = 0; trial < 5; trial += 1) {
  const start = performance.now();
  assert.equal(sumTo(1000), 500500);
  samples.push(performance.now() - start);
}
const sorted = [...samples].sort((a, b) => a - b);
const median = sorted[2];
assert.equal(samples.length, 5);
assert.ok(samples.every(value => Number.isFinite(value) && value >= 0));
assert.ok(median >= sorted[0] && median <= sorted[4]);
console.log(JSON.stringify({ samplesMs: samples, medianMs: median }));""",
            "Five tiny trials illustrate record keeping, not a statistically robust benchmark. A real comparison needs workload control, enough repetitions and an analysis of variability.",
        ),
        ex(
            "Release owned references without claiming immediate RSS change",
            "Populate and clear a Map while recording memory counters.",
            "entry count 100 then 0; valid counters, with no asserted memory drop.",
            r"""const cache = new Map();
for (let index = 0; index < 100; index += 1) cache.set(index, { payload: 'x'.repeat(100) });
assert.equal(cache.size, 100);
const before = process.memoryUsage();
cache.clear();
assert.equal(cache.size, 0);
const after = process.memoryUsage();
assert.ok(before.heapUsed > 0 && after.rss > 0);
console.log(JSON.stringify({ before, after, retainedEntries: cache.size }));""",
            "The ownership claim is directly observed through the collection size. Physical memory reclamation depends on garbage collection and allocator behavior outside this deterministic check.",
        ),
        ex(
            "Use and clear only owned performance entries",
            "Create named marks and one measure around a checked operation.",
            "one nonnegative duration; owned entries removed afterward.",
            r"""const prefix = 'course-js034-owned';
try {
  performance.mark(prefix + '-start');
  assert.equal(sumTo(10), 55);
  performance.mark(prefix + '-end');
  performance.measure(prefix, prefix + '-start', prefix + '-end');
  const entries = performance.getEntriesByName(prefix, 'measure');
  assert.equal(entries.length, 1);
  assert.ok(entries[0].duration >= 0);
} finally {
  performance.clearMarks(prefix + '-start');
  performance.clearMarks(prefix + '-end');
  performance.clearMeasures(prefix);
}
assert.equal(performance.getEntriesByName(prefix).length, 0);""",
            "Measurement infrastructure has state too. Scoped cleanup prevents this lesson from deleting unrelated entries or retaining its own indefinitely.",
        ),
        ex(
            "Inspect event-loop utilization as a bounded observation",
            "Take a baseline, yield through a timer, then inspect the interval delta.",
            "finite utilization between 0 and 1; no speed or CPU-percentage claim.",
            r"""const baseline = performance.eventLoopUtilization();
await delay(5);
const observed = performance.eventLoopUtilization(baseline);
assert.ok(Number.isFinite(observed.utilization));
assert.ok(observed.utilization >= 0 && observed.utilization <= 1);
console.log(JSON.stringify({ eventLoop: observed }));""",
            "The interval includes the explicit wait. A low value here says little about a production workload, other processes or worker-thread CPU consumption.",
        ),
        ex(
            "Enable and disable a real delay monitor",
            "Collect a short delay-monitor interval and report whether samples exist.",
            "monitor disabled afterward; sample count reported honestly.",
            r"""const histogram = monitorEventLoopDelay({ resolution: 10 });
histogram.enable();
try {
  await delay(35);
  const count = Number(histogram.count);
  assert.ok(Number.isInteger(count) && count >= 0);
  if (count > 0) assert.ok(Number.isFinite(histogram.mean));
  console.log(JSON.stringify({ samples: count, meanMs: count > 0 ? histogram.mean / 1e6 : null }));
} finally { histogram.disable(); }""",
            "The monitor reports nanoseconds, so the conversion to milliseconds is explicit. Zero samples remain an honest insufficient-observation result, not a fabricated zero delay.",
        ),
    ],
    helper="""function sumTo(length) {
  let total = 0;
  for (let value = 1; value <= length; value += 1) total += value;
  return total;
}""",
    imports="""import { strict as assert } from 'node:assert';
import { performance, monitorEventLoopDelay } from 'node:perf_hooks';
import { setTimeout as delay } from 'node:timers/promises';""",
    source=NODE + "perf_hooks.html",
)

add(
    35,
    """A date-time problem can involve an instant, a calendar date, a local clock reading or a duration. These are different concepts. JavaScript Date primarily represents a millisecond offset from the Unix epoch. Its display can use a timezone, but the object does not retain an original timezone label. Two ISO strings with different offsets can identify the same instant. A business date such as a billing day may need a separate calendar-date representation rather than an invented midnight instant.

Parsing is part of the contract. Accepting arbitrary date text lets implementation and locale assumptions enter the program. This lesson accepts an explicit YYYY-MM-DD format for calendar dates and verifies that the constructed UTC date round-trips to the same components. That rejects impossible dates that a permissive construction could normalize into another month. Invalid Date is still a Date object, so instanceof alone does not establish a valid timestamp.

Timezones map instants to local civil times. During a spring daylight-saving transition, some local clock readings do not occur. During a fall transition, the same local reading can correspond to two different instants. Adding 24 elapsed hours is not always the same as advancing a local calendar day at the same wall-clock time. The fixtures use specified UTC instants and named America/New_York rules, avoiding dependence on the host\'s default timezone.

Intl formats values according to an explicit locale and timezone. Prefer formatToParts when inspecting semantic fields rather than assuming punctuation, spacing or ordering. Formatting is not general parsing. Calendar and locale data can change across runtime versions; report the prepared runtime and avoid inferring a universal parser from one formatted string.""",
    """Date.parse on an ISO string with Z or an explicit offset produces an instant. toISOString produces UTC text. Number.isFinite(date.getTime()) checks timestamp validity. Intl.DateTimeFormat accepts timeZone and hourCycle explicitly; formatToParts returns named fields. Intl.NumberFormat separates display conventions from numeric storage. Integer cents should remain integer cents while formatting a display value under a declared currency and rounding policy.""",
    [
        ("Instant", "A specific point on the timeline."),
        ("Calendar date", "A year-month-day value without an implied instant."),
        ("Timezone", "Rules mapping instants to local calendar and clock fields."),
        ("Locale formatting", "Displaying values under language and regional conventions."),
    ],
    [
        ex(
            "Compare offset spellings of one instant",
            "Parse UTC midnight and the equivalent previous-day offset representation.",
            "equal timestamps and UTC ISO output.",
            r"""const utc = new Date('2024-01-01T00:00:00Z');
const offset = new Date('2023-12-31T19:00:00-05:00');
assert.equal(utc.getTime(), offset.getTime());
assert.equal(offset.toISOString(), '2024-01-01T00:00:00.000Z');""",
            "The offset changes the written clock reading, not the represented instant. Date does not preserve the original -05:00 label as part of its identity.",
        ),
        ex(
            "Observe a spring-forward clock gap",
            "Format two instants one hour apart across the New York spring transition.",
            "local hour changes from 01 to 03 while elapsed time is one hour.",
            r"""const before = new Date('2024-03-10T06:30:00Z');
const after = new Date('2024-03-10T07:30:00Z');
assert.equal(parts(before).hour, '01');
assert.equal(parts(after).hour, '03');
assert.equal(after.getTime() - before.getTime(), 60 * 60 * 1000);""",
            "The timeline remains continuous while local civil labels skip an hour. A local scheduling problem must account for this mapping rather than assuming every day contains every clock reading.",
        ),
        ex(
            "Reject impossible or ambiguous calendar text",
            "Accept leap-day 2024-02-29 and reject 2023-02-29, slash format and month 13.",
            "only the valid strict date is accepted.",
            r"""assert.equal(calendarDate('2024-02-29'), '2024-02-29');
for (const text of ['2023-02-29', '01/02/2024', '2024-13-01']) assert.throws(() => calendarDate(text), RangeError);""",
            "A round-trip component check catches normalization of impossible dates. A strict grammar avoids choosing a day/month interpretation from host locale.",
        ),
        ex(
            "Distinguish repeated fall-back clock readings",
            "Format two instants on either side of the fall transition.",
            "both read 01:30 locally but offsets differ and timestamps are one hour apart.",
            r"""const first = new Date('2024-11-03T05:30:00Z');
const second = new Date('2024-11-03T06:30:00Z');
assert.equal(parts(first).hour, '01');
assert.equal(parts(second).hour, '01');
assert.equal(parts(first).minute, parts(second).minute);
assert.notEqual(parts(first).timeZoneName, parts(second).timeZoneName);
assert.equal(second.getTime() - first.getTime(), 3600000);""",
            "A local clock label without an offset or disambiguation policy may not identify one instant. Persisting only that label loses information.",
        ),
        ex(
            "Inspect locale number parts without parsing display text",
            "Format 1234.5 in US English and German and inspect their decimal separators.",
            "decimal dot versus comma; numeric value remains unchanged.",
            r"""const value = 1234.5;
const us = new Intl.NumberFormat('en-US').formatToParts(value);
const de = new Intl.NumberFormat('de-DE').formatToParts(value);
assert.equal(us.find(part => part.type === 'decimal').value, '.');
assert.equal(de.find(part => part.type === 'decimal').value, ',');
assert.equal(value, 1234.5);""",
            "The formatter changes presentation, not the stored number. Removing punctuation from a localized string is not a reliable general numeric parser.",
        ),
        ex(
            "Reject invalid timestamp and timezone assumptions",
            "Inspect Invalid Date and request a nonexistent timezone.",
            "NaN timestamp; toISOString and invalid timezone construction throw RangeError.",
            r"""const invalid = new Date('not an ISO instant');
assert.equal(Number.isNaN(invalid.getTime()), true);
assert.throws(() => invalid.toISOString(), RangeError);
assert.throws(() => new Intl.DateTimeFormat('en-US', { timeZone: 'Invalid/Nowhere' }), RangeError);""",
            "Being a Date instance does not imply timestamp validity. Unsupported timezone configuration should be diagnosed explicitly rather than silently falling back to the host default.",
        ),
    ],
    helper="""function parts(date) {
  const formatter = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hourCycle: 'h23', timeZoneName: 'longOffset' });
  return Object.fromEntries(formatter.formatToParts(date).map(part => [part.type, part.value]));
}
function calendarDate(text) {
  if (typeof text !== 'string' || !/^\\d{4}-\\d{2}-\\d{2}$/u.test(text)) throw new RangeError('YYYY-MM-DD required');
  const date = new Date(text + 'T00:00:00.000Z');
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== text) throw new RangeError('invalid calendar date');
  return text;
}""",
    source=NODE + "intl.html",
)

add(
    36,
    """A package is a public interface plus the files and metadata needed to implement it. The exports map declares supported entry points. Consumers importing an undeclared internal path receive a loader error, even if a file exists on disk. This helps maintain an API boundary but is not filesystem access control for a hostile process with direct disk access.

A package version and an engine declaration communicate compatibility expectations. They do not prove the implementation obeys semantic-versioning conventions, and Node\'s module loader does not automatically enforce every package engines field. A tested runtime contract must check the actual executable and supported behavior. A breaking change can be behavioral even if TypeScript signatures or exported function names remain unchanged.

Reproducible preparation needs more than a top-level version range. Lockfiles record resolved dependency versions and integrity information; the package manager version, platform-specific dependencies, runtime, installation flags and build inputs can still matter. npm ci is the usual strict lockfile installation route, but this default lesson does not install dependencies or run lifecycle scripts. Its fixtures are small authored packages under an owned temporary node_modules directory so resolution can be observed offline.

The examples create a public entry, an explicit subpath and a private implementation file, then run real Node imports. A SHA-256 manifest demonstrates content identity and detects an intentional local modification. A hash proves equality to an expected byte sequence, not trustworthiness, licensing or correctness. Keep source identity, dependency resolution and runtime behavior as separate pieces of release evidence.""",
    """package.json type:module selects ESM for .js files in its package scope, while .mjs is explicit independently. exports maps package entry and subpath names to intended files. Bare package imports resolve from the importing module\'s location. A child main.mjs in the temporary project imports the authored package through node_modules, exercising the real loader. The helper captures exit status and stderr, cleans up its directory and never runs a shell or package installation.""",
    [
        ("Exports map", "The declared package entry and subpath interface."),
        ("Dependency lock", "A record of resolved dependency artifacts and metadata."),
        ("Engine declaration", "Package metadata describing an intended runtime requirement."),
        ("Content identity", "A digest tying evidence to exact file bytes."),
    ],
    [
        ex(
            "Import the public package entry",
            "Create a package with exports pointing at index.mjs and import its version value.",
            "actual child prints 1.",
            r"""await withPackage(async directory => {
  const result = runImport(directory, 'import { version } from \'course-fixture\'; console.log(version);');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '1');
});""",
            "The import uses normal package-name resolution from the temporary main module. It does not bypass the exports map with an absolute file URL.",
        ),
        ex(
            "Use an explicitly exported subpath",
            "Import twice from course-fixture/math.",
            "actual child prints 6.",
            r"""await withPackage(async directory => {
  const result = runImport(directory, 'import { twice } from \'course-fixture/math\'; console.log(twice(3));');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '6');
});""",
            "A public subpath is part of the package interface. Its name can remain stable even if the internal file layout later changes.",
        ),
        ex(
            "Reject an undeclared private path",
            "Attempt a package-name import of private.mjs even though the file exists.",
            "nonzero child status with ERR_PACKAGE_PATH_NOT_EXPORTED.",
            r"""await withPackage(async directory => {
  const result = runImport(directory, 'import \'course-fixture/private.mjs\';');
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /ERR_PACKAGE_PATH_NOT_EXPORTED/u);
});""",
            "The loader enforces the declared package interface. A consumer depending on internal paths would otherwise make ordinary package refactoring a compatibility hazard.",
        ),
        ex(
            "Observe that engines is metadata rather than a loader gate",
            "Read the fixture engine declaration requiring Node99, then import its entry with the actual runtime.",
            "metadata says >=99; ordinary import still succeeds.",
            r"""await withPackage(async directory => {
  const manifest = JSON.parse(await readFile(join(directory, 'node_modules/course-fixture/package.json'), 'utf8'));
  assert.equal(manifest.engines.node, '>=99');
  assert.ok(Number(process.versions.node.split('.')[0]) < 99);
  assert.equal(runImport(directory, 'import \'course-fixture\';').status, 0);
});""",
            "Package-manager policy may warn or reject based on configuration, but this demonstrates the actual Node loader boundary. A declared requirement is not runtime qualification.",
        ),
        ex(
            "Detect exact source tampering through a digest",
            "Hash the public source, change only that owned file, and compare hashes.",
            "digest changes after modification.",
            r"""await withPackage(async directory => {
  const path = join(directory, 'node_modules/course-fixture/index.mjs');
  const before = digest(await readFile(path));
  await writeFile(path, 'export const version = 2;');
  const after = digest(await readFile(path));
  assert.notEqual(after, before);
  assert.equal(before.length, 64);
});""",
            "The digest identifies bytes, so even a valid replacement implementation changes artifact identity. It does not tell whether version 1 or version 2 has better behavior.",
        ),
        ex(
            "Preserve a versioned behavior contract",
            "Import the arithmetic subpath and assert both a normal and a boundary input in the child.",
            "child exits successfully for twice(0)=0 and twice(-2)=-4.",
            r"""await withPackage(async directory => {
  const result = runImport(directory, 'import { strict as assert } from \'node:assert\'; import { twice } from \'course-fixture/math\'; assert.equal(twice(0), 0); assert.equal(twice(-2), -4);');
  assert.equal(result.status, 0, result.stderr);
});""",
            "An exported name existing is weaker than its behavior matching the consumer contract. Boundary tests help detect a breaking semantic change that leaves the interface shape untouched.",
        ),
    ],
    helper="""async function withPackage(use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-package-'));
  try {
    const folder = join(directory, 'node_modules/course-fixture');
    await mkdir(folder, { recursive: true });
    await writeFile(join(folder, 'package.json'), JSON.stringify({ name: 'course-fixture', version: '1.0.0', type: 'module', engines: { node: '>=99' }, exports: { '.': './index.mjs', './math': './math.mjs' } }));
    await writeFile(join(folder, 'index.mjs'), 'export const version = 1;');
    await writeFile(join(folder, 'math.mjs'), 'export const twice = value => value * 2;');
    await writeFile(join(folder, 'private.mjs'), 'export const internal = true;');
    return await use(directory);
  } finally { await rm(directory, { recursive: true, force: true }); }
}
function runImport(directory, source) {
  const path = join(directory, 'main.mjs');
  writeFileSync(path, source);
  const result = spawnSync(process.execPath, [path], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return result;
}
function digest(bytes) { return createHash('sha256').update(bytes).digest('hex'); }""",
    imports="""import { strict as assert } from 'node:assert';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';""",
    source=NODE + "packages.html",
    notes="""### Optional project preparation

In a real learner-owned package, review package.json and the lockfile together, record the intended Node and npm versions, and run the documented locked installation during explicit connected setup. `npm ci --ignore-scripts --no-audit --no-fund` is a useful starting policy when lifecycle scripts are unnecessary; some packages require reviewed build steps, so skipping scripts is not a universal guarantee that installation is complete. Offline reuse needs a complete compatible cache or prepared image. This chapter performs no npm install or npm ci and does not claim those optional project steps were executed.""",
)

add(
    37,
    """A retry is a new attempt after an uncertain or failed operation. It can improve resilience to transient failures, but it also multiplies load and may repeat side effects. Retrying every exception hides programming errors and permanent rejections. An operation needs a retry classification, maximum attempts, delay policy, cancellation behavior and a final failure result. A deadline limits waiting; it does not prove that a remote write did not occur.

Exponential backoff grows the delay between attempts. Full jitter chooses a delay uniformly from zero to a capped exponential bound, spreading clients that would otherwise retry simultaneously. The examples inject the random source and waiting function so expected delays are deterministic. They test a retry policy around a controlled transport fixture, not a real network outage or production recovery claim.

Idempotency associates repeated attempts with one intended operation. A key alone is insufficient if a caller reuses it with different request data. The fixture stores a canonical request representation and its completed result; matching retries reuse that result, while conflicting reuse rejects. Its Map is only in-memory and single-process. It does not survive crashes or solve distributed coordination; a durable service needs a transactionally enforced key/payload/result policy.

Bounded concurrency limits simultaneous owned work. Promise.all over a huge input starts all mapped operations immediately unless scheduling is controlled. The provided worker-loop scheduler starts at most the configured limit and preserves result order. On failure it stops scheduling new work, awaits already started work, then rejects. That is cleanup discipline, not cancellation of external side effects already underway.""",
    """retry receives an operation, an injected wait, an injected random function and an AbortSignal. It checks cancellation before each attempt, retries only the explicit transient category and throws the final error on exhaustion. The delay bound is min(cap, base times 2 to the attempt index), and jitter scales it by a sample in [0,1). The bounded map shares a synchronous next-index counter across async workers; each takes an index before awaiting its operation, so no two workers claim the same item.""",
    [
        ("Retry classification", "The policy selecting failures eligible for another attempt."),
        ("Backoff with jitter", "A growing delay bound with randomized spacing inside it."),
        ("Idempotency key", "An identifier linking retries to one intended operation and payload."),
        ("Bounded concurrency", "A limit on simultaneously active owned operations."),
    ],
    [
        ex(
            "Retry transient failures with deterministic full jitter",
            "Fail twice transiently, then succeed, using random value 0.5 and a recording wait.",
            "three attempts; delays 50 and 100; result ready.",
            r"""let attempts = 0;
const waits = [];
const result = await retry(async () => { attempts += 1; if (attempts < 3) throw Object.assign(new Error('temporary'), { transient: true }); return 'ready'; }, { wait: async value => { waits.push(value); }, random: () => 0.5 });
assert.equal(result, 'ready');
assert.equal(attempts, 3);
assert.deepEqual(waits, [50, 100]);""",
            "The injected wait records policy without sleeping. The result demonstrates classification and arithmetic, not elapsed network latency or a live outage recovery.",
        ),
        ex(
            "Stop on permanent failure and on exhausted attempts",
            "Use one permanent failure, then an always-transient operation with a three-attempt budget.",
            "permanent attempted once; transient attempted three times and still rejects.",
            r"""let permanent = 0;
await assert.rejects(retry(async () => { permanent += 1; throw new Error('permanent'); }), /permanent/u);
assert.equal(permanent, 1);
let transient = 0;
await assert.rejects(retry(async () => { transient += 1; throw Object.assign(new Error('still unavailable'), { transient: true }); }, { wait: async () => {} }), /still unavailable/u);
assert.equal(transient, 3);""",
            "A retry policy must retain a bounded final failure. Converting exhaustion into a default success would erase the operation's actual outcome.",
        ),
        ex(
            "Reuse a completed idempotent result",
            "Submit the same key and payload twice to the local store.",
            "one side effect; identical returned receipt.",
            r"""const store = new IdempotentStore();
const first = store.apply('request-A', { amount: 5 });
const second = store.apply('request-A', { amount: 5 });
assert.deepEqual(second, first);
assert.equal(store.effects, 1);""",
            "A matching retry reads the stored result rather than repeating the side effect. The example is intentionally limited to completed operations in one process.",
        ),
        ex(
            "Reject conflicting reuse of an idempotency key",
            "Reuse one key for amounts 5 and 7.",
            "conflict error; effects remains 1.",
            r"""const store = new IdempotentStore();
store.apply('request-A', { amount: 5 });
assert.throws(() => store.apply('request-A', { amount: 7 }), /key conflict/u);
assert.equal(store.effects, 1);""",
            "A key must identify an operation payload, not grant permission to replace its meaning. Accepting a changed payload could return an unrelated earlier result.",
        ),
        ex(
            "Bound active work while preserving input order",
            "Map four values with concurrency 2 and observe active-operation counts.",
            "results 2,4,6,8; peak active at most 2; active returns to 0.",
            r"""let active = 0;
let peak = 0;
const result = await mapBounded([1, 2, 3, 4], 2, async value => {
  active += 1; peak = Math.max(peak, active);
  try { await delay(1); return value * 2; }
  finally { active -= 1; }
});
assert.deepEqual(result, [2, 4, 6, 8]);
assert.ok(peak <= 2 && peak > 0);
assert.equal(active, 0);
const started = [];
await assert.rejects(mapBounded([1, 2, 3, 4], 2, async value => {
  started.push(value); active += 1;
  try { if (value === 2) throw new Error('controlled failure'); await delay(1); return value; }
  finally { active -= 1; }
}), /controlled failure/u);
assert.deepEqual(started, [1, 2]);
assert.equal(active, 0);
assert.deepEqual(await mapBounded([], 2, async value => value), []);""",
            "The scheduler limits started operations, not merely the size of a Promise result array. Returning results by original index makes completion order independent of output order.",
        ),
        ex(
            "Honor cancellation before the first attempt",
            "Abort a signal before calling retry and track attempted work.",
            "original reason rejects; attempts remain 0.",
            r"""const controller = new AbortController();
const reason = new Error('cancelled before start');
controller.abort(reason);
let attempts = 0;
await assert.rejects(retry(async () => { attempts += 1; return 1; }, { signal: controller.signal }), error => error === reason);
assert.equal(attempts, 0);""",
            "The pre-check prevents starting known-cancelled work. Cancellation during an actual external operation also requires that operation's own cooperative signal support.",
        ),
    ],
    helper="""async function retry(operation, { attempts = 3, base = 100, cap = 1000, random = Math.random, wait = (milliseconds, signal) => delay(milliseconds, undefined, { signal }), signal = new AbortController().signal } = {}) {
  if (!Number.isInteger(attempts) || attempts < 1 || attempts > 5) throw new RangeError('attempts from 1 to 5 required');
  if (!Number.isFinite(base) || !Number.isFinite(cap) || base < 0 || cap < 0 || cap > 10000) throw new RangeError('finite nonnegative backoff with cap at most 10000 required');
  for (let index = 0; index < attempts; index += 1) {
    signal.throwIfAborted();
    try { return await operation(signal); }
    catch (error) {
      if (!error || error.transient !== true || index + 1 === attempts) throw error;
      signal.throwIfAborted();
      const sample = random();
      if (!(sample >= 0 && sample < 1)) throw new RangeError('random sample must be in [0,1)');
      await wait(Math.floor(Math.min(cap, base * 2 ** index) * sample), signal);
    }
  }
  throw new Error('unreachable retry state');
}
class IdempotentStore {
  records = new Map();
  effects = 0;
  apply(key, payload) {
    if (typeof key !== 'string' || !key || !Number.isSafeInteger(payload.amount) || payload.amount <= 0) throw new TypeError('valid key and amount required');
    const canonical = JSON.stringify({ amount: payload.amount });
    const previous = this.records.get(key);
    if (previous) {
      if (previous.canonical !== canonical) throw new Error('idempotency key conflict');
      return { ...previous.result };
    }
    this.effects += 1;
    const result = { sequence: this.effects, amount: payload.amount };
    this.records.set(key, { canonical, result });
    return { ...result };
  }
}
async function mapBounded(values, limit, operation) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 8) throw new RangeError('limit from 1 to 8 required');
  const results = new Array(values.length);
  let next = 0;
  let failed = false;
  let failure;
  async function worker() {
    while (!failed && next < values.length) {
      const index = next++;
      try { results[index] = await operation(values[index], index); }
      catch (error) { if (!failed) { failed = true; failure = error; } }
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, values.length) }, worker));
  if (failed) throw failure;
  return results;
}""",
    imports="""import { strict as assert } from 'node:assert';
import { setTimeout as delay } from 'node:timers/promises';""",
    source=NODE + "timers.html",
)
