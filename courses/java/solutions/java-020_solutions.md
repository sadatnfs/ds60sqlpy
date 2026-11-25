# java-020: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys, which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case; memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## Reading the reference

A lower-bound search returns the first index whose value is at least the target, or length if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming table `dp[amount]` stores the minimum coin count for that exact amount, with `dp[0] = 0` and an unreachable sentinel. Each transition considers a smaller amount and one added coin.

## Exercise 1: Find the first duplicate boundary: change one input

Task: Change `int[] sorted = { 1, 2, 2, 5 };` to `int[] sorted = { 2, 2, 2, 5 };` in Example A and predict which assertion fails and why.

Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.

The unchanged code is the part that Example A adds:

```java
int[] sorted = { 1, 2, 2, 5 };
assert lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`.

**Verify:** Name the value that makes `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4` false, then restore the line.

## Exercise 2: Handle empty and outside searches: diagnose an edited check

Task: Example B's new assertion was edited to `assert lowerBound(new int[1], 7) == 0;`. Explain why it fails for unchanged state and restore it.

The half-open interval starts empty for an empty input. The result is an insertion position, not necessarily the index of an existing match.

The unchanged code is the part that Example B adds:

```java
assert lowerBound(new int[0], 7) == 0;
assert lowerBound(sorted, 0) == 0;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `lowerBound(new int[0], 7) == 0`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `lowerBound(new int[0], 7) == 0` accepts.

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

**Verify:** Control: changing `List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))` to `List.of(new Item("a", 3), new Item("b", 1), new Item("c", 2))` must fail the assertion on `items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"))`.

## Exercise 4: Solve a greedy counterexample

Task: Find minimum coins for amount 6 using coins 1, 3, 4.

The best first coin does not necessarily belong to the globally best solution. The table compares all valid smaller-amount transitions.

```java
assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;
```

**Expected:** 2 coins, using 3+3 rather than 4+1+1.

**Verify:** Control: changing `assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;` to `assert minimumCoins(6, new int[] { 1, 4, 4 }) == 2;` inside the assertion must make it fail.

## Exercise 5: Represent an unreachable amount

Task: Solve amount 3 with only coin 2 and amount 0 with any positive coins.

Zero is the base case, while -1 is an explicit unreachable result. Confusing them would make an impossible amount look solvable with no coins.

```java
assert minimumCoins(3, new int[] { 2 }) == -1;
assert minimumCoins(0, new int[] { 2, 5 }) == 0;
```

**Expected:** -1 for unreachable amount 3; 0 for amount 0.

**Verify:** Control: changing `assert minimumCoins(0, new int[] { 2, 5 }) == 0;` to `assert minimumCoins(1, new int[] { 2, 5 }) == 0;` inside the assertion must make it fail.

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

**Verify:** Control: changing `minimumCoins(3, new int[] { 0, 1 });` to `minimumCoins(3, new int[] { 1, 1 });` must fail the assertion on `negative && zeroCoin`.

## After comparing the answer

Add a helper `upperBound` to your copy and confirm that `upperBound - lowerBound` counts the two 2s in the sorted fixture.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
