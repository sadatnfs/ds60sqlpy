# java-007: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.

**Instance:** A particular object with its own state.

**Encapsulation:** Controlling state changes through operations that preserve rules.

**Invariant:** A property required to hold for every valid object state.

## Reading the reference

private fields are accessed by methods inside the class. this denotes the current object when needed to distinguish fields and parameters. A method should calculate and validate a candidate state before assigning it. Math.addExact prevents integer overflow from turning a positive deposit into a negative balance. Public accessors can expose a value without exposing a mutable internal collection.

## Exercise 1: Create independent accounts: change one input

Task: Copy Example A into a scratch `Main.java` and change `Account first = new Account(100);` to `Account first = new Account(101);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

Equal initial values do not mean shared identity. Each new expression creates a separate object whose field can evolve independently.

The unchanged code is the part that Example A adds:

```java
Account first = new Account(100);
Account second = new Account(100);
first.deposit(50);
assert first.balance() == 150 && second.balance() == 100;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `first.balance() == 150 && second.balance() == 100`. Restoring the original line brings back the worked observation: balances 150 and 100.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `first.balance() == 150 && second.balance() == 100` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Withdraw within the contract: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `first.withdraw(41);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The method validates the amount against current state, then performs one state change. The caller does not calculate and assign a raw field.

The unchanged code is the part that Example B adds:

```java
first.withdraw(40);
assert first.balance() == 110;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `first.balance() == 110`; after it the line reads `first.withdraw(40);` again and balance 110.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `first.balance() == 110` for this input.

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

**Verify:** Keep an assertion equivalent to `overdraft && first.balance() == 110`. As a control, change `overdraft = true;` to `overdraft = false;`: the run must fail with an `AssertionError` from the assertion on `overdraft && first.balance() == 110`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `negative && first.balance() == 110`. As a control, change `negative = true;` to `negative = false;`: the run must fail with an `AssertionError` from the assertion on `negative && first.balance() == 110`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `invalidStart`. As a control, change `invalidStart = true;` to `invalidStart = false;`: the run must fail with an `AssertionError` from the assertion on `invalidStart`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `overflow && full.balance() == Integer.MAX_VALUE`. As a control, change `overflow = true;` to `overflow = false;`: the run must fail with an `AssertionError` from the assertion on `overflow && full.balance() == Integer.MAX_VALUE`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
