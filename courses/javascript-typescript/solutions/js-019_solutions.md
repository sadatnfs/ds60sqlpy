# js-019: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

TypeScript adds a static checker to JavaScript. The checker reasons about possible values and operations before execution; the emitted program still follows JavaScript semantics. A type annotation does not create a runtime validator, convert a string to a number, or freeze an object. This distinction is essential when data comes from JSON, files, network responses or another program.

Inference lets the checker learn types from initial values and expressions. An explicit annotation is useful at a public boundary or when the intended set of values is broader than the initial expression. Repeating every obvious inferred type adds noise without necessarily improving the contract. Strict checking includes checks such as strictNullChecks and noImplicitAny, but it does not enable every possible compiler option. In particular, this profile does not silently claim exactOptionalPropertyTypes or noUncheckedIndexedAccess.

The prepared route compiles main.mts with TypeScript 5.9.3 using NodeNext resolution and noEmitOnError, then runs the resulting ES module on Node 24. An incorrect typed program is a compiler failure before runtime. Each deliberate negative type example is placed in an uncalled function with @ts-expect-error. The directive requires the next line to produce a compiler diagnostic; if that error disappears, the compiler reports an unused directive. These functions are teaching checks, not code paths to execute or broad permission to suppress errors.

**Static type:** A compile-time description of values and supported operations.

**Inference:** Deriving a type from code without an explicit annotation.

**Erasure:** Removal of type-only syntax from the emitted JavaScript.

**Unknown boundary:** An external value requiring runtime inspection before trusted use.

## Reading the implementation

A parameter annotation follows its name, and a return annotation follows the parameter list. const often preserves a literal primitive type, whereas let permits later assignment and commonly widens to the primitive category. A type alias names a compile-time description. unknown requires checking before use; any bypasses many checks and should not become the default for external input. The as syntax asserts what the author wants the checker to assume and performs no conversion.

## Exercise 1: Annotate a numeric function

Task: Define a function accepting two numbers and returning their sum; inspect its runtime value.

The annotation describes accepted calls to checked TypeScript code. It is erased during compilation; the emitted function still performs JavaScript addition and would need validation at an untyped boundary.

```typescript
function add(left: number, right: number): number { return left + right; }
const result = add(2, 3);
assert.equal(result, 5);
assert.equal(typeof result, 'number');
function negativeTypeCheck(): void {
  // @ts-expect-error A string is not a numeric argument.
  add('2', 3);
}
void negativeTypeCheck;
```

**Expected:** sum 5 with runtime typeof number.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Show that an assertion does not convert data

Task: Assert that an unknown string is a number, then inspect the actual runtime type.

This intentionally unsafe assertion demonstrates the escape hatch. The correct repair for external data is a runtime check or parser, not a stronger-looking cast.

```typescript
const external: unknown = 'wrong';
const claimed = external as number;
assert.equal(typeof claimed, 'string');
assert.equal(String(claimed), 'wrong');
```

**Expected:** the runtime value remains the string wrong.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Compare literal preservation and widening

Task: Use const for a fixed tag and let for a changing text value.

A literal type can describe one exact protocol tag. A mutable binding must allow its intended future values; inference therefore often widens it to string.

```typescript
const fixed = 'ready';
let mutable = 'ready';
mutable = 'done';
function acceptReady(value: 'ready'): string { return value; }
assert.equal(acceptReady(fixed), 'ready');
assert.equal(mutable, 'done');
function negativeTypeCheck(): void {
  // @ts-expect-error mutable is string, not the literal type ready.
  acceptReady(mutable);
}
void negativeTypeCheck;
```

**Expected:** fixed tag remains ready; mutable text can change to done.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Narrow unknown before numeric use

Task: Accept only a finite number from an unknown value.

The typeof branch narrows the static type, while the finite check enforces an additional domain property that ordinary number typing does not guarantee.

```typescript
function doubleFinite(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError('finite number required');
  return value * 2;
}
assert.equal(doubleFinite(12), 24);
assert.throws(() => doubleFinite('12'), TypeError);
assert.throws(() => doubleFinite(Infinity), TypeError);
```

**Expected:** 12 doubles to 24; string 12 and Infinity reject.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
