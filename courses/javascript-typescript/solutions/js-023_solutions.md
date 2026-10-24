# js-023: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Type operators can derive one static description from another, reducing duplicated declarations that drift apart. A mapped type iterates over a type's property keys, changing their value types or modifiers. Pick selects known fields, Omit excludes them, Partial makes immediate properties optional, and Readonly restricts immediate writes. These operators change the checker-visible shape, not the runtime object. Assigning a wider record to Omit<SecretRecord, 'secret'> does not remove the secret bytes.

Conditional types select a result type based on an assignability relation. When the checked side is a naked type parameter, applying the conditional to a union distributes across its members. Wrapping both sides in tuples changes the test to treat the union as a whole. This matters when a utility unexpectedly returns a union of arrays rather than one array whose elements may have several types.

infer introduces a type variable extracted from a matched shape, such as the element type of an array. Built-in utilities such as ReturnType and Awaited express common relations. They do not inspect runtime values, execute a function, wait for a Promise or validate an endpoint response. Use type-level transformations to model real API relationships; keep runtime selection, validation and serialization explicit.

**Mapped type:** A type constructed by transforming a set of property keys.

**Conditional type:** A type-level branch based on assignability.

**Distributivity:** Applying a conditional independently to members of a union.

**Type derivation:** Describing one API shape in terms of another without runtime transformation.

## Reading the implementation

A mapped type uses [K in keyof T] to visit each property key. A modifier such as readonly or an optional question mark affects the generated property declaration. A conditional T extends U ? X : Y chooses a static result; infer names a matched component. The satisfies operator checks compatibility while retaining the expression's more specific inferred shape. It can catch missing or extra literal keys without replacing the runtime object or adding validation code.

## Exercise 1: Map a record into field flags

Task: Create a boolean flag type from id and count fields.

The mapped type follows the source keys, so adding a field to Row creates a new required flag. The actual object still needs to be constructed by ordinary code.

```typescript
type Row = { id: string; count: number };
type Flags<T> = { [K in keyof T]: boolean };
const flags: Flags<Row> = { id: true, count: false };
assert.deepEqual(flags, { id: true, count: false });
function negativeTypeCheck(): void {
  // @ts-expect-error Every Row key must have a flag.
  const incomplete: Flags<Row> = { id: true };
  void incomplete;
}
void negativeTypeCheck;
```

**Expected:** id true and count false; a missing flag is a compile error.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Prove Omit does not remove runtime secrets

Task: Assign a wider record to an Omit type, then compare with an explicit public projection.

Type erasure makes this a concrete data-exposure risk. The public object must be constructed with an explicit field allowlist before serialization.

```typescript
type RecordWithSecret = { id: string; secret: string };
const full: RecordWithSecret = { id: 'A', secret: 'fixture-only' };
const view: Omit<RecordWithSecret, 'secret'> = full;
assert.equal(Object.hasOwn(view, 'secret'), true);
const publicRecord: Pick<RecordWithSecret, 'id'> = { id: full.id };
assert.equal(Object.hasOwn(publicRecord, 'secret'), false);
assert.equal(JSON.stringify(publicRecord), '{"id":"A"}');
```

**Expected:** typed view still has secret at runtime; explicit projection does not.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Compare distributed and whole-union array types

Task: Define both conditional utilities and demonstrate their different assignment behavior.

The tuple wrapper prevents the naked parameter from distributing. The difference is between choosing one homogeneous array alternative and allowing a union at each element position.

```typescript
type Distributed<T> = T extends unknown ? T[] : never;
type Whole<T> = [T] extends [unknown] ? T[] : never;
const mixed: Whole<string | number> = ['A', 2];
assert.deepEqual(mixed, ['A', 2]);
function negativeTypeCheck(): void {
  // @ts-expect-error Distributed<string|number> is string[] | number[].
  const invalid: Distributed<string | number> = ['A', 2];
  void invalid;
}
void negativeTypeCheck;
```

**Expected:** whole-union array accepts mixed values; distributed array rejects them.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Infer an array element type

Task: Extract the element type of a readonly array and use it in a checked value.

infer binds the matched component in the true branch. A non-array type would produce never under this utility, making unsupported use explicit.

```typescript
type ElementOf<T> = T extends readonly (infer Item)[] ? Item : never;
const value: ElementOf<readonly number[]> = 7;
assert.equal(value, 7);
function negativeTypeCheck(): void {
  // @ts-expect-error The extracted element type is number.
  const invalid: ElementOf<readonly number[]> = 'seven';
  void invalid;
}
void negativeTypeCheck;
```

**Expected:** element type permits number 7 and rejects text.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Derive an asynchronous result type without executing it

Task: Use ReturnType and Awaited for a small async function, then actually call it separately.

The type aliases perform no I/O and no waiting. The await expression is the actual runtime operation, and the assertion compares its observed result.

```typescript
async function load(): Promise<{ count: number }> { return { count: 3 }; }
type Loaded = Awaited<ReturnType<typeof load>>;
const expected: Loaded = { count: 3 };
assert.deepEqual(await load(), expected);
```

**Expected:** declared resolved shape and actual result both have count 3.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Check a configuration with satisfies

Task: Require exactly the literal success/failure keys on a label table.

satisfies checks the expression against the required relation without functioning as a runtime parser. Dynamic external keys still need validation before they become trusted configuration.

```typescript
const labels = { success: 'Ready', failure: 'Retry' } satisfies Record<'success' | 'failure', string>;
assert.equal(labels.success, 'Ready');
function negativeTypeCheck(): void {
  // @ts-expect-error typo is not a permitted literal key and failure is absent.
  const invalid = { success: 'Ready', typo: 'Retry' } satisfies Record<'success' | 'failure', string>;
  void invalid;
}
void negativeTypeCheck;
```

**Expected:** valid table remains usable; misspelled literal key is a compiler error.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
