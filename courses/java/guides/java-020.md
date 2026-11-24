# java-020: Search, sorting and dynamic programming

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-019`

## Learning objectives

Implement binary search, stable sorting and dynamic programming that handle empty, tied and unreachable cases. Along the way, explain binary-search invariant, stable sort, dynamic programming using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Sort records (a, 2), (b, 1) and (c, 2) by key only and inspect the equal-key order. The final exercise transfers the mechanism to reject invalid recurrence inputs.

## Purpose and mental model

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys, which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case; memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

## Vocabulary and concepts

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-020/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A lower-bound search returns the first index whose value is at least the target, or length if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming table `dp[amount]` stores the minimum coin count for that exact amount, with `dp[0] = 0` and an unreachable sentinel. Each transition considers a smaller amount and one added coin.

## Worked example / walkthrough

### Example A: Find the first duplicate boundary

Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.

```java
import java.util.*;

public class Main {

  record Item(String id, int key) {}

  static int lowerBound(int[] values, int target) {
    int low = 0,
      high = values.length;
    while (low < high) {
      int mid = low + (high - low) / 2;
      if (values[mid] < target) low = mid + 1;
      else high = mid;
    }
    return low;
  }

  static int minimumCoins(int amount, int[] coins) {
    if (amount < 0 || amount > 1000) throw new IllegalArgumentException("amount 0..1000 required");
    for (int coin : coins)
      if (coin <= 0) throw new IllegalArgumentException("positive coins required");
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);
    dp[0] = 0;
    for (int current = 1; current <= amount; current++) for (int coin : coins)
      if (coin <= current) dp[current] = Math.min(dp[current], dp[current - coin] + 1);
    return dp[amount] > amount ? -1 : dp[amount];
  }

  public static void main(String[] args) throws Exception {
    int[] sorted = { 1, 2, 2, 5 };
    assert lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4;
  }
}
```

**Expected:** indices 1 and 4.

### Example B: Handle empty and outside searches

The half-open interval starts empty for an empty input. The result is an insertion position, not necessarily the index of an existing match.

```java
import java.util.*;

public class Main {

  record Item(String id, int key) {}

  static int lowerBound(int[] values, int target) {
    int low = 0,
      high = values.length;
    while (low < high) {
      int mid = low + (high - low) / 2;
      if (values[mid] < target) low = mid + 1;
      else high = mid;
    }
    return low;
  }

  static int minimumCoins(int amount, int[] coins) {
    if (amount < 0 || amount > 1000) throw new IllegalArgumentException("amount 0..1000 required");
    for (int coin : coins)
      if (coin <= 0) throw new IllegalArgumentException("positive coins required");
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);
    dp[0] = 0;
    for (int current = 1; current <= amount; current++) for (int coin : coins)
      if (coin <= current) dp[current] = Math.min(dp[current], dp[current - coin] + 1);
    return dp[amount] > amount ? -1 : dp[amount];
  }

  public static void main(String[] args) throws Exception {
    int[] sorted = { 1, 2, 2, 5 };
    assert lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4;

    assert lowerBound(new int[0], 7) == 0;
    assert lowerBound(sorted, 0) == 0;
  }
}
```

**Expected:** both return 0.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Find the first duplicate boundary: change one input.** Copy Example A into a scratch `Main.java` and change `int[] sorted = { 1, 2, 2, 5 };` to `int[] sorted = { 2, 2, 2, 5 };`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`. Restoring the original line brings back the worked observation: indices 1 and 4.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Handle empty and outside searches: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert lowerBound(new int[1], 7) == 0;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `lowerBound(new int[0], 7) == 0`; after it the line reads `assert lowerBound(new int[0], 7) == 0;` again and both return 0.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `lowerBound(new int[0], 7) == 0` accepts.

3. **Preserve stable ties.** Sort records (a, 2), (b, 1) and (c, 2) by key only and inspect the equal-key order.
   **Expected:** IDs b, a, c.
   **Verify:** Keep an assertion equivalent to `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`. As a control, change `List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))` to `List.of(new Item("a", 3), new Item("b", 1), new Item("c", 2))`: the run must fail with an `AssertionError` from the assertion on `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`. Restore the line before continuing.

4. **Solve a greedy counterexample.** Find minimum coins for amount 6 using coins 1, 3, 4.
   **Expected:** 2 coins, using 3+3 rather than 4+1+1.
   **Verify:** Keep an assertion equivalent to `minimumCoins(6, new int[] { 1, 3, 4 }) == 2`. As a control, change `assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;` to `assert minimumCoins(6, new int[] { 1, 4, 4 }) == 2;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Represent an unreachable amount.** Solve amount 3 with only coin 2 and amount 0 with any positive coins.
   **Expected:** -1 for unreachable amount 3; 0 for amount 0.
   **Verify:** Keep an assertion equivalent to `minimumCoins(0, new int[] { 2, 5 }) == 0`. As a control, change `assert minimumCoins(0, new int[] { 2, 5 }) == 0;` to `assert minimumCoins(1, new int[] { 2, 5 }) == 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Reject invalid recurrence inputs.** Pass a negative amount or a zero-valued coin.
   **Expected:** IllegalArgumentException for both.
   **Verify:** Keep an assertion equivalent to `negative && zeroCoin`. As a control, change `minimumCoins(3, new int[] { 0, 1 });` to `minimumCoins(3, new int[] { 1, 1 });`: the run must fail with an `AssertionError` from the assertion on `negative && zeroCoin`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: indices 1 and 4. Then list the values read by `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4` and trace each one from its declaration. Finally, compute the asserted value with `int[] sorted = { 2, 2, 2, 5 };` in place before running.
- **Exercise 2:** First restate the expected observation: both return 0. Then list the values read by `lowerBound(new int[0], 7) == 0` and trace each one from its declaration. Finally, compare `assert lowerBound(new int[1], 7) == 0;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: IDs b, a, c. Then list the values read by `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))` and trace each one from its declaration. Finally, predict the effect of changing `List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))` to `List.of(new Item("a", 3), new Item("b", 1), new Item("c", 2))` before running anything.
- **Exercise 4:** First restate the expected observation: 2 coins, using 3+3 rather than 4+1+1. Then list the values read by `minimumCoins(6, new int[] { 1, 3, 4 }) == 2` and trace each one from its declaration. Finally, name one input that would make `minimumCoins(6, new int[] { 1, 3, 4 }) == 2` false.
- **Exercise 5:** First restate the expected observation: -1 for unreachable amount 3; 0 for amount 0. Then list the values read by `minimumCoins(0, new int[] { 2, 5 }) == 0` and trace each one from its declaration. Finally, name one input that would make `minimumCoins(0, new int[] { 2, 5 }) == 0` false.
- **Exercise 6:** First restate the expected observation: illegalArgumentException for both. Then list the values read by `negative && zeroCoin` and trace each one from its declaration. Finally, predict the effect of changing `minimumCoins(3, new int[] { 0, 1 });` to `minimumCoins(3, new int[] { 1, 1 });` before running anything.

## Self-check and retrieval

Close the solution and explain Binary-search invariant, Stable sort, Dynamic programming in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-020: Search, sorting and dynamic programming.
Read courses/java/guides/java-020.md and courses/java/lessons/java-020.java. Direct prerequisites: `java-019`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
