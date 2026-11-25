# java-003: Decisions, loops and invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-002`

## Learning objectives

Write guarded conditions, loops with explicit invariants and an exhaustive switch expression, and expose an off-by-one boundary.

The six exercises practice these steps:

- Guard a nullable value.
- Trace a prefix sum.
- Handle an empty loop.
- Choose a value with a switch expression.
- Stop at the first match.
- Expose a wrong boundary.

## Purpose and mental model

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error. A switch expression chooses one value from several labeled cases, and the compiler can check that every possible input has a case.

## Vocabulary and concepts

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

**Switch expression:** A switch that evaluates to one value and must cover every possible input.

## How to run this lesson

The examples use only arrays, lists and the `DayOfWeek` enum; Exercise 6 provokes an `ArrayIndexOutOfBoundsException` on purpose and catches it, so a clean finish is the expected result.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

if selects a branch. && evaluates the right operand only when the left is true; || evaluates it only when needed. A for loop has initialization, condition and update. Use index < length for zero-based arrays. The prefix-sum invariant starts with index 0, sum 0, then adds exactly the element at the current index before advancing. Break exits the loop; continue skips to the next iteration and can accidentally bypass an update in a while loop. In a switch expression, each case label is followed by -> and one result; labels never fall through, and an expression switch must cover every value of its input type.

## Worked example / walkthrough

### Example A: Guard a nullable value

The right operand is not evaluated when the left is false. Reversing the operands would attempt the method call before the guard.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String text = null;
    boolean nonempty = text != null && !text.isEmpty();
    assert !nonempty;
  }
}
```

**Expected:** condition false with no NullPointerException.

### Example B: Trace a prefix sum

The accumulator begins at the additive identity 0. Each iteration adds one new element, so no record is skipped or counted twice.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String text = null;
    boolean nonempty = text != null && !text.isEmpty();
    assert !nonempty;

    int[] values = { 2, 4, 6 };
    int sum = 0;
    List<Integer> prefixes = new ArrayList<>();
    for (int i = 0; i < values.length; i++) {
      sum += values[i];
      prefixes.add(sum);
    }
    assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;
  }
}
```

**Expected:** prefix sums 2, 6, 12; final 12.

## Prediction before your attempt

Before running Example A, decide whether `text != null && !text.isEmpty()` ever calls `isEmpty` when `text` is null, and what would happen if the operands were swapped. For Example B, write the value of `sum` before each iteration over 2, 4 and 6 and confirm that it always equals the sum of the elements already visited. Then predict how many times the loop body runs for an empty array.

## Exercises

1. **Guard a nullable value: predict an edited check.** Change Example A's assertion to `assert nonempty;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `!nonempty`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `!nonempty`.

2. **Trace a prefix sum: debug a regression.** A regression in Example B's new code makes one line read `sum -= values[i];`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; the repaired line reads `sum += values[i];`.
   **Verify:** Explain how the changed token alters the value that `prefixes.equals(List.of(2, 6, 12)) && sum == 12` tests.

3. **Handle an empty loop.** Run the same sum pattern over an empty int array.
   **Expected:** sum 0 and zero iterations.
   **Verify:** Control: changing `int emptySum = 0;` to `int emptySum = 1;` must fail the assertion on `emptySum == 0 && iterations == 0`.

4. **Choose a value with a switch expression.** Classify Saturday and Wednesday with one exhaustive switch expression over java.time.DayOfWeek.
   **Expected:** weekend, then weekday.
   **Verify:** Control: changing `case SATURDAY, SUNDAY -> "weekend";` to `case SATURDAY, SUNDAY -> "weekend!";` must fail the assertion on `kinds.equals(List.of("weekend", "weekday"))`.

5. **Stop at the first match.** Search 3, 8, 8 for the first 8 and stop immediately.
   **Expected:** index 1.
   **Verify:** Control: changing `if (items[i] == 8) {` to `if (items[i] != 8) {` must fail the assertion on `found == 1`.

6. **Expose a wrong boundary.** Compare a loop using i <= length with the valid i < length contract on a one-element array.
   **Expected:** wrong loop raises ArrayIndexOutOfBoundsException.
   **Verify:** Control: changing `for (int i = 0; i <= single.length; i++) {` to `for (int i = 0; i < single.length; i++) {` must fail the assertion on `failed`.

## Common pitfalls and diagnosis

Off-by-one boundaries are the defect this lesson targets. A loop written with `i <= values.length` passes every check that never reaches the last index and then fails with `ArrayIndexOutOfBoundsException` on the final iteration, so test a one-element array, not only a large one. A second mistake is using `&` instead of `&&` in a null guard: both operands are evaluated, and the method call on null throws. In a search loop, forgetting `break` lets a later match overwrite the first one.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First evaluate `text != null` for the null input and note that `&&` stops there. Then work out the value stored in `nonempty`. Finally, compare that value with what the edited assertion claims and decide whether the program or the assertion is wrong.
- **Exercise 2:** First trace `sum` through the three iterations with the edited operator. Then compare the prefixes you get with the list 2, 6, 12. Finally, explain which part of the loop invariant the subtraction breaks.
- **Exercise 3:** First start the accumulator at the additive identity 0 and count iterations in a separate variable. Then run the unchanged loop over `new int[0]` and note that the body never executes. Finally, assert both the sum and the iteration count, so a fabricated starting value would fail.
- **Exercise 4:** First write one `switch` expression with arrow labels over `DayOfWeek` that returns a `String`. Then name every constant in the two cases, with Saturday and Sunday in the weekend case. Finally, remove one constant temporarily and read the compiler error that proves the switch is checked for exhaustiveness.
- **Exercise 5:** First initialize the result index to the sentinel -1 so absence is distinguishable from index 0. Then scan the array and leave the loop with `break` as soon as an element equals 8. Finally, explain why the second 8 at index 2 must not overwrite the first match.
- **Exercise 6:** First write the loop with `i <= single.length` over a one-element array inside a `try` block. Then catch `ArrayIndexOutOfBoundsException` and record that it happened. Finally, run the same body with `i < single.length` and explain which index the wrong boundary reached.

## Self-check and retrieval

Close the guide and state the invariant of the prefix-sum loop in one sentence, then show that it holds before the first iteration and after the last. Explain why `&&` makes the null guard safe, why an empty array needs no special case, and what the compiler does when an arrow `switch` over `DayOfWeek` misses a constant.

## Next step

Continue with `java-004`: Methods and explicit contracts. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-003: Decisions, loops and invariants.
Read courses/java/guides/java-003.md and courses/java/lessons/java-003.java. Direct prerequisites: `java-002`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
