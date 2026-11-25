# java-018: Tests that detect broken behavior

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-017`

## Learning objectives

Write tests that fail on a broken implementation, including boundary, property and exception checks.

The six exercises practice these steps:

- Use independent table cases.
- Check a boundary failure.
- Test an idempotence property.
- Detect a broken implementation.
- Verify the exception checker itself.
- Test a fresh transfer property.

## Purpose and mental model

A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples, boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea, but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.

## Vocabulary and concepts

**Test oracle:** An independent basis for deciding the expected result.

**Property:** A relation that should hold across a family of inputs.

**Mutation test:** A check that an intentionally broken variant is detected.

## How to run this lesson

`clamp`, `brokenClamp`, `expect` and `reverse` are helpers beside `main`; the deliberately broken `brokenClamp` exists only so Exercise 4 can prove that the case table detects it.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

A table-driven test stores inputs and expected outputs together, then runs the same checker over all cases. A property test checks a relation over several inputs, such as reversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.

## Worked example / walkthrough

### Example A: Use independent table cases

The expected outputs are literal contract examples. They do not call clamp or duplicate its full branching logic to generate answers.

```java
import java.util.*;

public class Main {

  static int clamp(int value, int lower, int upper) {
    if (lower > upper) throw new IllegalArgumentException("invalid bounds");
    return Math.max(lower, Math.min(value, upper));
  }

  static int brokenClamp(int value, int lower, int upper) {
    return value < lower ? upper : Math.min(value, upper);
  }

  @FunctionalInterface
  interface Action {
    void run() throws Exception;
  }

  static void expect(Class<? extends Throwable> type, Action action) {
    try {
      action.run();
    } catch (Throwable error) {
      if (type.isInstance(error)) return;
      throw new AssertionError("wrong exception", error);
    }
    throw new AssertionError("expected " + type.getSimpleName());
  }

  static int[] reverse(int[] values) {
    int[] result = values.clone();
    for (int i = 0, j = result.length - 1; i < j; i++, j--) {
      int temporary = result[i];
      result[i] = result[j];
      result[j] = temporary;
    }
    return result;
  }

  public static void main(String[] args) throws Exception {
    int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };
    for (int[] row : cases) assert clamp(row[0], 0, 5) == row[1];
  }
}
```

**Expected:** outputs 0, 0, 3, 5.

### Example B: Check a boundary failure

An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.

```java
import java.util.*;

public class Main {

  static int clamp(int value, int lower, int upper) {
    if (lower > upper) throw new IllegalArgumentException("invalid bounds");
    return Math.max(lower, Math.min(value, upper));
  }

  static int brokenClamp(int value, int lower, int upper) {
    return value < lower ? upper : Math.min(value, upper);
  }

  @FunctionalInterface
  interface Action {
    void run() throws Exception;
  }

  static void expect(Class<? extends Throwable> type, Action action) {
    try {
      action.run();
    } catch (Throwable error) {
      if (type.isInstance(error)) return;
      throw new AssertionError("wrong exception", error);
    }
    throw new AssertionError("expected " + type.getSimpleName());
  }

  static int[] reverse(int[] values) {
    int[] result = values.clone();
    for (int i = 0, j = result.length - 1; i < j; i++, j--) {
      int temporary = result[i];
      result[i] = result[j];
      result[j] = temporary;
    }
    return result;
  }

  public static void main(String[] args) throws Exception {
    int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };
    for (int[] row : cases) assert clamp(row[0], 0, 5) == row[1];

