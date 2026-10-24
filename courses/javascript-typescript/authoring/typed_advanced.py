from render import add, ex

TS = "https://www.typescriptlang.org/docs/handbook/"

add(
    25,
    """TypeScript source participates in two related dependency graphs: the compiler resolves source and declarations while checking, and Node resolves emitted JavaScript while running. Under NodeNext, a .mts source emits an ES module with a .mjs extension. Source imports name the runtime .mjs dependency; the compiler can resolve that specifier to its corresponding .mts source. A bundler may have different rules, but this route deliberately targets Node ESM.

Type-only imports declare dependencies needed only by the checker and disappear from emitted code. Value imports remain runtime dependencies. Successful type checking does not prove every required runtime artifact was packaged. The examples inspect emitted files and deliberately remove one owned temporary dependency to observe that distinction.

This reference creates tiny two-file projects in temporary directories, invokes the actual prepared compiler with strict NodeNext and noEmitOnError, and runs the emitted entry as a fresh Node process. Negative projects produce real diagnostics and verify that no entry was emitted. A fresh output directory avoids accidentally running stale JavaScript from an earlier successful build. No package is installed. The single main.mts pad owns and cleans up its temporary project.""",
    """The prepared compiler path is /opt/typescript/node_modules/typescript/bin/tsc. DS60_TSC_JS optionally selects an already prepared development copy; it never downloads one. The adjacent @types directory supplies Node declarations. spawnSync uses fixed argument arrays, separate stdout/stderr, a timeout and output cap. Type diagnostics and runtime loader errors are checked separately. The type-only dependency test inspects emitted code instead of inferring erasure from a successful run.""",
    [
        ("NodeNext", "Resolution rules modeling Node module formats and loading."),
        ("Type-only import", "A dependency used for checking and erased before execution."),
        ("Emitted extension", "The filename extension the runtime resolver actually sees."),
        ("NoEmitOnError", "The policy preventing JavaScript output when checking fails."),
    ],
    [
        ex(
            "Compile and run a two-module project",
            "Compile a main module importing twice from ./math.mjs and run it.",
            "both processes succeed; output 8; math.mjs is emitted.",
            r"""await withProject({ 'math.mts': 'export const twice = (value: number): number => value * 2;', 'main.mts': 'import { twice } from \'./math.mjs\'; console.log(twice(4));' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const executed = runModule(directory);
  assert.equal(executed.status, 0, executed.stderr);
  assert.equal(executed.stdout.trim(), '8');
  assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true);
});""",
            "The runtime specifier is .mjs even though the source file is .mts. Naming a source-only extension without a corresponding emit policy can produce a runtime failure.",
        ),
        ex(
            "Inspect type-only erasure",
            "Compile a type import and inspect the emitted entry before running it.",
            "no model import in emitted entry; output A.",
            r"""await withProject({ 'model.mts': 'export type Item = { id: string };', 'main.mts': 'import type { Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(item.id);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
  assert.equal(emitted.includes('./model.mjs'), false);
  assert.equal(runModule(directory).stdout.trim(), 'A');
});""",
            "The type relation constrains source checking without becoming a value dependency. Inspecting the emitted program demonstrates this directly.",
        ),
        ex(
            "Reject a type mismatch without output",
            "Assign text to a number in a fresh project.",
            "TS2322; nonzero compiler status; no compiled main.mjs.",
            r"""await withProject({ 'main.mts': 'const count: number = \'wrong\'; console.log(count);' }, async directory => {
  const compiled = compile(directory);
  assert.notEqual(compiled.status, 0);
  assert.match(compiled.stdout + compiled.stderr, /TS2322/u);
  assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
});""",
            "The test checks both diagnosis and output policy. A diagnostic alone does not establish whether stale or partially emitted artifacts could still be executed.",
        ),
        ex(
            "Require runtime-valid relative extensions",
            "Import ./math without an extension under NodeNext ESM.",
            "TS2835 and no emitted entry.",
            r"""await withProject({ 'math.mts': 'export const value = 2;', 'main.mts': 'import { value } from \'./math\'; console.log(value);' }, async directory => {
  const compiled = compile(directory);
  assert.notEqual(compiled.status, 0);
  assert.match(compiled.stdout + compiled.stderr, /TS2835/u);
  assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
});""",
            "The chosen resolver is part of the program contract. A convenience supplied by another toolchain is not automatically available in direct Node execution.",
        ),
        ex(
            "Observe a missing runtime artifact",
            "Compile successfully, remove only the owned emitted dependency, then run the entry.",
            "Node fails with ERR_MODULE_NOT_FOUND.",
            r"""await withProject({ 'value.mts': 'export const value = 3;', 'main.mts': 'import { value } from \'./value.mjs\'; console.log(value);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  await rm(join(directory, 'compiled', 'value.mjs'));
  const executed = runModule(directory);
  assert.notEqual(executed.status, 0);
  assert.match(executed.stderr, /ERR_MODULE_NOT_FOUND/u);
});""",
            "The deletion is restricted to a newly allocated temporary output. It models a missing packaged dependency without editing learner or repository files.",
        ),
        ex(
            "Retain value imports beside erased type imports",
            "Import both a type and a value from one module.",
            "value dependency remains; runtime prints ready:A.",
            r"""await withProject({ 'model.mts': 'export type Item = { id: string }; export const prefix = \'ready\';', 'main.mts': 'import { prefix, type Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(prefix + \':\' + item.id);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
  assert.ok(emitted.includes('./model.mjs'));
  assert.equal(runModule(directory).stdout.trim(), 'ready:A');
});""",
            "The type and value namespaces have different runtime roles even when declarations share a source module. The value must remain packaged and resolvable.",
        ),
    ],
    helper="""type ProcessResult = { status: number | null; stdout: string; stderr: string };
async function withProject(files: Record<string, string>, use: (directory: string) => Promise<void>): Promise<void> {
  const directory = await mkdtemp(join(tmpdir(), 'course-ts-project-'));
  try {
    for (const [name, source] of Object.entries(files)) await writeFile(join(directory, name), source, 'utf8');
    await use(directory);
  } finally { await rm(directory, { recursive: true, force: true }); }
}
function child(args: string[]): ProcessResult {
  const result = spawnSync(process.execPath, args, { encoding: 'utf8', timeout: 20000, maxBuffer: 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return { status: result.status, stdout: result.stdout, stderr: result.stderr };
}
function compile(directory: string): ProcessResult {
  const compiler = process.env.DS60_TSC_JS ?? '/opt/typescript/node_modules/typescript/bin/tsc';
  const typeRoots = resolve(dirname(compiler), '../..', '@types');
  return child([compiler, '--target', 'ES2022', '--module', 'NodeNext', '--moduleResolution', 'NodeNext', '--strict', '--noEmitOnError', '--skipLibCheck', '--types', 'node', '--typeRoots', typeRoots, '--outDir', join(directory, 'compiled'), join(directory, 'main.mts')]);
}
function runModule(directory: string): ProcessResult { return child([join(directory, 'compiled', 'main.mjs')]); }
async function exists(path: string): Promise<boolean> {
  try { await access(path); return true; }
  catch (error: unknown) {
    if (error instanceof Error && 'code' in error && error.code === 'ENOENT') return false;
    throw error;
  }
}""",
    imports="""import { strict as assert } from 'node:assert';
import { mkdtemp, writeFile, readFile, access, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';""",
    source=TS + "modules/reference.html",
)

