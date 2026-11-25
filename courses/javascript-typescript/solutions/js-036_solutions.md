# js-036: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A package is a public interface plus the files and metadata needed to implement it. The exports map declares supported entry points. Consumers importing an undeclared internal path receive a loader error, even if a file exists on disk. This helps maintain an API boundary but is not filesystem access control for a hostile process with direct disk access.

A package version and an engine declaration communicate compatibility expectations. They do not prove the implementation obeys semantic-versioning conventions, and Node's module loader does not automatically enforce every package engines field. A tested runtime contract must check the actual executable and supported behavior. A breaking change can be behavioral even if TypeScript signatures or exported function names remain unchanged.

Reproducible preparation needs more than a top-level version range. Lockfiles record resolved dependency versions and integrity information; the package manager version, platform-specific dependencies, runtime, installation flags and build inputs can still matter. npm ci is the usual strict lockfile installation route, but this default lesson does not install dependencies or run lifecycle scripts. Its fixtures are small authored packages under an owned temporary node_modules directory so resolution can be observed offline.

The examples create a public entry, an explicit subpath and a private implementation file, then run real Node imports. A SHA-256 manifest demonstrates content identity and detects an intentional local modification. A hash proves equality to an expected byte sequence, not trustworthiness, licensing or correctness. Keep source identity, dependency resolution and runtime behavior as separate pieces of release evidence.

**Exports map:** The declared package entry and subpath interface.

**Dependency lock:** A record of resolved dependency artifacts and metadata.

**Engine declaration:** Package metadata describing an intended runtime requirement.

**Content identity:** A digest tying evidence to exact file bytes.

## Reading the implementation

package.json type:module selects ESM for .js files in its package scope, while .mjs is explicit independently. exports maps package entry and subpath names to intended files. Bare package imports resolve from the importing module's location. A child main.mjs in the temporary project imports the authored package through node_modules, exercising the real loader. The helper captures exit status and stderr, cleans up its directory and never runs a shell or package installation.

## Exercise 1: Import the public package entry: predict an edited check

Task: In a scratch copy of Example A, change `assert.equal(result.stdout.trim(), '1');` to `assert.equal(result.stdout.trim(), '2');` inside its check. Does the check still pass?

The import uses normal package-name resolution from the temporary main module. It does not bypass the exports map with an absolute file URL.

The unchanged code is the exercise block of Example A:

```javascript
await withPackage(async (directory) => {
  const result = runImport(
    directory,
    'import { version } from \'course-fixture\'; console.log(version);',
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '1');
});
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(result.stdout.trim(), '2');`. Restoring `assert.equal(result.stdout.trim(), '1');` brings back: actual child prints 1.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `assert.equal(result.stdout.trim(), '1');`.

## Exercise 2: Use an explicitly exported subpath: debug a regression

Task: A regression made one Example B line read `console.log(twice(4));`. Locate and repair it without editing the check.

A public subpath is part of the package interface. Its name can remain stable even if the internal file layout later changes.

The unchanged code is the exercise block of Example B:

```javascript
await withPackage(async (directory) => {
  const result = runImport(
    directory,
    'import { twice } from \'course-fixture/math\'; console.log(twice(3));',
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '6');
});
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(result.stdout.trim(), '6')`. Restoring `console.log(twice(3));` brings back: actual child prints 6.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Reject an undeclared private path

Task: Attempt a package-name import of private.mjs even though the file exists.

The loader enforces the declared package interface. A consumer depending on internal paths would otherwise make ordinary package refactoring a compatibility hazard.

```javascript
await withPackage(async (directory) => {
  const result = runImport(directory, 'import \'course-fixture/private.mjs\';');
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /ERR_PACKAGE_PATH_NOT_EXPORTED/u);
});
```

**Expected:** nonzero child status with ERR_PACKAGE_PATH_NOT_EXPORTED.

**Verify:** Keep `assert.match(result.stderr, /ERR_PACKAGE_PATH_NOT_EXPORTED/u)`. Control: changing `const result = runImport(directory, 'import \'course-fixture/private.mjs\';');` to `const result = runImport(directory, 'import \'course-fixture/private.mjs\';!');` must make that check fail; then restore it.

## Exercise 4: Observe that engines is metadata rather than a loader gate

Task: Read the fixture engine declaration requiring Node99, then import its entry with the actual runtime.

Package-manager policy may warn or reject based on configuration, but this demonstrates the actual Node loader boundary. A declared requirement is not runtime qualification.

```javascript
await withPackage(async (directory) => {
  const manifest = JSON.parse(
    await readFile(join(directory, 'node_modules/course-fixture/package.json'), 'utf8'),
  );
  assert.equal(manifest.engines.node, '>=99');
  assert.ok(Number(process.versions.node.split('.')[0]) < 99);
  assert.equal(runImport(directory, 'import \'course-fixture\';').status, 0);
});
```

**Expected:** metadata says >=99; ordinary import still succeeds.

**Verify:** Keep `assert.equal(runImport(directory, 'import \'course-fixture\';').status, 0)`. Control: editing it to `assert.equal(runImport(directory, 'import \'course-fixture\';!').status, 0);` must make the check fail; then restore it.

## Exercise 5: Detect exact source tampering through a digest

Task: Hash the public source, change only that owned file, and compare hashes.

The digest identifies bytes, so even a valid replacement implementation changes artifact identity. It does not tell whether version 1 or version 2 has better behavior.

```javascript
await withPackage(async (directory) => {
  const path = join(directory, 'node_modules/course-fixture/index.mjs');
  const before = digest(await readFile(path));
  await writeFile(path, 'export const version = 2;');
  const after = digest(await readFile(path));
  assert.notEqual(after, before);
  assert.equal(before.length, 64);
});
```

**Expected:** digest changes after modification.

**Verify:** Keep `assert.equal(before.length, 64)`. Control: editing it to `assert.equal(before.length, 65);` must make the check fail; then restore it.

## Exercise 6: Preserve a versioned behavior contract

Task: Import the arithmetic subpath and assert both a normal and a boundary input in the child.

An exported name existing is weaker than its behavior matching the consumer contract. Boundary tests help detect a breaking semantic change that leaves the interface shape untouched.

```javascript
await withPackage(async (directory) => {
  const result = runImport(
    directory,
    'import { strict as assert } from \'node:assert\'; import { twice } from \'course-fixture/math\'; assert.equal(twice(0), 0); assert.equal(twice(-2), -4);',
  );
  assert.equal(result.status, 0, result.stderr);
});
```

**Expected:** child exits successfully for twice(0)=0 and twice(-2)=-4.

**Verify:** Keep `assert.equal(result.status, 0, result.stderr)`. Control: changing `assert.equal(twice(0)` to `assert.equal(twice(1)` must make that check fail; then restore it.

## After comparison

Fresh case: add a `./format` subpath to the fixture package. Predict the import result before and after listing it in `exports`, and hash the new file to record its identity. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
