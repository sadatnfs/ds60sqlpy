# js-022: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Generics express a relationship between types across a reusable operation. An identity function returning any loses information about the relationship between input and output. A generic identity function returns the same type T supplied by its caller. The parameter is not a runtime argument or a request to create a new specialized JavaScript function for every type; it is a compile-time relation checked against one implementation.

A constraint gives the implementation only the operations known to exist. T extends {length: number} permits reading length, but does not permit replacing the input with an arbitrary object containing length and claiming it is still the caller's exact T. The caller may have supplied an array, a string or a richer record with additional invariants.

keyof and indexed access types connect property keys to property result types. A generic getProperty<T,K extends keyof T> returns T[K], preserving whether the chosen field is a string or a number. This is useful when the relationship is real. Overly elaborate generics can make an API harder to understand; prefer a concrete parameter type when only one domain shape is needed. Generics cannot validate unknown JSON or prove that an external service honored a claimed schema.

**Type parameter:** A placeholder describing a relationship selected at a call site.

**Constraint:** The minimum structure a generic implementation may rely on.

**Keyof:** A type operator producing the known keys of a type.

**Indexed access type:** A type expression selecting the type associated with a key.

## Reading the implementation

Declare type parameters in angle brackets on the function. T names a caller-selected type; extends constrains its allowed structure. K extends keyof T restricts a key to known properties, and T[K] gives the corresponding value type. A generic function returning the first element should expose T | undefined for an empty input even when the project's indexed-access checking is less strict. Runtime control flow must implement the same absence policy.

## Exercise 1: Preserve identity type and object identity

Task: Pass a number and an object through identity.

The generic relationship preserves static information without copying data. Runtime identity is still a separate observation checked by the assertion.

```typescript
const value: number = identity(7);
const record = { id: 'A' };
assert.equal(value, 7);
assert.equal(identity(record), record);
function negativeTypeCheck(): void {
  // @ts-expect-error identity preserves number rather than inventing string.
  const text: string = identity(7);
  void text;
}
void negativeTypeCheck;
```

**Expected:** number remains 7; object is the same reference.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Connect a key to its exact result type

Task: Read id and count from one record with getProperty.

Returning a broad string|number union would lose the connection between the selected key and its payload. T[K] preserves that correlation.

```typescript
const row = { id: 'A', count: 2 };
const id: string = getProperty(row, 'id');
const count: number = getProperty(row, 'count');
assert.equal(id, 'A');
assert.equal(count, 2);
function negativeTypeCheck(): void {
  // @ts-expect-error missing is not a key of this record.
  getProperty(row, 'missing');
}
void negativeTypeCheck;
```

**Expected:** id is string A; count is number 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Expose absence in a generic first function

Task: Read the first item from a nonempty and an empty readonly array.

The signature deliberately includes undefined. Depending on an unchecked array access that happens to compile would misrepresent the empty-input behavior.

```typescript
assert.equal(first([4, 5]), 4);
assert.equal(first<number>([]), undefined);
function negativeTypeCheck(): void {
  // @ts-expect-error The function promises possible absence.
  const definite: number = first<number>([]);
  void definite;
}
void negativeTypeCheck;
```

**Expected:** 4 and undefined.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Use only the constrained length property

Task: Apply a length operation to a string and an array; reject a number at compile time.

A constraint permits one shared capability across otherwise different types. It does not assert that the values have the same domain meaning or interchangeable methods.

```typescript
assert.equal(measuredLength('abc'), 3);
assert.equal(measuredLength([1, 2]), 2);
function negativeTypeCheck(): void {
  // @ts-expect-error number has no required length property.
  measuredLength(7);
}
void negativeTypeCheck;
```

**Expected:** lengths 3 and 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Transform while preserving output element type

Task: Map numbers to labels through a generic map function.

Two type parameters represent the input element and output element. The callback supplies the actual transformation, and the resulting array type follows it.

```typescript
const values = [2, 4];
const labels: string[] = mapValues(values, value => `item:${value}`);
assert.deepEqual(labels, ['item:2', 'item:4']);
assert.deepEqual(values, [2, 4]);
```

**Expected:** string array item:2,item:4; input unchanged.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Avoid pretending a constraint is the exact caller type

Task: Show that a replacement object cannot be returned as arbitrary T even if it meets the constraint.

A constraint is a lower bound on required capabilities, not the full identity of every allowed type. Fabricating a minimal object could discard fields the caller was promised.

```typescript
function negativeTypeCheck<T extends { length: number }>(value: T): T {
  void value;
  // @ts-expect-error T may require additional fields or a more specific shape.
  return { length: 0 };
}
void negativeTypeCheck;
assert.equal(measuredLength({ length: 5, id: 'A' }), 5);
```

**Expected:** expected compile error for returning a fabricated length-only object.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
