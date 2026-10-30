# js-021: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

TypeScript object types describe the properties an operation requires. Compatibility is largely structural: an object with the required fields can be accepted even if it was not created by a named class. A fresh object literal receives additional excess-property checking, which catches likely misspellings, but assigning the same wider object through a variable can be allowed. Neither rule is a runtime exact-schema validator.

readonly restricts writes through a particular typed view. It does not freeze the runtime object, and another mutable alias may still change it. A shallow readonly property containing a mutable object also leaves that nested object mutable unless its type says otherwise. Readonly arrays prevent mutating methods through their interface, but ordinary copy and transformation operations remain available.

An optional property may be absent. Under this route's strict profile, reading it produces a value that may be undefined. The profile does not enable exactOptionalPropertyTypes, so explicit undefined assignment has different checking behavior from a stricter configuration that distinguishes absence from an explicitly present undefined. Be precise about the actual compiler flags and the wire-format policy. JSON serialization can omit undefined fields, further separating runtime presence from serialized presence.

**Structural compatibility:** Acceptance based on required members rather than a declared class identity.

**Excess-property checking:** Extra scrutiny of fresh object literals for unexpected properties.

**Readonly view:** A type-level restriction on writes through a particular reference.

**Optional property:** A field that may be absent and must be handled accordingly.

## Reading the implementation

Use property?: Type for optional fields and readonly property: Type for a restricted view. Readonly<T> is shallow: it changes the write permissions of the immediate fields in the type, not the underlying objects. readonly T[] or ReadonlyArray<T> disallows push through that reference. Object.freeze is a runtime operation with its own shallow boundary. Object.hasOwn can distinguish property presence independently of its value.

## Exercise 1: Use structural compatibility

Task: Pass a wider named object with id and count to a function requiring only id.

Structural acceptance is useful for small interfaces, but does not strip extra fields. Treating an accepted type as an exact serialization schema can leak fields that still exist at runtime.

```typescript
function label(value: { id: string }): string {
  return value.id;
}
const wider = { id: 'A', count: 2 };
assert.equal(label(wider), 'A');
assert.equal(wider.count, 2);
function negativeTypeCheck(): void {
  // @ts-expect-error A fresh literal is checked for excess properties.
  label({ id: 'A', count: 2 });
}
void negativeTypeCheck;
```

**Expected:** label A; original count remains 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Observe mutation through an alias

Task: Create a readonly view of a mutable record, then mutate the original reference.

The view and original reference point to the same object. Readonly is a static access restriction, not a historical snapshot or deep immutability guarantee.

```typescript
const mutable = { count: 1 };
const view: Readonly<{ count: number }> = mutable;
mutable.count = 4;
assert.equal(view.count, 4);
function negativeTypeCheck(): void {
  // @ts-expect-error Writes through the readonly view are forbidden.
  view.count = 9;
}
void negativeTypeCheck;
```

**Expected:** readonly view observes count changing from 1 to 4.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Handle absent and zero-valued optional counts

Task: Use a nullish fallback on an optional count.

The optional field forces the caller to account for undefined. Nullish fallback preserves a valid zero, unlike a truthiness fallback.

```typescript
type Options = { count?: number };
function count(options: Options): number {
  return options.count ?? 10;
}
assert.equal(count({}), 10);
assert.equal(count({ count: 0 }), 0);
```

**Expected:** absent becomes 10; explicit 0 remains 0.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Distinguish runtime presence from undefined

Task: Compare an absent property with an explicitly present undefined property.

This code matches the actual compiler profile without exactOptionalPropertyTypes. Serialization can erase a runtime distinction, so patch/update APIs must define whether absence and explicit removal differ.

```typescript
const absent: { count?: number } = {};
const present: { count?: number } = { count: undefined };
assert.equal(Object.hasOwn(absent, 'count'), false);
assert.equal(Object.hasOwn(present, 'count'), true);
assert.equal(JSON.stringify(absent), '{}');
assert.equal(JSON.stringify(present), '{}');
```

**Expected:** hasOwn is false versus true; JSON serializes both as empty objects.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Show shallow readonly and shallow freeze boundaries

Task: Freeze an outer record containing a nested mutable object and update the nested count.

Both the inferred readonly property and runtime freeze protect the outer reference. Neither automatically traverses the nested object graph.

```typescript
const record = Object.freeze({ nested: { count: 1 } });
record.nested.count = 3;
assert.equal(record.nested.count, 3);
assert.equal(Object.isFrozen(record), true);
assert.equal(Object.isFrozen(record.nested), false);
```

**Expected:** nested count becomes 3; outer object is frozen.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Transform a readonly array without mutation

Task: Accept readonly numbers, return a doubled array, and demonstrate push is rejected statically.

A read-only consumer can compute a new value without requiring mutation rights. This often makes a function easier to reuse with both mutable and readonly callers.

```typescript
const values: readonly number[] = [1, 2];
const doubled = values.map((value) => value * 2);
assert.deepEqual(doubled, [2, 4]);
assert.deepEqual(values, [1, 2]);
function negativeTypeCheck(): void {
  // @ts-expect-error A readonly array has no mutable push operation.
  values.push(3);
}
void negativeTypeCheck;
```

**Expected:** new array 2,4; input remains 1,2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
