# js-025: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

TypeScript source participates in two related dependency graphs: the compiler resolves source and declarations while checking, and Node resolves emitted JavaScript while running. Under NodeNext, a .mts source emits an ES module with a .mjs extension. Source imports name the runtime .mjs dependency; the compiler can resolve that specifier to its corresponding .mts source. A bundler may have different rules, but this route deliberately targets Node ESM. Node 24 can also strip types and run main.mts directly, but it never rewrites specifiers: under node main.mts an import of ./math.mjs fails with ERR_MODULE_NOT_FOUND because only math.mts exists, while ./math.mts loads. The compiler rejects a .mts specifier (TS5097) unless allowImportingTsExtensions or rewriteRelativeImportExtensions is set; the latter rewrites ./math.mts to ./math.mjs in emitted code. Stripping also skips type checking, which is why this route compiles first.

Type-only imports declare dependencies needed only by the checker and disappear from emitted code. Value imports remain runtime dependencies. Successful type checking does not prove every required runtime artifact was packaged. The examples inspect emitted files and deliberately remove one owned temporary dependency to observe that distinction.

This reference creates tiny two-file projects in temporary directories, invokes the actual prepared compiler with strict NodeNext and noEmitOnError, and runs the emitted entry as a fresh Node process. Negative projects produce real diagnostics and verify that no entry was emitted. A fresh output directory avoids accidentally running stale JavaScript from an earlier successful build. No package is installed. The single main.mts pad owns and cleans up its temporary project.

**NodeNext:** Resolution rules modeling Node module formats and loading.

**Type-only import:** A dependency used for checking and erased before execution.

**Emitted extension:** The filename extension the runtime resolver actually sees.

**NoEmitOnError:** The policy preventing JavaScript output when checking fails.

## Reading the implementation

The prepared compiler path is /opt/typescript/node_modules/typescript/bin/tsc. DS60_TSC_JS optionally selects an already prepared development copy; it never downloads one. The adjacent @types directory supplies Node declarations. spawnSync uses fixed argument arrays, separate stdout/stderr, a timeout and output cap. Type diagnostics and runtime loader errors are checked separately. The type-only dependency test inspects emitted code instead of inferring erasure from a successful run.

## Exercise 1: Compile and run a two-module project: predict an edited check

Task: Copy Example A into a scratch `main.mts` and change `assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true);` to `assert.equal(await exists(join(directory, 'compiled!', 'math.mjs')), true);` inside its check. Before running it, predict whether the check still passes and explain why; then restore it.

The runtime specifier is .mjs even though the source file is .mts. Naming a source-only extension without a corresponding emit policy can produce a runtime failure.

The unchanged code is the exercise block of Example A:

```typescript
await withProject(
  {
    'math.mts': 'export const twice = (value: number): number => value * 2;',
    'main.mts': 'import { twice } from \'./math.mjs\'; console.log(twice(4));',
  },
  async (directory) => {
    const compiled = compile(directory);
    assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
    const executed = runModule(directory);
    assert.equal(executed.status, 0, executed.stderr);
    assert.equal(executed.stdout.trim(), '8');
    assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true);
  },
);
```

**Expected:** The changed run fails with an `AssertionError` at `assert.equal(await exists(join(directory, 'compiled!', 'math.mjs')), true);`. Restoring `assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true);` brings back: both processes succeed; output 8; math.mjs is emitted.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and explain why the edited check rejects the values that `assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true)` accepts. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Inspect type-only erasure: debug a regression

Task: A regression changed one token in Example B, so one line now reads `'model.mts!': 'export type Item = { id: string };',`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

The type relation constrains source checking without becoming a value dependency. Inspecting the emitted program demonstrates this directly.

The unchanged code is the exercise block of Example B:

