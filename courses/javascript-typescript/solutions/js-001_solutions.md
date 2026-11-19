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

## Exercise 1: Inspect the actual host: predict an edited check

Task: Copy Example A into a scratch `main.mjs` and change `assert.equal(Number(process.versions.node.split('.')[0]), 24);` to `assert.equal(Number(process.versions.node.split('.')[1]), 24);` inside its check. Before running it, predict whether the check still passes and explain why; then restore it.

The version check verifies the actual process rather than trusting a file extension. The prepared profile is the supported baseline for later host APIs.

The unchanged code is the exercise block of Example A:

```javascript
assert.equal(Number(process.versions.node.split('.')[0]), 24);
assert.equal(process.release.name, 'node');
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal(Number(process.versions.node.split('.')[0]), 24)`. Restoring the original line brings back the worked observation: major version 24; process.release.name is node.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and explain why the edited check rejects the values that `assert.equal(Number(process.versions.node.split('.')[0]), 24)` accepts. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Distinguish browser globals: diagnose an edited check

Task: A careless edit changed a check in Example B so that it reads `assert.equal(typeof window, 'undefined!');`. Run Example B with that line, explain why the edited check now fails for the same program state, and restore it.

A browser DOM lesson cannot be validated by a Node run that never had a document. Later browser chapters use separate real HTML fixtures.

The unchanged code is the exercise block of Example B:

```javascript
assert.equal(typeof document, 'undefined');
assert.equal(typeof window, 'undefined');
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.equal(typeof window, 'undefined')`; after it the line reads `assert.equal(typeof window, 'undefined');` again and both undefined.

**Verify:** Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that `assert.equal(typeof window, 'undefined')` accepts.

## Exercise 3: Use language arithmetic independently of host APIs

Task: Calculate 2+3 and compare the numeric result with a string.

The arithmetic belongs to the language. The strict assertion distinguishes the numeric value from a textual representation.

```javascript
const total = 2 + 3;
assert.equal(total, 5);
assert.notEqual(total, '5');
```

**Expected:** number 5; not strictly equal to string 5.

**Verify:** Keep a check equivalent to `assert.equal(total, 5)`. As a control, change `const total = 2 + 3;` to `const total = 2 - 3;`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Inspect module identity

Task: Read import.meta.url and confirm it identifies the current module.

Module identity is useful for resolving local resources without assuming the current working directory. It is not a network download request.

```javascript
assert.equal(new URL(import.meta.url).protocol, 'file:');
assert.ok(import.meta.url.endsWith('.mjs'));
```

**Expected:** a file URL ending in .mjs in the classroom.

**Verify:** Keep a check equivalent to `assert.ok(import.meta.url.endsWith('.mjs'))`. As a control, change `assert.ok(import.meta.url.endsWith('.mjs'));` to `assert.ok(import.meta.url.endsWith('.mjs!'));` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

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

**Verify:** Keep a check equivalent to `assert.equal(receiver(), undefined)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

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

**Verify:** Keep a check equivalent to `assert.equal(value, 7)`. As a control, change `const pending = Promise.resolve(7);` to `const pending = Promise.resolve(8);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
