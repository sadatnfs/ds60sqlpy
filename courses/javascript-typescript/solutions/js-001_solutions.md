# js-001: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

JavaScript is a language; Node and browsers are hosts that provide different APIs around it. Arithmetic, objects, functions and Promises belong to the language. Node adds process information, filesystem access and server APIs. Browsers add a document tree, events, layout and browser storage. Some APIs such as URL and fetch exist in both hosts, but that overlap does not make every program portable. A Node process has no document object to edit.

This course uses ES modules with the .mjs extension for JavaScript. Modules have their own scope and run in strict mode. Imports name dependencies explicitly, and top-level await can wait for asynchronous setup. A file being syntactically valid does not mean its host dependencies exist. The first lesson makes the actual Node version, module identity and missing browser globals observable before introducing larger programs.

**ECMAScript:** The standardized JavaScript language semantics.

**Host:** The environment supplying APIs around the language.

**ES module:** A file with explicit imports/exports and its own strict scope.

## Reading the implementation

An import statement loads a declared module binding. The node: prefix identifies a built-in Node module rather than an installed package. const creates a binding that cannot be reassigned, while the object it references may still be mutable. import.meta.url identifies the current ES module. typeof can inspect an undeclared host global without throwing, which is useful for distinguishing Node from a browser without pretending to implement the missing API.

## Exercise 1: Inspect the actual host

Task: Check that the prepared runtime is Node 24 and that process exists.

The version check verifies the actual process rather than trusting a file extension. The prepared profile is the supported baseline for later host APIs.

```javascript
assert.equal(Number(process.versions.node.split('.')[0]), 24);
assert.equal(process.release.name, 'node');
```

**Expected:** major version 24; process.release.name is node.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Distinguish browser globals

Task: Inspect document and window using typeof inside Node.

A browser DOM lesson cannot be validated by a Node run that never had a document. Later browser chapters use separate real HTML fixtures.

```javascript
assert.equal(typeof document, 'undefined');
assert.equal(typeof window, 'undefined');
```

**Expected:** both undefined.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Use language arithmetic independently of host APIs

Task: Calculate 2+3 and compare the numeric result with a string.

The arithmetic belongs to the language. The strict assertion distinguishes the numeric value from a textual representation.

```javascript
const total = 2 + 3;
assert.equal(total, 5);
assert.notEqual(total, '5');
```

**Expected:** number 5; not strictly equal to string 5.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Inspect module identity

Task: Read import.meta.url and confirm it identifies the current module.

Module identity is useful for resolving local resources without assuming the current working directory. It is not a network download request.

```javascript
assert.equal(new URL(import.meta.url).protocol, 'file:');
assert.ok(import.meta.url.endsWith('.mjs'));
```

**Expected:** a file URL ending in .mjs in the classroom.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Observe strict module function calls

Task: Call an ordinary function without a receiver and inspect this.

ES modules use strict semantics. The callsite determines this for an ordinary function; it is not automatically the global object.

```javascript
function receiver() { return this; }
assert.equal(receiver(), undefined);
```

**Expected:** this is undefined.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
