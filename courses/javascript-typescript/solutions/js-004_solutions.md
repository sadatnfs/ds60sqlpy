# js-004: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Functions define reusable computations, and lexical scope determines which bindings a function can read. A closure retains access to bindings from the environment where it was created. Those bindings can hold state across calls, which is useful for a small counter or factory. Closures do not automatically copy every captured value. A shared var binding in a loop can make several functions observe the same final value, while let creates the intended per-iteration bindings.

Default parameters apply when an argument is undefined, not when it is null. Ordinary function this depends on the callsite; arrow functions capture this lexically. A clear function contract should distinguish arguments, returned values, mutable captured state and receiver dependence. Prefer explicit parameters when a closure would hide important dependencies.

**Lexical scope:** Binding lookup determined by where code is written.

**Closure:** A function retaining access to its surrounding bindings.

**Default parameter:** A fallback used when the supplied argument is undefined.

**Receiver:** The this value used by an ordinary method call.

## Reading the implementation

A function declaration introduces a named callable; an arrow expression creates a function value. Returning a nested function forms a closure over its surrounding bindings. let and const are block-scoped, while var is function-scoped. The default syntax name=value is evaluated when the argument is undefined. Use call or bind only when receiver behavior is part of the contract, not as a substitute for understanding the callsite.

## Exercise 1: Call a pure function

Task: Use add with 2, 3 and with negative 1, 1.

The function depends only on its arguments and changes no external state. Boundary examples can be tested independently.

```javascript
function add(left, right) { return left + right; }
assert.equal(add(2, 3), 5);
assert.equal(add(-1, 1), 0);
```

**Expected:** 5 and 0.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Build independent closures

Task: Create two counters; increment the first twice and the second once.

Each factory call creates a separate captured binding. Equal initial values do not imply shared counter state.

```javascript
const first = counter();
const second = counter();
assert.equal(first(), 1);
assert.equal(first(), 2);
assert.equal(second(), 1);
```

**Expected:** first 1, 2; second 1.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Compare let and var loop capture

Task: Create three closures in a let loop and three in a var loop.

The difference is binding lifetime, not the time the function body was parsed. All var closures share one function-scoped index.

```javascript
const block = [];
for (let index = 0; index < 3; index += 1) block.push(() => index);
const shared = [];
for (var index = 0; index < 3; index += 1) shared.push(() => index);
assert.deepEqual(block.map(fn => fn()), [0, 1, 2]);
assert.deepEqual(shared.map(fn => fn()), [3, 3, 3]);
```

**Expected:** let returns 0, 1, 2; var returns 3, 3, 3.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Distinguish undefined from null defaults

Task: Call a greeting function with no argument, undefined and null.

A default parameter does not define a general missing-value policy. If null is invalid, the function must validate it explicitly.

```javascript
function label(value = 'guest') { return value; }
assert.equal(label(), 'guest');
assert.equal(label(undefined), 'guest');
assert.equal(label(null), null);
```

**Expected:** default used for the first two; null preserved.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Observe an ordinary receiver

Task: Call a method through its object and then with an explicit alternate receiver.

The same function can operate on different receivers. Detaching it and calling without a receiver may produce an error rather than retain the original object.

```javascript
const item = { value: 4, read() { return this.value; } };
assert.equal(item.read(), 4);
assert.equal(item.read.call({ value: 9 }), 9);
```

**Expected:** 4 and 9.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Reject an invalid factory configuration

Task: Create a step counter with nonpositive or noninteger step.

Validate the configuration when the closure is created so every later call can rely on its invariant. Hidden invalid state is harder to diagnose after many calls.

```javascript
assert.throws(() => counter(0), TypeError);
assert.throws(() => counter(1.5), TypeError);
const next = counter(2);
assert.deepEqual([next(), next()], [2, 4]);
```

**Expected:** TypeError for 0 and 1.5; step 2 yields 2, 4.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
