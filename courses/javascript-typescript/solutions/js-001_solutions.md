# js-001: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

JavaScript is a language; Node and browsers are hosts that provide different APIs around it. Arithmetic, objects, functions and Promises belong to the language. Node adds process information, filesystem access and server APIs. Browsers add a document tree, events, layout and browser storage. Some APIs such as URL and fetch exist in both hosts, but that overlap does not make every program portable. A Node process has no document object to edit.

This course uses ES modules with the .mjs extension for JavaScript. Modules have their own scope and run in strict mode. Imports name dependencies explicitly, and top-level await can wait for asynchronous setup. A file being syntactically valid does not mean its host dependencies exist. The first lesson makes the actual Node version, module identity and missing browser globals observable before introducing larger programs.

**ECMAScript:** The standardized JavaScript language semantics.

**Host:** The environment supplying APIs around the language.

**ES module:** A file with explicit imports/exports and its own strict scope.

## Reading the implementation

An import statement loads a declared module binding. The node: prefix identifies a built-in Node module rather than an installed package. const creates a binding that cannot be reassigned, while the object it references may still be mutable. import.meta.url identifies the current ES module. typeof can inspect an undeclared host global without throwing, which is useful for distinguishing Node from a browser without pretending to implement the missing API.

## Exercise 1: Inspect the actual host: predict an edited check

Task: In a scratch copy of Example A, change `assert.equal(Number(process.versions.node.split('.')[0]), 24);` to `assert.equal(Number(process.versions.node.split('.')[1]), 24);` inside its check. Does the check still pass?

The version check verifies the actual process rather than trusting a file extension. The prepared profile is the supported baseline for later host APIs.

The unchanged code is the exercise block of Example A:

```javascript
assert.equal(Number(process.versions.node.split('.')[0]), 24);
assert.equal(process.release.name, 'node');
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(Number(process.versions.node.split('.')[1]), 24);`. Restoring `assert.equal(Number(process.versions.node.split('.')[0]), 24);` brings back: major version 24; process.release.name is node.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `assert.equal(Number(process.versions.node.split('.')[0]), 24);`.

## Exercise 2: Distinguish browser globals: diagnose an edited check

Task: Example B's check was edited to read `assert.equal(typeof window, 'undefined!');`. Run it, explain the failure and restore the original.

A browser DOM lesson cannot be validated by a Node run that never had a document. Later browser chapters use separate real HTML fixtures.

The unchanged code is the exercise block of Example B:

```javascript
assert.equal(typeof document, 'undefined');
assert.equal(typeof window, 'undefined');
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(typeof window, 'undefined!');`. Restoring `assert.equal(typeof window, 'undefined');` brings back: both undefined.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Use language arithmetic independently of host APIs

Task: Calculate 2+3 and compare the numeric result with a string.

The arithmetic belongs to the language. The strict assertion distinguishes the numeric value from a textual representation.

```javascript
const total = 2 + 3;
assert.equal(total, 5);
assert.notEqual(total, '5');
```

**Expected:** number 5; not strictly equal to string 5.

**Verify:** Keep `assert.equal(total, 5)`. Control: changing `const total = 2 + 3;` to `const total = 2 - 3;` must make that check fail; then restore it.

## Exercise 4: Inspect module identity

Task: Read import.meta.url and confirm it identifies the current module.

Module identity is useful for resolving local resources without assuming the current working directory. It is not a network download request.

```javascript
assert.equal(new URL(import.meta.url).protocol, 'file:');
assert.ok(import.meta.url.endsWith('.mjs'));
```

**Expected:** a file URL ending in .mjs in the classroom.

**Verify:** Keep `assert.ok(import.meta.url.endsWith('.mjs'))`. Control: editing it to `assert.ok(import.meta.url.endsWith('.mjs!'));` must make the check fail; then restore it.

## Exercise 5: Observe strict module function calls

Task: Call an ordinary function without a receiver and inspect this.

ES modules use strict semantics. The callsite determines this for an ordinary function; it is not automatically the global object.

```javascript
function receiver() {
  return this;
}
assert.equal(receiver(), undefined);
```

**Expected:** this is undefined.

**Verify:** Keep the check `assert.equal(receiver(), undefined)`; name an input that would make it fail and the value that changes.

## Exercise 6: Await a real Promise result

Task: Resolve 7 through a Promise and await it before checking.

A Promise is a handle for eventual completion. Checking the handle is different from checking the resolved value after the asynchronous boundary.

```javascript
const pending = Promise.resolve(7);
assert.ok(pending instanceof Promise);
const value = await pending;
assert.equal(value, 7);
```

**Expected:** observed value 7 after await.

**Verify:** Keep `assert.equal(value, 7)`. Control: changing `const pending = Promise.resolve(7);` to `const pending = Promise.resolve(8);` must make that check fail; then restore it.

## After comparison

Fresh case: predict what `typeof globalThis.setTimeout` and `typeof globalThis.structuredClone` report in Node 24, then decide whether either belongs to ECMAScript itself. Both are host APIs, even though Node and browsers each provide them. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