```typescript
await withProject(
  {
    'model.mts': 'export type Item = { id: string };',
    'main.mts':
      'import type { Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(item.id);',
  },
  async (directory) => {
    const compiled = compile(directory);
    assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
    const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
    assert.equal(emitted.includes('./model.mjs'), false);
    assert.equal(runModule(directory).stdout.trim(), 'A');
  },
);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr)`. Restoring `'model.mts': 'export type Item = { id: string };',` brings back: no model import in emitted entry; output A.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr)` for this input.

## Exercise 3: Reject a type mismatch without output

Task: Assign text to a number in a fresh project.

The test checks both diagnosis and output policy. A diagnostic alone does not establish whether stale or partially emitted artifacts could still be executed.

```typescript
await withProject(
  { 'main.mts': 'const count: number = \'wrong\'; console.log(count);' },
  async (directory) => {
    const compiled = compile(directory);
    assert.notEqual(compiled.status, 0);
    assert.match(compiled.stdout + compiled.stderr, /TS2322/u);
    assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
  },
);
```

**Expected:** TS2322; nonzero compiler status; no compiled main.mjs.

**Verify:** Keep a check equivalent to `assert.match(compiled.stdout + compiled.stderr, /TS2322/u)`. As a control, change `{ 'main.mts': 'const count: number = \'wrong\'; console.log(count);' },` to `{ 'main.mts!': 'const count: number = \'wrong\'; console.log(count);' },`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Require runtime-valid relative extensions

Task: Import ./math without an extension under NodeNext ESM.

The chosen resolver is part of the program contract. A convenience supplied by another toolchain is not automatically available in direct Node execution.

```typescript
await withProject(
  {
    'math.mts': 'export const value = 2;',
    'main.mts': 'import { value } from \'./math\'; console.log(value);',
  },
  async (directory) => {
    const compiled = compile(directory);
    assert.notEqual(compiled.status, 0);
    assert.match(compiled.stdout + compiled.stderr, /TS2835/u);
    assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
  },
);
```

**Expected:** TS2835 and no emitted entry.

**Verify:** Keep a check equivalent to `assert.match(compiled.stdout + compiled.stderr, /TS2835/u)`. As a control, change `'math.mts': 'export const value = 2;',` to `'math.mts!': 'export const value = 2;',`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Observe a missing runtime artifact

Task: Compile successfully, remove only the owned emitted dependency, then run the entry.

The deletion is restricted to a newly allocated temporary output. It models a missing packaged dependency without editing learner or repository files.

```typescript
await withProject(
  {
    'value.mts': 'export const value = 3;',
    'main.mts': 'import { value } from \'./value.mjs\'; console.log(value);',
  },
  async (directory) => {
    const compiled = compile(directory);
    assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
    await rm(join(directory, 'compiled', 'value.mjs'));
    const executed = runModule(directory);
    assert.notEqual(executed.status, 0);
    assert.match(executed.stderr, /ERR_MODULE_NOT_FOUND/u);
  },
);
```

**Expected:** Node fails with ERR_MODULE_NOT_FOUND.

**Verify:** Keep a check equivalent to `assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr)`. As a control, change `'value.mts': 'export const value = 3;',` to `'value.mts!': 'export const value = 3;',`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 6: Retain value imports beside erased type imports

Task: Import both a type and a value from one module.

The type and value namespaces have different runtime roles even when declarations share a source module. The value must remain packaged and resolvable.

```typescript
await withProject(
  {
    'model.mts': 'export type Item = { id: string }; export const prefix = \'ready\';',
    'main.mts':
      'import { prefix, type Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(prefix + \':\' + item.id);',
  },
  async (directory) => {
    const compiled = compile(directory);
    assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
    const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
    assert.ok(emitted.includes('./model.mjs'));
    assert.equal(runModule(directory).stdout.trim(), 'ready:A');
  },
);
```

**Expected:** value dependency remains; runtime prints ready:A.

**Verify:** Keep a check equivalent to `assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr)`. As a control, change `'model.mts': 'export type Item = { id: string }; export const prefix = \'ready\';',` to `'model.mts!': 'export type Item = { id: string }; export const prefix = \'ready\';',`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
