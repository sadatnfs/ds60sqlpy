# java-007: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.

**Instance:** A particular object with its own state.

**Encapsulation:** Controlling state changes through operations that preserve rules.

**Invariant:** A property required to hold for every valid object state.

## Reading the reference

private fields are accessed by methods inside the class. this denotes the current object when needed to distinguish fields and parameters. A method should calculate and validate a candidate state before assigning it. Math.addExact prevents integer overflow from turning a positive deposit into a negative balance. Public accessors can expose a value without exposing a mutable internal collection.

## Exercise 1: Create independent accounts

Task: Construct accounts with 100 and 100 cents,deposit 50 into the first.

Equal initial values do not mean shared identity. Eachnew expression creates a separate object whose field can evolve independently.

```java
Account first = new Account(100);
Account second = new Account(100);
first.deposit(50);
assert first.balance() == 150 && second.balance() == 100;
```

**Expected:** balances 150 and 100.

**Verify:** Compare the program values or named exception with balances 150 and 100. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Withdraw within the contract

Task: Withdraw40 cents from the first account.

The method validates the amount against current state, then performs one state change. The caller does not calculate and assign a raw field.

```java
first.withdraw(40);
assert first.balance() == 110;
```

**Expected:** balance110.

**Verify:** Compare the program values or named exception with balance110. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Reject overdraft atomically

Task: Attempt to withdraw111 from balance110.

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

**Expected:** IllegalArgumentException;balance still110.

**Verify:** Compare the program values or named exception with IllegalArgumentException;balance still110. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject negative input

Task: Attempt a deposit of-1.

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

**Expected:** IllegalArgumentException;balance unchanged.

**Verify:** Compare the program values or named exception with IllegalArgumentException;balance unchanged. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject invalid construction

Task: Construct an account with-1 cents.

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

**Expected:** constructor throwsIllegalArgumentException.

**Verify:** Compare the program values or named exception with constructor throwsIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Protect against overflow

Task: Create an account atInteger.MAX_VALUE and deposit1.

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

**Expected:** ArithmeticException;original maximum balance preserved.

**Verify:** Compare the program values or named exception with ArithmeticException;original maximum balance preserved. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
