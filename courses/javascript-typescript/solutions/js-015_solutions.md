# js-015: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Tests make a behavioral claim executable. A useful test fails when a plausible implementation error is introduced. Merely calling a function without checking the result is weak evidence. Node supplies an assertion library and a built-in test runner, so this lesson needs no package installation. The runner discovers declared tests, awaits returned asynchronous work, reports failures, and sets a nonzero process exit status when a test fails.

A test should distinguish setup, action and observation. Fixtures should be small enough to explain the expected result independently. Check a normal case, an empty or boundary case, and a controlled failure. Avoid asserting incidental details such as an entire stack trace or machine-specific duration unless those details are themselves the contract. A failure message should name the behavior that broke.

Async tests must return or await their work. A Promise started and forgotten can outlive its test and create misleading results. Failure testing also needs the right assertion: throws inspects synchronous exceptions; rejects awaits a rejection. This lesson starts an actual node --test child for each exercise, preserving stdout and stderr separately and checking the child status. That proves the runner detected both deliberately passing and deliberately failing fixtures, instead of printing an invented test summary.

**Test oracle:** An independent expectation used to judge behavior.

**Negative test:** A test asserting the intended handling of an invalid or failing case.

**Regression:** A previously repaired behavior breaking again.

**Async test lifetime:** The work the runner can observe through the returned or awaited Promise.

## Reading the implementation

import test from node:test declares tests, while node:assert/strict provides exact assertions. test(name, async () => ...) awaits the returned Promise. assert.deepEqual compares structured values; assert.throws and assert.rejects check distinct failure channels. The child runner uses process.execPath, a fixed argument array and shell:false through spawnSync. A temporary source file belongs to the exercise and is removed in finally. A nonzero child result is expected only in the deliberately broken fixture.

## Exercise 1: Run a passing pure-function test: change one input

Task: Copy Example A into a scratch `main.mjs` and change `assert.equal(2` to `assert.equal(3`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The child actually evaluates an assertion through the built-in runner. Process status supplies a machine-readable success signal; text is retained for diagnosis.

The unchanged code is the exercise block of Example A:

```javascript
const result = await runTests("test('addition', () => { assert.equal(2 + 3, 5); });");
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 1/u);
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal(result.status, 0, result.stderr + result.stdout)`. Restoring the original line brings back the worked observation: child exit status 0; one passing test.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(result.status, 0, result.stderr + result.stdout)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Prove a wrong result fails the runner: debug a regression

Task: A regression changed one token in Example B, so one line now reads `assert.equal(3`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

A test suite that never fails cannot establish that its checks are connected. This controlled mutation proves that the assertion reaches the runner and influences the exit result.

The unchanged code is the exercise block of Example B:

```javascript
const result = await runTests("test('deliberate regression', () => { assert.equal(2 + 3, 6); });");
assert.notEqual(result.status, 0);
assert.match(result.stdout, /# fail 1/u);
assert.match(result.stdout, /AssertionError/u);
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.notEqual(result.status, 0)`; after it the line reads `assert.equal(2` again and nonzero child exit; one failing test.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.notEqual(result.status, 0)` for this input.

## Exercise 3: Await an asynchronous test

Task: Declare an async test that awaits Promise resolution before checking the value.

Returning the async function Promise gives the runner ownership of its lifetime. A detached Promise would need separate handling and could escape the intended observation window.

```javascript
const result = await runTests(
  "test('awaited value', async () => { const value = await Promise.resolve(7); assert.equal(value, 7); });",
);
assert.equal(result.status, 0, result.stderr + result.stdout);
```

**Expected:** child exit status 0.

**Verify:** Keep a check equivalent to `assert.equal(result.status, 0, result.stderr + result.stdout)`. As a control, change `Promise.resolve(7);` to `Promise.resolve(8);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Check rejection with rejects

Task: Assert that an async operation rejects with a RangeError.

An async function converts its thrown error into Promise rejection. assert.throws would inspect only the immediate call and therefore test the wrong channel.

```javascript
const result = await runTests(
  "test('async boundary', async () => { await assert.rejects(async () => { throw new RangeError('negative'); }, RangeError); });",
);
assert.equal(result.status, 0, result.stderr + result.stdout);
```

**Expected:** child exit status 0.

**Verify:** Keep a check equivalent to `assert.equal(result.status, 0, result.stderr + result.stdout)`. As a control, change `assert.equal(result.status, 0, result.stderr + result.stdout);` to `assert.equal(result.status, 1, result.stderr + result.stdout);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 5: Cover a table of boundary cases

Task: Use a table for sums of empty, singleton and signed arrays.

The cases share a mechanism but target different failure boundaries. An explicit reduction identity makes the empty case valid rather than silently excluding it from coverage.

```javascript
const body = `for (const [name, values, expected] of [['empty', [], 0], ['one', [4], 4], ['signed', [-2, 2], 0]]) {
  test(name, () => assert.equal(values.reduce((sum, value) => sum + value, 0), expected));
}`;
const result = await runTests(body);
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 3/u);
```

**Expected:** three passing child tests.

**Verify:** Keep a check equivalent to `assert.equal(result.status, 0, result.stderr + result.stdout)`. As a control, change `0` to `1`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 6: Keep fixtures independent

Task: Create a fresh array inside each test and mutate it in only one test.

A fresh fixture prevents one test from making another pass or fail through leftover state. Ordering assumptions often conceal a shared-state defect rather than a product requirement.

```javascript
const result = await runTests(
  "test('mutate local', () => { const rows = [1]; rows.push(2); assert.deepEqual(rows, [1,2]); });\ntest('fresh local', () => { const rows = [1]; assert.deepEqual(rows, [1]); });",
);
assert.equal(result.status, 0, result.stderr + result.stdout);
assert.match(result.stdout, /# pass 2/u);
```

**Expected:** two tests pass without shared mutable state.

**Verify:** Keep a check equivalent to `assert.equal(result.status, 0, result.stderr + result.stdout)`. As a control, change `1` to `2`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
