# js-026: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Classes combine state with operations that preserve invariants. A typed number can still be negative, fractional, infinite or too large for exact integer arithmetic. A balance object therefore checks values before assigning new state. Constructor and method annotations document accepted checked calls, while runtime checks protect the actual numeric domain.

JavaScript #private fields enforce privacy at runtime. TypeScript private is primarily a checking restriction and should not be confused with a security boundary around ordinary emitted properties. Encapsulation is useful when callers should request an operation rather than directly assign arbitrary state. A getter returning a number supplies a value; a getter returning a mutable object would need a separate ownership policy.

Composition supplies a collaborator through a small interface, such as a clock. A test can provide a deterministic clock without changing global time or subclassing a large framework. The interface describes the capability required by the consumer. Inheritance is appropriate when substitutability is real, but reusing a few implementation lines does not prove that every subclass preserves its parent's contract.

**Encapsulation:** Restricting state changes to invariant-preserving operations.

**Private field:** A JavaScript # field with runtime-enforced access.

**Composition:** Building behavior from explicit collaborators.

**Interface:** A static capability contract for compatible values.

## Reading the implementation

A constructor establishes initial state. #balance names a runtime private field, while the cents getter exposes a primitive observation. implements would check an interface without generating methods. Constructor parameter properties create fields as part of TypeScript emission. A readonly dependency reference prevents reassignment through that class; it does not guarantee the collaborator itself is immutable. Validate derived results before committing a state transition.

## Exercise 1: Maintain balance through methods: change one input

Task: Copy Example A into a scratch `main.mts` and change `const wallet = new Wallet(100);` to `const wallet = new Wallet(101);`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The public API exposes observations and controlled mutations. A caller cannot directly assign the private field by an ordinary property name.

The unchanged code is the exercise block of Example A:

```typescript
const wallet = new Wallet(100);
wallet.deposit(50);
wallet.withdraw(30);
assert.equal(wallet.cents, 120);
assert.equal(Object.hasOwn(wallet, 'balance'), false);
assert.deepEqual(Object.keys(wallet), []);
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal(wallet.cents, 120)`. Restoring the original line brings back the worked observation: balance 120; no enumerable balance field.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(wallet.cents, 120)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Inject a deterministic clock: debug a regression

Task: A regression changed one token in Example B, so one line now reads `const service = new ReceiptService({ now: () => new Date('2027-01-01T00:00:00.000Z') });`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

The time dependency is explicit and replaceable. The test does not mutate global time or rely on a fragile elapsed-time tolerance.

The unchanged code is the exercise block of Example B:

```typescript
const service = new ReceiptService({ now: () => new Date('2026-01-01T00:00:00.000Z') });
assert.deepEqual(service.create('A'), { id: 'A', createdAt: '2026-01-01T00:00:00.000Z' });
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.deepEqual(service.create('A'), { id: 'A', createdAt: '2026-01-01T00:00:00.000Z' })`; after it the line reads `const service = new ReceiptService({ now: () => new Date('2026-01-01T00:00:00.000Z') });` again and timestamp 2026-01-01T00:00:00.000Z.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.deepEqual(service.create('A'), { id: 'A', createdAt: '2026-01-01T00:00:00.000Z' })` for this input.

## Exercise 3: Reject invalid transitions without mutation

Task: Try a negative deposit and an overdraw.

Checking after mutation would leave invalid state when the method throws. Validation must precede assignment for this failure-atomic contract.

```typescript
const wallet = new Wallet(100);
assert.throws(() => wallet.deposit(-1), RangeError);
assert.throws(() => wallet.withdraw(101), RangeError);
assert.equal(wallet.cents, 100);
```

**Expected:** both throw; balance stays 100.

**Verify:** Keep a check equivalent to `assert.throws(() => wallet.withdraw(101), RangeError)`. As a control, change `const wallet = new Wallet(100);` to `const wallet = new Wallet(101);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Guard derived overflow

Task: Deposit one cent into the maximum safe balance.

Valid individual inputs do not guarantee a representable sum. The invariant applies to the resulting state as well as the method argument.

```typescript
const wallet = new Wallet(Number.MAX_SAFE_INTEGER);
assert.throws(() => wallet.deposit(1), RangeError);
assert.equal(wallet.cents, Number.MAX_SAFE_INTEGER);
```

**Expected:** RangeError; original balance preserved.

**Verify:** Keep a check equivalent to `assert.equal(wallet.cents, Number.MAX_SAFE_INTEGER)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## Exercise 5: Reject an incompatible collaborator

Task: Pass a clock returning text in an uncalled negative type check.

The small interface catches a concrete mismatch without requiring the collaborator to inherit from a particular class.

```typescript
function negativeTypeCheck(): void {
  // @ts-expect-error Clock.now must return Date.
  new ReceiptService({ now: () => 'today' });
}
void negativeTypeCheck;
assert.equal(
  new ReceiptService({ now: () => new Date(0) }).create('B').createdAt,
  '1970-01-01T00:00:00.000Z',
);
```

**Expected:** expected compiler error; valid Date clock works.

**Verify:** Keep a check equivalent to `assert.equal(new ReceiptService({ now: () => new Date(0) }).create('B').createdAt, '1970-01-01T00:00:00.000Z')`. As a control, change `new ReceiptService({ now: () => new Date(0) }).create('B').createdAt,` to `new ReceiptService({ now: () => new Date(1) }).create('B').createdAt,` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Distinguish private storage from a lookalike property

Task: Add an ordinary balance property to the wallet.

The string property and private name refer to separate storage. This observation demonstrates a runtime guarantee rather than only a compiler diagnostic.

```typescript
const wallet = new Wallet(2);
Object.assign(wallet, { balance: 999 });
assert.equal(Reflect.get(wallet, 'balance'), 999);
assert.equal(wallet.cents, 2);
```

**Expected:** ordinary property 999; private cents remain 2.

**Verify:** Keep a check equivalent to `assert.equal(wallet.cents, 2)`. As a control, change `const wallet = new Wallet(2);` to `const wallet = new Wallet(3);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
