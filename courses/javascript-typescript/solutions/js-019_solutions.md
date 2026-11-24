# js-019: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

TypeScript adds a static checker to JavaScript. The checker reasons about possible values and operations before execution; the emitted program still follows JavaScript semantics. A type annotation does not create a runtime validator, convert a string to a number, or freeze an object. This distinction is essential when data comes from JSON, files, network responses or another program.

Inference lets the checker learn types from initial values and expressions. An explicit annotation is useful at a public boundary or when the intended set of values is broader than the initial expression. Repeating every obvious inferred type adds noise without necessarily improving the contract. Strict checking includes checks such as strictNullChecks and noImplicitAny, but it does not enable every possible compiler option. In particular, this profile does not silently claim exactOptionalPropertyTypes or noUncheckedIndexedAccess.

The prepared route compiles main.mts with TypeScript 5.9.3 using NodeNext resolution and noEmitOnError, then runs the resulting ES module on Node 24. An incorrect typed program is a compiler failure before runtime. Each deliberate negative type example is placed in an uncalled function with @ts-expect-error. The directive requires the next line to produce a compiler diagnostic; if that error disappears, the compiler reports an unused directive. These functions are teaching checks, not code paths to execute or broad permission to suppress errors.

Node 24 can also run main.mts directly: it strips erasable type syntax by default, so node main.mts starts without any compiler. Stripping is not checking. A file whose annotations are wrong still runs under node main.mts, while tsc --noEmit reports the same error without writing output. Only erasable syntax can be stripped: a parameter property or an enum stops node with ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX, and the erasableSyntaxOnly compiler option reports such syntax while checking. This course keeps the compile-then-run route so every exercise is type-checked before it executes.

**Static type:** A compile-time description of values and supported operations.

**Inference:** Deriving a type from code without an explicit annotation.

**Erasure:** Removal of type-only syntax from the emitted JavaScript.

**Unknown boundary:** An external value requiring runtime inspection before trusted use.

## Reading the implementation

A parameter annotation follows its name, and a return annotation follows the parameter list. const often preserves a literal primitive type, whereas let permits later assignment and commonly widens to the primitive category. A type alias names a compile-time description. unknown requires checking before use; any bypasses many checks and should not become the default for external input. The as syntax asserts what the author wants the checker to assume and performs no conversion.

## Exercise 1: Annotate a numeric function: change one input

Task: Copy Example A into a scratch `main.mts` and change `const result = add(2, 3);` to `const result = add(3, 3);`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The annotation describes accepted calls to checked TypeScript code. It is erased during compilation; the emitted function still performs JavaScript addition and would need validation at an untyped boundary.

The unchanged code is the exercise block of Example A:

```typescript
function add(left: number, right: number): number {
  return left + right;
}
const result = add(2, 3);
assert.equal(result, 5);
assert.equal(typeof result, 'number');
function negativeTypeCheck(): void {
  // @ts-expect-error A string is not a numeric argument.
  add('2', 3);
}
void negativeTypeCheck;
```

**Expected:** The changed run fails with an `AssertionError` at `assert.equal(result, 5)`. Restoring `const result = add(2, 3);` brings back: sum 5 with runtime typeof number.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(result, 5)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Show that an assertion does not convert data: debug a regression

Task: A regression changed one token in Example B, so one line now reads `const external: unknown = 'wrong!';`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

This intentionally unsafe assertion demonstrates the escape hatch. The correct repair for external data is a runtime check or parser, not a stronger-looking cast.

The unchanged code is the exercise block of Example B:

```typescript
const external: unknown = 'wrong';
const claimed = external as number;
assert.equal(typeof claimed, 'string');
assert.equal(String(claimed), 'wrong');
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(String(claimed), 'wrong')`. Restoring `const external: unknown = 'wrong';` brings back: the runtime value remains the string wrong.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.equal(String(claimed), 'wrong')` for this input.

## Exercise 3: Compare literal preservation and widening

Task: Use const for a fixed tag and let for a changing text value.

A literal type can describe one exact protocol tag. A mutable binding must allow its intended future values; inference therefore often widens it to string.

```typescript
const fixed = 'ready';
let mutable = 'ready';
mutable = 'done';
function acceptReady(value: 'ready'): string {
  return value;
}
assert.equal(acceptReady(fixed), 'ready');
assert.equal(mutable, 'done');
function negativeTypeCheck(): void {
  // @ts-expect-error mutable is string, not the literal type ready.
  acceptReady(mutable);
}
void negativeTypeCheck;
```

**Expected:** fixed tag remains ready; mutable text can change to done.

**Verify:** Keep a check equivalent to `assert.equal(mutable, 'done')`. As a control, change `mutable = 'done';` to `mutable = 'done!';`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Handle null explicitly under strict checking

Task: Write a length function accepting string or null.

The null branch establishes a runtime fact that the checker can use. A non-null assertion would silence the diagnostic without adding this behavior.

```typescript
function lengthOrZero(value: string | null): number {
  return value === null ? 0 : value.length;
}
assert.equal(lengthOrZero('abc'), 3);
assert.equal(lengthOrZero(null), 0);
function negativeTypeCheck(value: string | null): void {
  // @ts-expect-error value may be null before a guard.
  void value.length;
}
void negativeTypeCheck;
```

**Expected:** length 3 for abc and 0 for null.

**Verify:** Keep a check equivalent to `assert.equal(lengthOrZero(null), 0)`. As a control, change `return value === null ? 0 : value.length;` to `return value === null ? 1 : value.length;`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Observe type erasure through object keys

Task: Declare a record type and create a compatible object.

A type alias is not a constructor or a runtime schema. Code that needs a schema must represent and execute validation separately.

```typescript
type Item = { id: string; count: number };
const item: Item = { id: 'A', count: 2 };
assert.deepEqual(Object.keys(item), ['id', 'count']);
assert.equal('Item' in item, false);
```

**Expected:** runtime keys contain only id and count, with no type alias metadata.

**Verify:** Keep a check equivalent to `assert.equal('Item' in item, false)`. As a control, change `assert.equal('Item' in item, false);` to `assert.equal('Item' in item, true);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Narrow unknown before numeric use

Task: Accept only a finite number from an unknown value.

The typeof branch narrows the static type, while the finite check enforces an additional domain property that ordinary number typing does not guarantee.

```typescript
function doubleFinite(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value))
    throw new TypeError('finite number required');
  return value * 2;
}
assert.equal(doubleFinite(12), 24);
assert.throws(() => doubleFinite('12'), TypeError);
assert.throws(() => doubleFinite(Infinity), TypeError);
```

**Expected:** 12 doubles to 24; string 12 and Infinity reject.

**Verify:** Keep a check equivalent to `assert.equal(doubleFinite(12), 24)`. As a control, change `return value * 2;` to `return value + 2;`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
