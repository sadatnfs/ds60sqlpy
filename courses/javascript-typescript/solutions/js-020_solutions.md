# js-020: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A union type describes a value that may belong to one of several alternatives. Until code proves which alternative is present, only operations valid for all alternatives are safe. Narrowing uses control flow to refine that set. typeof checks, equality checks, property checks and explicit discriminants can provide evidence. Truthiness is sometimes too coarse: an empty string is still a valid string even though it is falsy.

A discriminated union uses a shared property with distinct literal values, such as kind: success or kind: failure. Each alternative can then carry exactly the fields appropriate to that state. This is more precise than one object with several optional fields, which may admit impossible combinations such as success with no value. A switch over the discriminant connects runtime branching to static knowledge of the payload.

Exhaustiveness means accounting for every alternative. A function accepting never can mark a branch that should be unreachable after complete narrowing. Adding a new union member then creates a compile error at that branch until the handler is updated. This protects checked internal code. A JSON payload still needs validation: a type assertion can inject a value that violates the union and reaches the supposedly impossible branch at runtime.

**Union:** A value belonging to one of several alternatives.

**Narrowing:** Refining a type using control-flow evidence.

**Discriminant:** A shared field whose literal value identifies a variant.

**Exhaustiveness:** Handling every possible alternative in a closed union.

## Reading the implementation

Use a union operator between alternatives, then compare a literal discriminant with switch or equality. Within each branch, the checker exposes only that variant's fields. assertNever throws in the runtime fallback while requiring a never argument statically. User-defined type predicates can guide narrowing, but TypeScript trusts their declared claim; an incorrect predicate can make unsafe code compile. Prefer simple guards whose runtime checks actually establish the claimed property.

## Exercise 1: Handle a result union

Task: Format both successful value 7 and a failure message.

The kind check determines which payload exists. A failure result cannot accidentally be read as if it contained the success value.

```typescript
assert.equal(formatResult({ kind: 'success', value: 7 }), 'value:7');
assert.equal(formatResult({ kind: 'failure', message: 'offline' }), 'error:offline');
```

**Expected:** value:7 and error:offline.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Preserve an empty string during narrowing

Task: Handle string or undefined using an explicit undefined comparison.

if(value) would merge the empty-string case with absence. A guard should encode the domain distinction, not merely satisfy the checker.

```typescript
function describe(value: string | undefined): number | 'missing' {
  return value === undefined ? 'missing' : value.length;
}
assert.equal(describe(''), 0);
assert.equal(describe(undefined), 'missing');
```

**Expected:** empty string has length 0; absent value returns missing.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Reject access to another variant payload

Task: Demonstrate that a failure branch cannot read value.

The type prevents a concrete impossible-state mistake. It is stronger than optional fields that would allow reading undefined and hoping the caller checks it later.

```typescript
function negativeTypeCheck(result: Result): void {
  if (result.kind === 'failure') {
    // @ts-expect-error failure has message, not value.
    void result.value;
  }
}
void negativeTypeCheck;
assert.equal(formatResult({ kind: 'failure', message: 'bad' }), 'error:bad');
```

**Expected:** expected compiler error on value; valid failure formatting remains unchanged.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Catch an unhandled new variant at compile time

Task: Add a pending variant and intentionally omit it from a switch in an uncalled function.

The missing handler becomes a compiler obligation when the union grows. The error is evidence that the exhaustiveness guard is connected to the actual type.

```typescript
type Extended = Result | { kind: 'pending'; attempt: number };
function negativeTypeCheck(result: Extended): string {
  switch (result.kind) {
    case 'success':
      return String(result.value);
    case 'failure':
      return result.message;
    default:
      // @ts-expect-error pending remains possible here.
      return assertNever(result);
  }
}
void negativeTypeCheck;
assert.equal(formatResult({ kind: 'success', value: 0 }), 'value:0');
```

**Expected:** expected compiler error at assertNever for pending.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Use an honest unknown-value predicate

Task: Check for a record with a finite numeric value before consuming it.

The predicate inspects every property it claims. A declaration of value is SomeType is not automatically verified against the function body by the compiler.

```typescript
function hasFiniteValue(value: unknown): value is { value: number } {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value) &&
    'value' in value &&
    typeof value.value === 'number' &&
    Number.isFinite(value.value)
  );
}
assert.equal(hasFiniteValue({ value: 2 }), true);
for (const value of [null, [], { value: '2' }, { value: NaN }])
  assert.equal(hasFiniteValue(value), false);
```

**Expected:** valid record accepted; null, arrays and string-valued records rejected.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Expose the runtime limit of an asserted union

Task: Force a malformed external value into Result for demonstration and call the handler.

The intentionally unsafe assertion shows why exhaustiveness does not validate external data. The runtime fallback preserves diagnosis, but a real input boundary should reject the malformed value earlier.

```typescript
const malformed: unknown = { kind: 'unexpected' };
assert.throws(() => formatResult(malformed as Result), /unhandled variant/u);
```

**Expected:** runtime fallback throws rather than fabricating success.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
