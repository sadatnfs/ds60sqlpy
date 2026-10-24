# js-024: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

An external payload should enter typed code as unknown. JSON parsing establishes syntactic validity, but the result may be null, an array, a primitive or an object with the wrong fields. A runtime validator must inspect the shape and domain constraints before producing a trusted typed value. A type assertion skips this work; it cannot turn malformed input into valid data.

This lesson validates a small order with an id and an array of line items. Each item has a nonempty SKU and a positive safe-integer quantity. The validator returns a discriminated result instead of throwing for expected user-data errors, and includes a path such as items[1].quantity so the caller can identify the failing field. It copies accepted records so later edits to the original JSON object do not invalidate the already validated value.

Validation depth and resource budgets must be chosen together. An arbitrary recursive schema can consume excessive stack, CPU or memory. Here the structure has two bounded levels, at most twenty items, and bounded string lengths. Unknown extra keys are rejected deliberately. This is an exact fixture schema, not a claim that every API should reject forward-compatible fields. A permissive protocol might retain or ignore extras under a documented versioning policy.

**Unknown input:** A value whose structure has not yet been established.

**Schema validation:** Runtime checks for the required object and collection shape.

**Domain validation:** Checks for business constraints beyond primitive types.

**Diagnostic path:** A stable field location identifying where validation failed.

## Reading the implementation

A record guard checks typeof object, non-null and non-array before exposing string-key access as unknown. Domain checks then establish primitive types and bounds. The success branch carries an Order value; the failure branch carries a code, path and message. The JSON wrapper separates parse failure from schema failure. When validating an array, check each element and build a new typed output; do not cast the entire array after inspecting only the first row.

## Exercise 1: Validate and copy a complete order

Task: Parse an order with two line items and inspect the typed success.

The successful branch provides a typed value only after all fields pass. The result contains new objects, separating validation from later mutation of the input graph.

```typescript
const raw: unknown = { id: 'A', items: [{ sku: 'X', quantity: 2 }, { sku: 'Y', quantity: 3 }] };
const result = validateOrder(raw);
if (!result.ok) throw new Error(result.message);
assert.equal(result.ok, true);
assert.equal(result.value.items.reduce((sum, item) => sum + item.quantity, 0), 5);
assert.notEqual(result.value, raw);
```

**Expected:** success with total quantity 5; independent copied item records.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Report a nested domain failure precisely

Task: Validate a second item with quantity zero.

Checking every element prevents a valid first row from legitimizing invalid later rows. A stable path is more useful to the caller than a generic invalid input message.

```typescript
const result = validateOrder({ id: 'A', items: [{ sku: 'X', quantity: 2 }, { sku: 'Y', quantity: 0 }] });
assert.equal(result.ok, false);
if (result.ok) throw new Error('expected rejection');
assert.equal(result.code, 'schema');
assert.equal(result.path, 'items[1].quantity');
```

**Expected:** failure code schema and path items[1].quantity.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Separate JSON syntax failure from schema failure

Task: Parse malformed JSON and valid JSON null.

The two failure categories identify different repair actions. A client can fix JSON syntax before reasoning about missing domain fields.

```typescript
const malformed = parseOrder('{broken');
const wrongShape = parseOrder('null');
assert.equal(malformed.ok, false);
assert.equal(wrongShape.ok, false);
if (malformed.ok || wrongShape.ok) throw new Error('expected failures');
assert.equal(malformed.code, 'json');
assert.equal(wrongShape.code, 'schema');
```

**Expected:** codes json and schema respectively.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Reject unknown fields and excessive item counts

Task: Add an extra top-level field, then exceed the twenty-item limit.

Exact keys and bounded collection sizes are explicit choices of this schema. They prevent unnoticed extra configuration and keep work proportional to a small known limit.

```typescript
const extra = validateOrder({ id: 'A', items: [], admin: true });
const tooMany = validateOrder({ id: 'A', items: Array.from({ length: 21 }, () => ({ sku: 'X', quantity: 1 })) });
assert.equal(extra.ok, false);
assert.equal(tooMany.ok, false);
if (extra.ok || tooMany.ok) throw new Error('expected failures');
assert.equal(extra.path, '$');
assert.equal(tooMany.path, 'items');
```

**Expected:** paths $ and items respectively.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Preserve the validated value after input mutation

Task: Validate a mutable source and edit its first item afterward.

Validation alone does not freeze references. Constructing a fresh output ensures that external aliases cannot silently modify the accepted state after the boundary.

```typescript
const raw = { id: 'A', items: [{ sku: 'X', quantity: 2 }] };
const result = validateOrder(raw);
if (!result.ok) throw new Error(result.message);
raw.items[0].quantity = 9;
assert.equal(result.value.items[0].quantity, 2);
assert.equal(raw.items[0].quantity, 9);
```

**Expected:** validated quantity stays 2 while input becomes 9.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Exercise numeric and string boundaries

Task: Reject NaN, fractional quantities, empty SKU and oversized identifiers.

A number type includes NaN, infinities and fractions, so the integer domain needs explicit checks. An empty item array is deliberately accepted here; changing that business rule requires a matching validator and test change.

```typescript
for (const quantity of [NaN, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
  assert.equal(validateOrder({ id: 'A', items: [{ sku: 'X', quantity }] }).ok, false);
}
assert.equal(validateOrder({ id: 'A', items: [{ sku: '', quantity: 1 }] }).ok, false);
assert.equal(validateOrder({ id: 'A'.repeat(41), items: [] }).ok, false);
assert.equal(validateOrder({ id: 'A', items: [] }).ok, true);
```

**Expected:** every malformed fixture is rejected; an empty items array remains valid.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