add(
    26,
    """Classes combine state with operations that preserve invariants. A typed number can still be negative, fractional, infinite or too large for exact integer arithmetic. A balance object therefore checks values before assigning new state. Constructor and method annotations document accepted checked calls, while runtime checks protect the actual numeric domain.

JavaScript #private fields enforce privacy at runtime. TypeScript private is primarily a checking restriction and should not be confused with a security boundary around ordinary emitted properties. Encapsulation is useful when callers should request an operation rather than directly assign arbitrary state. A getter returning a number supplies a value; a getter returning a mutable object would need a separate ownership policy.

Composition supplies a collaborator through a small interface, such as a clock. A test can provide a deterministic clock without changing global time or subclassing a large framework. The interface describes the capability required by the consumer. Inheritance is appropriate when substitutability is real, but reusing a few implementation lines does not prove that every subclass preserves its parent's contract.""",
    """A constructor establishes initial state. #balance names a runtime private field, while the cents getter exposes a primitive observation. implements would check an interface without generating methods. Constructor parameter properties create fields as part of TypeScript emission. A readonly dependency reference prevents reassignment through that class; it does not guarantee the collaborator itself is immutable. Validate derived results before committing a state transition.""",
    [
        ("Encapsulation", "Restricting state changes to invariant-preserving operations."),
        ("Private field", "A JavaScript # field with runtime-enforced access."),
        ("Composition", "Building behavior from explicit collaborators."),
        ("Interface", "A static capability contract for compatible values."),
    ],
    [
        ex(
            "Maintain balance through methods",
            "Start with 100 cents, deposit 50 and withdraw 30.",
            "balance 120; no enumerable balance field.",
            r"""const wallet = new Wallet(100);
wallet.deposit(50);
wallet.withdraw(30);
assert.equal(wallet.cents, 120);
assert.equal(Object.hasOwn(wallet, 'balance'), false);
assert.deepEqual(Object.keys(wallet), []);""",
            "The public API exposes observations and controlled mutations. A caller cannot directly assign the private field by an ordinary property name.",
        ),
        ex(
            "Inject a deterministic clock",
            "Create a receipt service using a fixed clock.",
            "timestamp 2026-01-01T00:00:00.000Z.",
            r"""const service = new ReceiptService({ now: () => new Date('2026-01-01T00:00:00.000Z') });
assert.deepEqual(service.create('A'), { id: 'A', createdAt: '2026-01-01T00:00:00.000Z' });""",
            "The time dependency is explicit and replaceable. The test does not mutate global time or rely on a fragile elapsed-time tolerance.",
        ),
        ex(
            "Reject invalid transitions without mutation",
            "Try a negative deposit and an overdraw.",
            "both throw; balance stays 100.",
            r"""const wallet = new Wallet(100);
assert.throws(() => wallet.deposit(-1), RangeError);
assert.throws(() => wallet.withdraw(101), RangeError);
assert.equal(wallet.cents, 100);""",
            "Checking after mutation would leave invalid state when the method throws. Validation must precede assignment for this failure-atomic contract.",
        ),
        ex(
            "Guard derived overflow",
            "Deposit one cent into the maximum safe balance.",
            "RangeError; original balance preserved.",
            r"""const wallet = new Wallet(Number.MAX_SAFE_INTEGER);
assert.throws(() => wallet.deposit(1), RangeError);
assert.equal(wallet.cents, Number.MAX_SAFE_INTEGER);""",
            "Valid individual inputs do not guarantee a representable sum. The invariant applies to the resulting state as well as the method argument.",
        ),
        ex(
            "Reject an incompatible collaborator",
            "Pass a clock returning text in an uncalled negative type check.",
            "expected compiler error; valid Date clock works.",
            r"""function negativeTypeCheck(): void {
  // @ts-expect-error Clock.now must return Date.
  new ReceiptService({ now: () => 'today' });
}
void negativeTypeCheck;
assert.equal(new ReceiptService({ now: () => new Date(0) }).create('B').createdAt, '1970-01-01T00:00:00.000Z');""",
            "The small interface catches a concrete mismatch without requiring the collaborator to inherit from a particular class.",
        ),
        ex(
            "Distinguish private storage from a lookalike property",
            "Add an ordinary balance property to the wallet.",
            "ordinary property 999; private cents remain 2.",
            r"""const wallet = new Wallet(2);
Object.assign(wallet, { balance: 999 });
assert.equal(Reflect.get(wallet, 'balance'), 999);
assert.equal(wallet.cents, 2);""",
            "The string property and private name refer to separate storage. This observation demonstrates a runtime guarantee rather than only a compiler diagnostic.",
        ),
    ],
    helper="""function validCents(value: number): void {
  if (!Number.isSafeInteger(value) || value < 0) throw new RangeError('nonnegative safe integer cents required');
}
class Wallet {
  #balance: number;
  constructor(initial: number) { validCents(initial); this.#balance = initial; }
  get cents(): number { return this.#balance; }
  deposit(amount: number): void {
    validCents(amount);
    const next = this.#balance + amount;
    validCents(next);
    this.#balance = next;
  }
  withdraw(amount: number): void {
    validCents(amount);
    if (amount > this.#balance) throw new RangeError('insufficient balance');
    this.#balance -= amount;
  }
}
interface Clock { now(): Date }
class ReceiptService {
  constructor(private readonly clock: Clock) {}
  create(id: string): { id: string; createdAt: string } {
    if (id === '') throw new TypeError('id required');
    return { id, createdAt: this.clock.now().toISOString() };
  }
}""",
    source=TS + "2/classes.html",
)

