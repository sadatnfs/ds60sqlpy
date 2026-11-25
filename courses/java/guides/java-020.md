# java-020: Search, sorting and dynamic programming

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-019`

## Learning objectives

Implement binary search, stable sorting and dynamic programming that handle empty, tied and unreachable cases.

The six exercises practice these steps:

- Find the first duplicate boundary.
- Handle empty and outside searches.
- Preserve stable ties.
- Solve a greedy counterexample.
- Represent an unreachable amount.
- Reject invalid recurrence inputs.

## Purpose and mental model

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys, which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case; memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

## Vocabulary and concepts

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## How to run this lesson

`lowerBound` and `minimumCoins` are helpers beside `main`; the coin fixture with coins 1, 3 and 4 is chosen because a greedy strategy gives the wrong answer for amount 6.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, trace `lowerBound` on 1, 2, 2, 5 for target 2 and for target 6, and say what the result means when the target is absent (an insertion position). For Example B, predict the result for an empty array and for a target below the first element. Before Exercise 4, compute the greedy answer for amount 6 with coins 1, 3 and 4 (4 + 1 + 1, three coins) and compare it with the optimum.

## Exercises

1. **Find the first duplicate boundary: change one input.** Change `int[] sorted = { 1, 2, 2, 5 };` to `int[] sorted = { 2, 2, 2, 5 };` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`.
   **Verify:** Name the value that makes `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4` false, then restore the line.

2. **Handle empty and outside searches: diagnose an edited check.** Example B's new assertion was edited to `assert lowerBound(new int[1], 7) == 0;`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `lowerBound(new int[0], 7) == 0`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `lowerBound(new int[0], 7) == 0` accepts.

3. **Preserve stable ties.** Sort records (a, 2), (b, 1) and (c, 2) by key only and inspect the equal-key order.
   **Expected:** IDs b, a, c.
   **Verify:** Control: changing `List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))` to `List.of(new Item("a", 3), new Item("b", 1), new Item("c", 2))` must fail the assertion on `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`.

4. **Solve a greedy counterexample.** Find minimum coins for amount 6 using coins 1, 3, 4.
   **Expected:** 2 coins, using 3+3 rather than 4+1+1.
   **Verify:** Control: changing `assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;` to `assert minimumCoins(6, new int[] { 1, 4, 4 }) == 2;` inside the assertion must make it fail.

5. **Represent an unreachable amount.** Solve amount 3 with only coin 2 and amount 0 with any positive coins.
   **Expected:** -1 for unreachable amount 3; 0 for amount 0.
   **Verify:** Control: changing `assert minimumCoins(0, new int[] { 2, 5 }) == 0;` to `assert minimumCoins(1, new int[] { 2, 5 }) == 0;` inside the assertion must make it fail.

6. **Reject invalid recurrence inputs.** Pass a negative amount or a zero-valued coin.
   **Expected:** IllegalArgumentException for both.
   **Verify:** Control: changing `minimumCoins(3, new int[] { 0, 1 });` to `minimumCoins(3, new int[] { 1, 1 });` must fail the assertion on `negative && zeroCoin`.

## Common pitfalls and diagnosis

Binary search bugs are boundary bugs: mixing a closed interval `[low, high]` with a half-open update such as `high = mid` either skips the answer or loops forever, so pick one convention and keep its invariant. Computing `mid` as `(low + high) / 2` can overflow for huge arrays; `low + (high - low) / 2` cannot. In dynamic programming, using 0 for "unreachable" makes an impossible amount look free; keep a separate sentinel such as -1. And a zero-valued coin never shrinks the subproblem.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit makes the array 2, 2, 2, 5. Then find the first index whose value is at least 2. Finally, compare it with the 1 the assertion expects and explain why the search itself is still correct.
- **Exercise 2:** First note that `new int[1]` is an array holding one 0, not an empty array. Then compute where 7 would be inserted. Finally, compare that position with 0 and explain why the edit no longer tests the empty case.
- **Exercise 3:** First sort the items with `Comparator.comparingInt(Item::key)` and no secondary comparator. Then read the order of the two items with key 2. Finally, explain why `List.sort` keeps a before c and what an explicit tie-breaker would change.
- **Exercise 4:** First fill a table where entry `a` holds the fewest coins for amount `a`, starting from 0 for amount 0. Then compute each entry from every coin that fits, using the earlier entries. Finally, read entry 6 and compare 3 + 3 with the greedy 4 + 1 + 1.
- **Exercise 5:** First fill the table with `amount + 1`, a value no real answer can reach, and set entry 0 to 0. Then solve amount 3 with only the coin 2 and amount 0 with coins 2 and 5. Finally, translate the leftover sentinel to -1 and explain why unreachable must differ from zero coins.
- **Exercise 6:** First call `minimumCoins` with a negative amount inside a `try` block, and then with a coin of value 0 in a separate `try` block. Then catch `IllegalArgumentException` from both. Finally, explain why a zero coin would make the recurrence depend on itself.

## Self-check and retrieval

From memory, state the invariant of `lowerBound` and the meaning of its result when the target is missing. Explain what a stable sort preserves, why the greedy choice fails for amount 6, and how the DP table builds `minimumCoins(6)` from smaller amounts.

## Next step

Continue with `java-021`: Threads and the memory model. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
