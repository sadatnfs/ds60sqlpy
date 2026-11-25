# java-007: Classes and encapsulation

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-006`

## Learning objectives

Encapsulate state in a class whose methods reject invalid input and leave the object unchanged on failure.

The six exercises practice these steps:

- Create independent accounts.
- Withdraw within the contract.
- Reject overdraft atomically.
- Reject negative input.
- Reject invalid construction.
- Protect against overflow.

## Purpose and mental model

An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.

## Vocabulary and concepts

**Instance:** A particular object with its own state.

**Encapsulation:** Controlling state changes through operations that preserve rules.

**Invariant:** A property required to hold for every valid object state.

## How to run this lesson

The `Account` class is declared inside `Main`, so every example still compiles as one `Main.java`; the overdraft, negative deposit, invalid start and overflow checks throw on purpose and catch the exception.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

private fields are accessed by methods inside the class. this denotes the current object when needed to distinguish fields and parameters. A method should calculate and validate a candidate state before assigning it. Math.addExact prevents integer overflow from turning a positive deposit into a negative balance. Public accessors can expose a value without exposing a mutable internal collection.

## Worked example / walkthrough

### Example A: Create independent accounts

Equal initial values do not mean shared identity. Each new expression creates a separate object whose field can evolve independently.

```java
import java.util.*;

public class Main {

  static final class Account {

    private int cents;

    Account(int cents) {
      if (cents < 0) throw new IllegalArgumentException("negative balance");
      this.cents = cents;
    }

    int balance() {
      return cents;
    }

    void deposit(int amount) {
      if (amount < 0) throw new IllegalArgumentException("negative deposit");
      cents = Math.addExact(cents, amount);
    }

    void withdraw(int amount) {
      if (amount < 0 || amount > cents) throw new IllegalArgumentException("invalid withdrawal");
      cents -= amount;
    }
  }

  public static void main(String[] args) throws Exception {
    Account first = new Account(100);
    Account second = new Account(100);
    first.deposit(50);
    assert first.balance() == 150 && second.balance() == 100;
  }
}
```

**Expected:** balances 150 and 100.

### Example B: Withdraw within the contract

The method validates the amount against current state, then performs one state change. The caller does not calculate and assign a raw field.

```java
import java.util.*;

public class Main {

  static final class Account {

    private int cents;

    Account(int cents) {
      if (cents < 0) throw new IllegalArgumentException("negative balance");
      this.cents = cents;
    }

    int balance() {
      return cents;
    }

    void deposit(int amount) {
      if (amount < 0) throw new IllegalArgumentException("negative deposit");
      cents = Math.addExact(cents, amount);
    }

    void withdraw(int amount) {
      if (amount < 0 || amount > cents) throw new IllegalArgumentException("invalid withdrawal");
      cents -= amount;
    }
  }

  public static void main(String[] args) throws Exception {
    Account first = new Account(100);
    Account second = new Account(100);
    first.deposit(50);
    assert first.balance() == 150 && second.balance() == 100;

    first.withdraw(40);
    assert first.balance() == 110;
  }
}
```

**Expected:** balance 110.

## Prediction before your attempt

Before running Example A, decide whether two accounts that both start at 100 cents share any state, and write both balances after depositing 50 into the first. For Example B, predict the balance after withdrawing 40 and which method performs the subtraction. Before Exercise 3, predict whether a rejected withdrawal of 111 can change the balance, given that validation runs before the field is assigned.

## Exercises

1. **Create independent accounts: change one input.** Change `Account first = new Account(100);` to `Account first = new Account(101);` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `first.balance() == 150 && second.balance() == 100`.
   **Verify:** Name the value that makes `first.balance() == 150 && second.balance() == 100` false, then restore the line.

2. **Withdraw within the contract: debug a regression.** A regression in Example B's new code makes one line read `first.withdraw(41);`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `first.balance() == 110`; the repaired line reads `first.withdraw(40);`.
   **Verify:** Explain how the changed token alters the value that `first.balance() == 110` tests.

3. **Reject overdraft atomically.** Attempt to withdraw 111 from balance 110.
   **Expected:** IllegalArgumentException; balance still 110.
   **Verify:** Control: changing `overdraft = true;` to `overdraft = false;` must fail the assertion on `overdraft && first.balance() == 110`.

4. **Reject negative input.** Attempt a deposit of -1.
   **Expected:** IllegalArgumentException; balance unchanged.
   **Verify:** Control: changing `negative = true;` to `negative = false;` must fail the assertion on `negative && first.balance() == 110`.

5. **Reject invalid construction.** Construct an account with -1 cents.
   **Expected:** constructor throws IllegalArgumentException.
   **Verify:** Control: changing `invalidStart = true;` to `invalidStart = false;` must fail the assertion on `invalidStart`.

6. **Protect against overflow.** Create an account at Integer.MAX_VALUE and deposit 1.
   **Expected:** ArithmeticException; original maximum balance preserved.
   **Verify:** Control: changing `overflow = true;` to `overflow = false;` must fail the assertion on `overflow && full.balance() == Integer.MAX_VALUE`.

## Common pitfalls and diagnosis

The typical encapsulation bug is mutating first and validating second: `balance -= amount; if (balance < 0) throw ...` leaves the account negative after the exception. Validate, then assign once. Another mistake is a public setter for `balance`, which lets callers skip every rule. And `balance + amount` on an `int` can wrap silently near `Integer.MAX_VALUE`; `Math.addExact` throws before the field changes, so the old valid balance survives.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First compute the first account's balance after the edit: 101 plus the deposit of 50. Then compare it with the 150 the assertion expects, while the second account still reports 100. Finally, explain which half of the condition fails and why the second account is unaffected.
- **Exercise 2:** First compute 150 minus 41. Then compare the result with the 110 in the assertion. Finally, notice that the withdrawal was still accepted, because 41 cents is within the balance, so the failure is in the amount and not in validation.
- **Exercise 3:** First call `withdraw(111)` on the account holding 110 inside a `try` block. Then catch `IllegalArgumentException` and set a flag. Finally, assert both the flag and the unchanged balance, which passes only if validation ran before the subtraction.
- **Exercise 4:** First call `deposit(-1)` inside a `try` block and catch `IllegalArgumentException`. Then read the balance after the `catch`. Finally, explain why treating a negative deposit as a withdrawal would blur two operations with different rules.
- **Exercise 5:** First call the constructor with -1 inside a `try` block. Then catch `IllegalArgumentException` and record it. Finally, explain why the check belongs in the constructor rather than in a later repair method.
- **Exercise 6:** First create an account holding `Integer.MAX_VALUE` and deposit 1 inside a `try` block. Then catch the `ArithmeticException` that the exact addition throws. Finally, assert that the balance still equals `Integer.MAX_VALUE`, which proves the failed sum never reached the field.

## Self-check and retrieval

Without the guide, state the invariant of `Account` and name each operation that could break it: construction, deposit, withdrawal and overflow. For each, explain how the reference rejects the input and why the balance is unchanged after the rejection.

## Next step

Continue with `java-008`: Constructors, records and invariants. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-007: Classes and encapsulation.
Read courses/java/guides/java-007.md and courses/java/lessons/java-007.java. Direct prerequisites: `java-006`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