add(
    27,
    """Promise<T> describes a fulfilled value. JavaScript rejection reasons are not captured by a second built-in error type parameter, so caught failures must still be inspected. Expected domain failures can instead be represented as a discriminated Result value. Unexpected operational failures may continue to reject. An API must explain which failure channel it uses, especially if it uses both.

Promise<Result<T>> introduces two decisions: await completion, then inspect the result. A failed Result is a fulfilled Promise containing an explicit failure value. It does not trigger catch. Conversely, a rejected Promise does not become a Result unless implementation code catches and translates it. Failing to distinguish these channels can turn an expected missing record into an unhandled rejection or turn a genuine programming error into misleading business data.

Cancellation remains a runtime cooperation protocol. A signal annotation proves that a compatible object was supplied, not that the operation observes it. The examples cancel a real timer and translate only its documented AbortError category. Batch operations must also choose whether to stop at the first rejection or retain every outcome. allSettled preserves outcome records, but rejected records must not be mistaken for valid values.""",
    """A Result union carries either ok:true with value or ok:false with an error category. Narrow ok before reading the payload. An async function wraps a returned result in a Promise. Catch variables are unknown under strict checking. instanceof Error permits reading message, while matching a documented name or code determines whether translation is appropriate. Re-throw unrecognized failures to retain diagnosis.""",
    [
        ("Result channel", "An explicit success/failure value."),
        ("Rejection channel", "A Promise failure propagated through throw or reject."),
        ("Error translation", "Mapping a recognized failure into a documented result."),
        (
            "Batch outcome policy",
            "The treatment of partial success and failure across several operations.",
        ),
    ],
    [
        ex(
            "Await and narrow a result",
            "Look up a known id and an absent id.",
            "known value 7; absent error not_found.",
            r"""const present = await lookup('A');
if (!present.ok) throw new Error(present.error);
assert.equal(present.value, 7);
assert.deepEqual(await lookup('missing'), { ok: false, error: 'not_found' });""",
            "Await establishes completion; the discriminant establishes domain success. Both conditions are needed before accessing the payload.",
        ),
        ex(
            "Show a failure result does not invoke catch",
            "Attach catch to a lookup returning a not_found value.",
            "catch count 0; result still not_found.",
            r"""let caught = 0;
const result = await lookup('missing').catch(() => { caught += 1; return { ok: false as const, error: 'operational' as const }; });
assert.equal(caught, 0);
assert.deepEqual(result, { ok: false, error: 'not_found' });""",
            "A result value is ordinary fulfilled data even when it describes a domain failure. The caller must branch on it explicitly.",
        ),
        ex(
            "Translate recognized cancellation",
            "Abort a real timer-backed operation.",
            "failure result cancelled.",
            r"""const controller = new AbortController();
const pending = waitForValue(controller.signal);
controller.abort(new Error('stop'));
assert.deepEqual(await pending, { ok: false, error: 'cancelled' });""",
            "The timer cooperates with the signal. Only its recognized abort error is translated; unrelated exceptions remain visible through rejection.",
        ),
        ex(
            "Inspect an unknown rejection reason",
            "Reject with a string and normalize it at a reporting boundary.",
            "diagnostic unclassified failure.",
            r"""function message(error: unknown): string { return error instanceof Error ? error.message : 'unclassified failure'; }
try { await Promise.reject('not an Error'); }
catch (error: unknown) { assert.equal(message(error), 'unclassified failure'); }""",
            "Any JavaScript value can be a rejection reason. Assuming it always has a message property risks a second failure while reporting the first.",
        ),
        ex(
            "Preserve every batch outcome",
            "Summarize one fulfilled value and one rejected task.",
            "value:2 and error:offline.",
            r"""const outcomes = await Promise.allSettled([Promise.resolve(2), Promise.reject(new Error('offline'))]);
const summaries = outcomes.map(outcome => {
  if (outcome.status === 'fulfilled') return `value:${outcome.value}`;
  const reason: unknown = outcome.reason;
  return `error:${reason instanceof Error ? reason.message : 'unknown'}`;
});
assert.deepEqual(summaries, ['value:2', 'error:offline']);""",
            "The status discriminant selects the outcome payload. Treating rejection data as unknown keeps the application boundary honest even when library declarations expose a broader type.",
        ),
        ex(
            "Reject unresolved and unnarrowed access",
            "Demonstrate both errors in an uncalled compile-time check.",
            "expected diagnostics for value before await or before narrowing.",
            r"""function negativeTypeCheck(result: Result<number>): void {
  // @ts-expect-error The failure alternative has no value.
  void result.value;
  // @ts-expect-error lookup returns a Promise, not an immediate payload.
  void lookup('A').value;
}
void negativeTypeCheck;
assert.deepEqual(await lookup('A'), { ok: true, value: 7 });""",
            "These are distinct boundaries. Adding await fixes only the asynchronous layer; success narrowing is still required afterward.",
        ),
    ],
    helper="""type Result<T> = { ok: true; value: T } | { ok: false; error: 'not_found' | 'cancelled' | 'operational' };
async function lookup(id: string): Promise<Result<number>> {
  return id === 'A' ? { ok: true, value: 7 } : { ok: false, error: 'not_found' };
}
async function waitForValue(signal: AbortSignal): Promise<Result<number>> {
  try {
    const value = await delay(1000, 7, { signal });
    return { ok: true, value };
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') return { ok: false, error: 'cancelled' };
    throw error;
  }
}""",
    imports="""import { strict as assert } from 'node:assert';
import { setTimeout as delay } from 'node:timers/promises';""",
    source=TS + "2/narrowing.html",
)

