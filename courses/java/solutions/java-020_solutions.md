# java-020: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys, which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case; memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## Reading the reference

A lower-bound search returns the first index whose value is at least the target, or length if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming table dp[amount] stores the minimum coin count for that exact amount, with dp[0]=0 and an unreachable sentinel. Each transition considers a smaller amount and one added coin.

## Exercise 1: Find the first duplicate boundary: change one input

Task: Copy Example A into a scratch `Main.java` and change `int[] sorted = { 1, 2, 2, 5 };` to `int[] sorted = { 2, 2, 2, 5 };`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.

The unchanged code is the part that Example A adds:

```java
int[] sorted = { 1, 2, 2, 5 };
assert lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`. Restoring the original line brings back the worked observation: indices 1 and 4.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Handle empty and outside searches: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert lowerBound(new int[1], 7) == 0;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

The half-open interval starts empty for an empty input. The result is an insertion position, not necessarily the index of an existing match.

The unchanged code is the part that Example B adds:

```java
assert lowerBound(new int[0], 7) == 0;
assert lowerBound(sorted, 0) == 0;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `lowerBound(new int[0], 7) == 0`; after it the line reads `assert lowerBound(new int[0], 7) == 0;` again and both return 0.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `lowerBound(new int[0], 7) == 0` accepts.

## Exercise 3: Preserve stable ties

Task: Sort records (a, 2), (b, 1) and (c, 2) by key only and inspect the equal-key order.

The two key 2 records retain their original a-before-c order. Adding an explicit secondary comparator would intentionally define a different tie rule.

```java
List<Item> items = new ArrayList<>(
  List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))
);
items.sort(Comparator.comparingInt(Item::key));
assert items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"));
```

**Expected:** IDs b, a, c.

**Verify:** Keep an assertion equivalent to `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`. As a control, change `List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))` to `List.of(new Item("a", 3), new Item("b", 1), new Item("c", 2))`: the run must fail with an `AssertionError` from the assertion on `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`. Restore the line before continuing.

## Exercise 4: Solve a greedy counterexample

Task: Find minimum coins for amount 6 using coins 1, 3, 4.

The best first coin does not necessarily belong to the globally best solution. The table compares all valid smaller-amount transitions.

```java
assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;
```

**Expected:** 2 coins, using 3+3 rather than 4+1+1.

**Verify:** Keep an assertion equivalent to `minimumCoins(6, new int[] { 1, 3, 4 }) == 2`. As a control, change `assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;` to `assert minimumCoins(6, new int[] { 1, 4, 4 }) == 2;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 5: Represent an unreachable amount

Task: Solve amount 3 with only coin 2 and amount 0 with any positive coins.

Zero is the base case, while -1 is an explicit unreachable result. Confusing them would make an impossible amount look solvable with no coins.

```java
assert minimumCoins(3, new int[] { 2 }) == -1;
assert minimumCoins(0, new int[] { 2, 5 }) == 0;
```

**Expected:** -1 for unreachable amount 3; 0 for amount 0.

**Verify:** Keep an assertion equivalent to `minimumCoins(0, new int[] { 2, 5 }) == 0`. As a control, change `assert minimumCoins(0, new int[] { 2, 5 }) == 0;` to `assert minimumCoins(1, new int[] { 2, 5 }) == 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Reject invalid recurrence inputs

Task: Pass a negative amount or a zero-valued coin.

A zero coin would not reduce the subproblem and violates the intended recurrence. Validation prevents an ill-defined algorithm rather than relying on an accidental loop bound.

```java
boolean negative = false,
  zeroCoin = false;
try {
  minimumCoins(-1, new int[] { 1 });
} catch (IllegalArgumentException expected) {
  negative = true;
}
try {
  minimumCoins(3, new int[] { 0, 1 });
} catch (IllegalArgumentException expected) {
  zeroCoin = true;
}
assert negative && zeroCoin;
```

**Expected:** IllegalArgumentException for both.

**Verify:** Keep an assertion equivalent to `negative && zeroCoin`. As a control, change `minimumCoins(3, new int[] { 0, 1 });` to `minimumCoins(3, new int[] { 1, 1 });`: the run must fail with an `AssertionError` from the assertion on `negative && zeroCoin`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
