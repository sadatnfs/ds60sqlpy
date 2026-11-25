# java-007: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.

**Instance:** A particular object with its own state.

**Encapsulation:** Controlling state changes through operations that preserve rules.

**Invariant:** A property required to hold for every valid object state.

## Reading the reference

private fields are accessed by methods inside the class. this denotes the current object when needed to distinguish fields and parameters. A method should calculate and validate a candidate state before assigning it. Math.addExact prevents integer overflow from turning a positive deposit into a negative balance. Public accessors can expose a value without exposing a mutable internal collection.

## Exercise 1: Create independent accounts: change one input

Task: Change `Account first = new Account(100);` to `Account first = new Account(101);` in Example A and predict which assertion fails and why.

Equal initial values do not mean shared identity. Each new expression creates a separate object whose field can evolve independently.

The unchanged code is the part that Example A adds:

```java
Account first = new Account(100);
Account second = new Account(100);
first.deposit(50);
assert first.balance() == 150 && second.balance() == 100;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `first.balance() == 150 && second.balance() == 100`.

**Verify:** Name the value that makes `first.balance() == 150 && second.balance() == 100` false, then restore the line.

## Exercise 2: Withdraw within the contract: debug a regression

Task: A regression in Example B's new code makes one line read `first.withdraw(41);`. Repair it using the failing assertion.

The method validates the amount against current state, then performs one state change. The caller does not calculate and assign a raw field.

The unchanged code is the part that Example B adds:

```java
first.withdraw(40);
assert first.balance() == 110;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `first.balance() == 110`; the repaired line reads `first.withdraw(40);`.

**Verify:** Explain how the changed token alters the value that `first.balance() == 110` tests.

## Exercise 3: Reject overdraft atomically

Task: Attempt to withdraw 111 from balance 110.

Validation precedes mutation. Subtracting first and throwing afterward would leave an invalid object behind.

```java
boolean overdraft = false;
try {
  first.withdraw(111);
} catch (IllegalArgumentException expected) {
  overdraft = true;
}
assert overdraft && first.balance() == 110;
```

**Expected:** IllegalArgumentException; balance still 110.

**Verify:** Control: changing `overdraft = true;` to `overdraft = false;` must fail the assertion on `overdraft && first.balance() == 110`.

## Exercise 4: Reject negative input

Task: Attempt a deposit of -1.

A negative deposit is not silently interpreted as a withdrawal. Each operation has a clear domain meaning and validation path.

```java
boolean negative = false;
try {
  first.deposit(-1);
} catch (IllegalArgumentException expected) {
  negative = true;
}
assert negative && first.balance() == 110;
```

**Expected:** IllegalArgumentException; balance unchanged.

**Verify:** Control: changing `negative = true;` to `negative = false;` must fail the assertion on `negative && first.balance() == 110`.

## Exercise 5: Reject invalid construction

Task: Construct an account with -1 cents.

An invariant should hold from the moment an object becomes available. Requiring a later repair call would expose invalid intermediate state to every user.

```java
boolean invalidStart = false;
try {
  new Account(-1);
} catch (IllegalArgumentException expected) {
  invalidStart = true;
}
assert invalidStart;
```

**Expected:** constructor throws IllegalArgumentException.

**Verify:** Control: changing `invalidStart = true;` to `invalidStart = false;` must fail the assertion on `invalidStart`.

## Exercise 6: Protect against overflow

Task: Create an account at Integer.MAX_VALUE and deposit 1.

The right-hand calculation fails before field assignment, so the prior valid value remains. Overflow is distinct from an ordinary insufficient-funds domain error.

```java
Account full = new Account(Integer.MAX_VALUE);
boolean overflow = false;
try {
  full.deposit(1);
} catch (ArithmeticException expected) {
  overflow = true;
}
assert overflow && full.balance() == Integer.MAX_VALUE;
```

**Expected:** ArithmeticException; original maximum balance preserved.

**Verify:** Control: changing `overflow = true;` to `overflow = false;` must fail the assertion on `overflow && full.balance() == Integer.MAX_VALUE`.

## After comparing the answer

Add a `transferTo(Account other, int cents)` method to your copy and decide where validation must happen so that a failed transfer changes neither account.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
