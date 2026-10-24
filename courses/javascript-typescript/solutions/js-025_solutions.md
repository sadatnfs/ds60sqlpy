# js-025: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

TypeScript source participates in two related dependency graphs: the compiler resolves source and declarations while checking, and Node resolves emitted JavaScript while running. Under NodeNext, a .mts source emits an ES module with a .mjs extension. Source imports name the runtime .mjs dependency; the compiler can resolve that specifier to its corresponding .mts source. A bundler may have different rules, but this route deliberately targets Node ESM.

Type-only imports declare dependencies needed only by the checker and disappear from emitted code. Value imports remain runtime dependencies. Successful type checking does not prove every required runtime artifact was packaged. The examples inspect emitted files and deliberately remove one owned temporary dependency to observe that distinction.

This reference creates tiny two-file projects in temporary directories, invokes the actual prepared compiler with strict NodeNext and noEmitOnError, and runs the emitted entry as a fresh Node process. Negative projects produce real diagnostics and verify that no entry was emitted. A fresh output directory avoids accidentally running stale JavaScript from an earlier successful build. No package is installed. The single main.mts pad owns and cleans up its temporary project.

**NodeNext:** Resolution rules modeling Node module formats and loading.

**Type-only import:** A dependency used for checking and erased before execution.

**Emitted extension:** The filename extension the runtime resolver actually sees.

**NoEmitOnError:** The policy preventing JavaScript output when checking fails.

## Reading the implementation

The prepared compiler path is /opt/typescript/node_modules/typescript/bin/tsc. DS60_TSC_JS optionally selects an already prepared development copy; it never downloads one. The adjacent @types directory supplies Node declarations. spawnSync uses fixed argument arrays, separate stdout/stderr, a timeout and output cap. Type diagnostics and runtime loader errors are checked separately. The type-only dependency test inspects emitted code instead of inferring erasure from a successful run.

## Exercise 1: Compile and run a two-module project

Task: Compile a main module importing twice from ./math.mjs and run it.

The runtime specifier is .mjs even though the source file is .mts. Naming a source-only extension without a corresponding emit policy can produce a runtime failure.

```typescript
await withProject({ 'math.mts': 'export const twice = (value: number): number => value * 2;', 'main.mts': 'import { twice } from \'./math.mjs\'; console.log(twice(4));' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const executed = runModule(directory);
  assert.equal(executed.status, 0, executed.stderr);
  assert.equal(executed.stdout.trim(), '8');
  assert.equal(await exists(join(directory, 'compiled', 'math.mjs')), true);
});
```

**Expected:** both processes succeed; output 8; math.mjs is emitted.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Inspect type-only erasure

Task: Compile a type import and inspect the emitted entry before running it.

The type relation constrains source checking without becoming a value dependency. Inspecting the emitted program demonstrates this directly.

```typescript
await withProject({ 'model.mts': 'export type Item = { id: string };', 'main.mts': 'import type { Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(item.id);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
  assert.equal(emitted.includes('./model.mjs'), false);
  assert.equal(runModule(directory).stdout.trim(), 'A');
});
```

**Expected:** no model import in emitted entry; output A.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Reject a type mismatch without output

Task: Assign text to a number in a fresh project.

The test checks both diagnosis and output policy. A diagnostic alone does not establish whether stale or partially emitted artifacts could still be executed.

```typescript
await withProject({ 'main.mts': 'const count: number = \'wrong\'; console.log(count);' }, async directory => {
  const compiled = compile(directory);
  assert.notEqual(compiled.status, 0);
  assert.match(compiled.stdout + compiled.stderr, /TS2322/u);
  assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
});
```

**Expected:** TS2322; nonzero compiler status; no compiled main.mjs.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Require runtime-valid relative extensions

Task: Import ./math without an extension under NodeNext ESM.

The chosen resolver is part of the program contract. A convenience supplied by another toolchain is not automatically available in direct Node execution.

```typescript
await withProject({ 'math.mts': 'export const value = 2;', 'main.mts': 'import { value } from \'./math\'; console.log(value);' }, async directory => {
  const compiled = compile(directory);
  assert.notEqual(compiled.status, 0);
  assert.match(compiled.stdout + compiled.stderr, /TS2835/u);
  assert.equal(await exists(join(directory, 'compiled', 'main.mjs')), false);
});
```

**Expected:** TS2835 and no emitted entry.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Observe a missing runtime artifact

Task: Compile successfully, remove only the owned emitted dependency, then run the entry.

The deletion is restricted to a newly allocated temporary output. It models a missing packaged dependency without editing learner or repository files.

```typescript
await withProject({ 'value.mts': 'export const value = 3;', 'main.mts': 'import { value } from \'./value.mjs\'; console.log(value);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  await rm(join(directory, 'compiled', 'value.mjs'));
  const executed = runModule(directory);
  assert.notEqual(executed.status, 0);
  assert.match(executed.stderr, /ERR_MODULE_NOT_FOUND/u);
});
```

**Expected:** Node fails with ERR_MODULE_NOT_FOUND.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Retain value imports beside erased type imports

Task: Import both a type and a value from one module.

The type and value namespaces have different runtime roles even when declarations share a source module. The value must remain packaged and resolvable.

```typescript
await withProject({ 'model.mts': 'export type Item = { id: string }; export const prefix = \'ready\';', 'main.mts': 'import { prefix, type Item } from \'./model.mjs\'; const item: Item = { id: \'A\' }; console.log(prefix + \':\' + item.id);' }, async directory => {
  const compiled = compile(directory);
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const emitted = await readFile(join(directory, 'compiled', 'main.mjs'), 'utf8');
  assert.ok(emitted.includes('./model.mjs'));
  assert.equal(runModule(directory).stdout.trim(), 'ready:A');
});
```

**Expected:** value dependency remains; runtime prints ready:A.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
