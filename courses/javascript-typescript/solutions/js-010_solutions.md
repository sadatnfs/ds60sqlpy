# js-010: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A module is both a namespace and a dependency boundary. An ES module declares imports and exports before its body executes. The loader resolves dependencies, links the bindings, then evaluates the graph. An imported binding observes the exporting module's current binding; it is not a copied snapshot. Importing the same resolved module URL again normally returns the cached module namespace and does not repeat its initialization.

Node uses .mjs to select ES module syntax explicitly. Relative imports require the intended filename extension. Bare package names use package resolution rules; node: names identify built-in modules. CommonJS uses a different export object and loading model. Interoperability is useful, but guessing that an arbitrary CommonJS property will become a named ES export is fragile. This lesson imports a CommonJS default export deliberately and keeps ESM bindings explicit.

The fixtures create tiny source files in a newly allocated temporary directory, import them, and remove only that directory afterward. They do not install a package or edit the repository. Unique directory URLs avoid accidental cache sharing between exercises. A production module should usually avoid expensive side effects at import time: top-level file writes, network requests or background listeners make dependency loading itself operational work.

**Live binding:** An imported name observes updates made to the exporting binding.

**Module namespace:** The read-only view of a module's exported bindings.

**Resolution:** Mapping a module specifier to the module that will be loaded.

**Module cache:** Reuse of an already loaded module for its resolved identity.

## Reading the implementation

An export declaration exposes a binding. import() returns a Promise for the module namespace, so asynchronous loading must be awaited. pathToFileURL converts a platform filesystem path to a correctly encoded file URL; concatenating file: with a raw path fails for spaces and reserved characters. A namespace property cannot be reassigned by the importer, although exported functions may update their own module state. finally runs cleanup after success and after an import rejection.

## Exercise 1: Observe a live binding

Task: Import a mutable counter and its increment function, then inspect the count before and after incrementing.

The importer receives a binding view. Copying count into a local number would instead preserve the value read at that moment. The distinction becomes visible only after the exporter changes state.

```javascript
await withModules(
  { 'counter.mjs': 'export let count = 0; export function increment() { count += 1; }' },
  async (directory) => {
    const module = await import(pathToFileURL(join(directory, 'counter.mjs')).href);
    assert.equal(module.count, 0);
    module.increment();
    assert.equal(module.count, 1);
  },
);
```

**Expected:** count changes from 0 to 1 through the imported namespace.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Resolve a relative dependency

Task: Create a main module importing twice from ./math.mjs, then call its export.

The relative path is resolved from the importing file, not from the process working directory. Naming the .mjs extension makes the loader contract explicit.

```javascript
await withModules(
  {
    'math.mjs': 'export const twice = value => 2 * value;',
    'main.mjs': "import { twice } from './math.mjs'; export const answer = twice(4);",
  },
  async (directory) => {
    const module = await import(pathToFileURL(join(directory, 'main.mjs')).href);
    assert.equal(module.answer, 8);
  },
);
```

**Expected:** answer equals 8.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Prove cached module identity

Task: Import one URL twice and compare the namespace and exported object.

A module is not a factory that automatically resets on each import. For independent instances, export a factory function and call it explicitly.

```javascript
await withModules({ 'state.mjs': 'export const state = { visits: 0 };' }, async (directory) => {
  const url = pathToFileURL(join(directory, 'state.mjs')).href;
  const first = await import(url);
  const second = await import(url);
  assert.equal(first, second);
  assert.equal(first.state, second.state);
});
```

**Expected:** both namespace and object identities are shared.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Inspect CommonJS interoperability

Task: Import a .cjs file exporting an object through its default binding.

The default binding is the intentional CommonJS export-object boundary here. This example does not depend on heuristic named-export detection.

```javascript
await withModules({ 'legacy.cjs': "module.exports = { label: 'legacy' };" }, async (directory) => {
  const module = await import(pathToFileURL(join(directory, 'legacy.cjs')).href);
  assert.equal(module.default.label, 'legacy');
});
```

**Expected:** default.label equals legacy.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Reject a missing dependency

Task: Import a module with a nonexistent relative dependency and preserve the loader error code.

Missing dependency resolution is a loader failure before useful module evaluation. Catching every import error and returning an empty object would disguise a broken dependency graph.

```javascript
await withModules({ 'broken.mjs': "import './missing.mjs';" }, async (directory) => {
  await assert.rejects(
    import(pathToFileURL(join(directory, 'broken.mjs')).href),
    (error) => error.code === 'ERR_MODULE_NOT_FOUND',
  );
});
```

**Expected:** ERR_MODULE_NOT_FOUND.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Respect namespace ownership

Task: Attempt to assign an exported binding from the importer.

Live does not mean writable from every importer. The exporter owns assignment to its binding. Expose a deliberate operation when mutation is part of the public contract.

```javascript
await withModules({ 'fixed.mjs': 'export let value = 3;' }, async (directory) => {
  const module = await import(pathToFileURL(join(directory, 'fixed.mjs')).href);
  assert.throws(() => {
    module.value = 9;
  }, TypeError);
  assert.equal(module.value, 3);
});
```

**Expected:** TypeError; exported value remains 3.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
