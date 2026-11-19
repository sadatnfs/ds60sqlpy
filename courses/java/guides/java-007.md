# java-007: Classes and encapsulation

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-006`

## Learning objectives

Encapsulate state in a class whose methods reject invalid input and leave the object unchanged on failure. Along the way, explain instance, encapsulation, invariant using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Attempt to withdraw 111 from balance 110. The final exercise transfers the mechanism to protect against overflow.

## Purpose and mental model

An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.

## Vocabulary and concepts

**Instance:** A particular object with its own state.

**Encapsulation:** Controlling state changes through operations that preserve rules.

**Invariant:** A property required to hold for every valid object state.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-007/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Create independent accounts: change one input.** Copy Example A into a scratch `Main.java` and change `Account first = new Account(100);` to `Account first = new Account(101);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `first.balance() == 150 && second.balance() == 100`. Restoring the original line brings back the worked observation: balances 150 and 100.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `first.balance() == 150 && second.balance() == 100` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Withdraw within the contract: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `first.withdraw(41);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `first.balance() == 110`; after it the line reads `first.withdraw(40);` again and balance 110.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `first.balance() == 110` for this input.

3. **Reject overdraft atomically.** Attempt to withdraw 111 from balance 110.
   **Expected:** IllegalArgumentException; balance still 110.
   **Verify:** Keep an assertion equivalent to `overdraft && first.balance() == 110`. As a control, change `overdraft = true;` to `overdraft = false;`: the run must fail with an `AssertionError` from the assertion on `overdraft && first.balance() == 110`. Restore the line before continuing.

4. **Reject negative input.** Attempt a deposit of -1.
   **Expected:** IllegalArgumentException; balance unchanged.
   **Verify:** Keep an assertion equivalent to `negative && first.balance() == 110`. As a control, change `negative = true;` to `negative = false;`: the run must fail with an `AssertionError` from the assertion on `negative && first.balance() == 110`. Restore the line before continuing.

5. **Reject invalid construction.** Construct an account with -1 cents.
   **Expected:** constructor throws IllegalArgumentException.
   **Verify:** Keep an assertion equivalent to `invalidStart`. As a control, change `invalidStart = true;` to `invalidStart = false;`: the run must fail with an `AssertionError` from the assertion on `invalidStart`. Restore the line before continuing.

6. **Protect against overflow.** Create an account at Integer.MAX_VALUE and deposit 1.
   **Expected:** ArithmeticException; original maximum balance preserved.
   **Verify:** Keep an assertion equivalent to `overflow && full.balance() == Integer.MAX_VALUE`. As a control, change `overflow = true;` to `overflow = false;`: the run must fail with an `AssertionError` from the assertion on `overflow && full.balance() == Integer.MAX_VALUE`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: balances 150 and 100. Then list the values read by `first.balance() == 150 && second.balance() == 100` and trace each one from its declaration. Finally, compute the asserted value with `Account first = new Account(101);` in place before running.
- **Exercise 2:** First restate the expected observation: balance 110. Then list the values read by `first.balance() == 110` and trace each one from its declaration. Finally, compare `first.withdraw(41);` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: illegalArgumentException; balance still 110. Then list the values read by `overdraft && first.balance() == 110` and trace each one from its declaration. Finally, predict the effect of changing `overdraft = true;` to `overdraft = false;` before running anything.
- **Exercise 4:** First restate the expected observation: illegalArgumentException; balance unchanged. Then list the values read by `negative && first.balance() == 110` and trace each one from its declaration. Finally, predict the effect of changing `negative = true;` to `negative = false;` before running anything.
- **Exercise 5:** First restate the expected observation: constructor throws IllegalArgumentException. Then list the values read by `invalidStart` and trace each one from its declaration. Finally, predict the effect of changing `invalidStart = true;` to `invalidStart = false;` before running anything.
- **Exercise 6:** First restate the expected observation: arithmeticException; original maximum balance preserved. Then list the values read by `overflow && full.balance() == Integer.MAX_VALUE` and trace each one from its declaration. Finally, predict the effect of changing `overflow = true;` to `overflow = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Instance, Encapsulation, Invariant in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