    expect(IllegalArgumentException.class, () -> clamp(3, 5, 2));
  }
}
```

**Expected:** exception observed.

## Prediction before your attempt

Before running Example A, write `clamp` for -2, 0, 3 and 9 with bounds 0 and 5 by applying the contract, not the code. For Example B, predict what `clamp(1, 5, 2)` should do when the lower bound exceeds the upper bound. Then predict whether the idempotence property in Exercise 3 alone would catch a mutant that always returns 0 (it would not, which is why the table matters).

## Exercises

1. **Use independent table cases: change one input.** Change `int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };` to `int[][] cases = { { -2, 1 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `clamp(row[0], 0, 5) == row[1]`.
   **Verify:** Name the value that makes `clamp(row[0], 0, 5) == row[1]` false, then restore the line.

2. **Check a boundary failure: debug a regression.** Add one defect to Example B's new code that changes its observation, then repair it.
   **Expected:** The defective copy fails its assertion and the repaired copy passes.
   **Verify:** Name the first statement whose value differs between the failing and repaired runs.

3. **Test an idempotence property.** For values -10 through 10, clamping an already clamped value leaves it unchanged.
   **Expected:** all 21 cases satisfy idempotence.
   **Verify:** Control: changing `int once = clamp(value, 0, 5);` to `int once = clamp(value, 0, 6);` must fail the assertion on `clamp(once, 0, 5) == once`.

4. **Detect a broken implementation.** Use a mutant that returns upper for values below lower and show the table rejects it.
   **Expected:** at least one mismatch.
   **Verify:** Control: changing `for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;` to `for (int[] row : cases) if (brokenClamp(row[1], 0, 5) != row[1]) caught = true;` must fail the assertion on `caught`.

5. **Verify the exception checker itself.** Ask the helper to expect an exception from a successful action and catch its AssertionError.
   **Expected:** checker fails when no exception is thrown.
   **Verify:** Control: changing `checkerFailed = true;` to `checkerFailed = false;` must fail the assertion on `checkerFailed`.

6. **Test a fresh transfer property.** Reverse arrays of length 0, 1, 3 twice using a separate copy and compare with originals.
   **Expected:** all originals restored; input arrays unchanged.
   **Verify:** Control: changing `if (original.length > 1) assert first[0] == original[original.length - 1];` to `if (original.length > 1) assert first[1] == original[original.length - 1];` inside the assertion must make it fail.

## Common pitfalls and diagnosis

The weakest test computes its expected value with the same formula as the implementation, so a bug appears on both sides and the test still passes. Another common failure is a test helper that catches every exception and reports success, which turns every negative test green; Exercise 5 tests the helper itself. Watch for property tests that a trivial implementation also satisfies, and remember that plain `java Main` skips every `assert`, so a suite built on assertions must run with `-ea`.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit changes the expected output for -2 to 1. Then apply the contract by hand: clamping -2 into 0 to 5 gives 0. Finally, decide whether the implementation or the table row is wrong, and explain why a test can be the defect.
- **Exercise 2:** First change `clamp(3, 5, 2)` to `clamp(3, 2, 5)` inside the `expect` call, which turns the reversed bounds into a valid interval. Then run it: `clamp` returns 3 instead of throwing, so `expect` raises `AssertionError` with the message "expected IllegalArgumentException". Finally, restore the reversed bounds and name the guard `lower > upper` as the first statement that behaves differently between the two runs.
- **Exercise 3:** First loop over every value from -10 to 10. Then compute `once = clamp(value, 0, 5)` and assert that clamping `once` again returns the same value. Finally, name a broken implementation that would still pass this property.
- **Exercise 4:** First run `brokenClamp` on every input in the case table and compare with the expected outputs. Then set a flag when any row differs. Finally, assert the flag and name the row that exposed the defect.
- **Exercise 5:** First call `expect(IllegalArgumentException.class, () -> {})` with an action that succeeds. Then catch the `AssertionError` the helper should throw and record it. Finally, explain why a helper that returned quietly here would make every negative test pass.
- **Exercise 6:** First reverse each array twice and compare the result with the original using `Arrays.equals`. Then assert, for arrays longer than one element, that the first reversal starts with the original's last element. Finally, explain why a `reverse` that returned its input unchanged would pass the round trip but not the second check.

## Self-check and retrieval

From memory, explain what makes a test oracle independent, why the table uses literal outputs, what idempotence of `clamp` means and which bug it cannot detect, and how a mutation such as `brokenClamp` shows that a suite is worth having.

## Next step

Continue with `java-019`: Data structures and complexity. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-018: Tests that detect broken behavior.
Read courses/java/guides/java-018.md and courses/java/lessons/java-018.java. Direct prerequisites: `java-017`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