add(
    28,
    """Types clarify an algorithm's interface, but correctness depends on its invariant. Breadth-first search explores a graph in layers of edge distance. Marking a vertex when enqueuing it ensures the vertex enters the queue once, even when edges form cycles. A parent map records each first-discovery edge, allowing the shortest unweighted path to be reconstructed from target to source.

Adjacency-list BFS performs O(V+E) work under ordinary Map lookup assumptions and stores O(V) extra state. An array plus a cursor avoids repeated shift operations that move remaining elements. Several shortest paths may exist; neighbor order defines this implementation's deterministic tie policy. Weighted edges need another algorithm, such as Dijkstra for nonnegative weights. BFS does not minimize arbitrary travel cost merely because its path has few edges.

Dynamic programming reuses overlapping subproblem results. For minimum coin count, best[a] is the smallest number of allowed coins summing to amount a. best[0]=0. Each other state minimizes best[a-coin]+1 over usable denominations. Infinity represents an unreachable amount. The recurrence assumes unbounded reuse of positive integer coins. For coins 1,3,4 and target 6, greedy selection gives 4+1+1, while the recurrence discovers 3+3. The table has O(amount) memory and O(amount times number-of-coins) work, so numeric magnitude is part of its cost.""",
    """ReadonlyMap<string, readonly string[]> states that search consumes the graph without modifying it. Runtime checks require every referenced neighbor to exist. A null parent marks the source; an absent Map entry means undiscovered. Reconstruction follows parent links until null. The DP table is filled in increasing amount order so every dependency is already available. Positive integer denominations and a target cap preserve this dependency order and bound resource use.""",
    [
        (
            "Breadth-first search",
            "Layered exploration finding fewest-edge paths in an unweighted graph.",
        ),
        ("Parent map", "First-discovery predecessors used to reconstruct a path."),
        ("Dynamic programming", "Reusing results of overlapping subproblems."),
        ("Recurrence", "A rule computing a state from smaller solved states."),
    ],
    [
        ex(
            "Find a shortest unweighted path",
            "Search a graph with two equal-length routes from A to D.",
            "A,B,D under the stated neighbor order.",
            r"""const graph: Graph = new Map([['A', ['B', 'C']], ['B', ['D']], ['C', ['D']], ['D', []]]);
assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D']);""",
            "Both two-edge routes are shortest. The implementation chooses the first discovered route rather than claiming the answer is mathematically unique.",
        ),
        ex(
            "Beat greedy coin selection",
            "Use denominations 1,3,4 to make amount 6.",
            "two coins; amount zero needs zero coins.",
            r"""assert.equal(minCoins([1, 3, 4], 6), 2);
assert.equal(minCoins([1, 3, 4], 0), 0);""",
            "The recurrence evaluates every possible final coin. It avoids the attractive local choice of 4 that leads to a worse total count.",
        ),
        ex(
            "Terminate on a cyclic graph",
            "Search A to C through A-B-A cycles and check source-to-source.",
            "A,B,C and A.",
            r"""const graph: Graph = new Map([['A', ['B']], ['B', ['A', 'C']], ['C', ['B']]]);
assert.deepEqual(shortestPath(graph, 'A', 'C'), ['A', 'B', 'C']);
assert.deepEqual(shortestPath(graph, 'A', 'A'), ['A']);""",
            "Marking on enqueue prevents repeated insertion through the cycle. The source begins discovered at distance zero.",
        ),
        ex(
            "Separate disconnection from malformed input",
            "Search a disconnected target, then supply a missing neighbor.",
            "undefined for no path; RangeError for invalid graph.",
            r"""assert.equal(shortestPath(new Map([['A', []], ['B', []]]), 'A', 'B'), undefined);
assert.throws(() => shortestPath(new Map([['A', ['missing']]]), 'A', 'A'), RangeError);""",
            "No path is a valid answer for a well-formed graph. Missing vertices violate the input contract and are rejected even if source equals target.",
        ),
        ex(
            "Represent unreachable coin amounts",
            "Use denomination 2 for targets 3 and 4.",
            "undefined and 2.",
            r"""assert.equal(minCoins([2], 3), undefined);
assert.equal(minCoins([2], 4), 2);""",
            "Infinity remains an internal unreachable sentinel. The public return type exposes absence instead of pretending Infinity is a valid count.",
        ),
        ex(
            "Reject invalid recurrence configurations",
            "Try zero, negative and fractional coins plus target 1001.",
            "RangeError for all invalid configurations; empty denominations cannot make 1.",
            r"""for (const coins of [[0], [-1], [1.5]]) assert.throws(() => minCoins(coins, 5), RangeError);
assert.throws(() => minCoins([1], 1001), RangeError);
assert.equal(minCoins([], 1), undefined);""",
            "Positive coins guarantee dependencies point to smaller amounts. A target bound prevents unexpectedly large allocations in this small teaching implementation.",
        ),
    ],
    helper="""type Graph = ReadonlyMap<string, readonly string[]>;
function shortestPath(graph: Graph, start: string, target: string): string[] | undefined {
  if (!graph.has(start) || !graph.has(target)) throw new RangeError('start and target must exist');
  for (const neighbors of graph.values()) for (const neighbor of neighbors) {
    if (!graph.has(neighbor)) throw new RangeError('missing neighbor');
  }
  const queue = [start];
  const parent = new Map<string, string | null>([[start, null]]);
  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const vertex = queue[cursor];
    if (vertex === target) {
      const path: string[] = [];
      let current: string | null = vertex;
      while (current !== null) {
        path.push(current);
        const previous: string | null | undefined = parent.get(current);
        if (previous === undefined) throw new Error('broken parent invariant');
        current = previous;
      }
      return path.reverse();
    }
    for (const neighbor of graph.get(vertex) ?? []) {
      if (!parent.has(neighbor)) { parent.set(neighbor, vertex); queue.push(neighbor); }
    }
  }
  return undefined;
}
function minCoins(coins: readonly number[], amount: number): number | undefined {
  if (!Number.isInteger(amount) || amount < 0 || amount > 1000 || coins.some(coin => !Number.isSafeInteger(coin) || coin <= 0)) throw new RangeError('positive coins and amount from 0 to 1000 required');
  const best: number[] = Array.from({ length: amount + 1 }, () => Infinity);
  best[0] = 0;
  for (let value = 1; value <= amount; value += 1) {
    for (const coin of coins) if (coin <= value) best[value] = Math.min(best[value], best[value - coin] + 1);
  }
  return Number.isFinite(best[amount]) ? best[amount] : undefined;
}""",
    source=TS + "2/generics.html",
    notes="""### Representation and correctness

The Map and array annotations cannot prove that the search invariant or recurrence is correct. The trace, tie policy, invalid-input checks and independent expected values establish those claims for the fixtures. Large graphs require an input-size budget, and weighted paths need a different algorithm. Large numeric targets may make the pseudo-polynomial DP cost unacceptable even if the target fits in a JavaScript number. Choose an algorithm from its assumptions and resource requirements, not from whether its type signature looks sophisticated.""",
)
