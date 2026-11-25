# java-003: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error. A switch expression chooses one value from several labeled cases, and the compiler can check that every possible input has a case.

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

**Switch expression:** A switch that evaluates to one value and must cover every possible input.

## Reading the reference

if selects a branch. && evaluates the right operand only when the left is true; || evaluates it only when needed. A for loop has initialization, condition and update. Use index < length for zero-based arrays. The prefix-sum invariant starts with index 0, sum 0, then adds exactly the element at the current index before advancing. Break exits the loop; continue skips to the next iteration and can accidentally bypass an update in a while loop. In a switch expression, each case label is followed by -> and one result; labels never fall through, and an expression switch must cover every value of its input type.

## Exercise 1: Guard a nullable value: predict an edited check

Task: Change Example A's assertion to `assert nonempty;`, predict whether it holds, then run and restore it.

The right operand is not evaluated when the left is false. Reversing the operands would attempt the method call before the guard.

The unchanged code is the part that Example A adds:

```java
String text = null;
boolean nonempty = text != null && !text.isEmpty();
assert !nonempty;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `!nonempty`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `!nonempty`.

## Exercise 2: Trace a prefix sum: debug a regression

Task: A regression in Example B's new code makes one line read `sum -= values[i];`. Repair it using the failing assertion.

The accumulator begins at the additive identity 0. Each iteration adds one new element, so no record is skipped or counted twice.

The unchanged code is the part that Example B adds:

```java
int[] values = { 2, 4, 6 };
int sum = 0;
List<Integer> prefixes = new ArrayList<>();
for (int i = 0; i < values.length; i++) {
  sum += values[i];
  prefixes.add(sum);
}
assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; the repaired line reads `sum += values[i];`.

**Verify:** Explain how the changed token alters the value that `prefixes.equals(List.of(2, 6, 12)) && sum == 12` tests.

## Exercise 3: Handle an empty loop

Task: Run the same sum pattern over an empty int array.

An empty collection is a valid case for this sum contract. The initial value already represents the result, so no special fabricated element is needed.

```java
int emptySum = 0;
int iterations = 0;
for (int value : new int[0]) {
  emptySum += value;
  iterations++;
}
assert emptySum == 0 && iterations == 0;
```

**Expected:** sum 0 and zero iterations.

**Verify:** Control: changing `int emptySum = 0;` to `int emptySum = 1;` must fail the assertion on `emptySum == 0 && iterations == 0`.

## Exercise 4: Choose a value with a switch expression

Task: Classify Saturday and Wednesday with one exhaustive switch expression over java.time.DayOfWeek.

A switch expression produces exactly one value, and arrow labels never fall through to the next case. Because the cases name every DayOfWeek constant, the compiler accepts the switch without a default; leaving one constant out would be a compile-time error instead of a silent fallback. Since Java 21 a switch can also match types and record patterns, which java-010 uses.

```java
List<String> kinds = new ArrayList<>();
var days = List.of(java.time.DayOfWeek.SATURDAY, java.time.DayOfWeek.WEDNESDAY);
for (java.time.DayOfWeek day : days) {
  String kind = switch (day) {
    case SATURDAY, SUNDAY -> "weekend";
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "weekday";
  };
  kinds.add(kind);
}
assert kinds.equals(List.of("weekend", "weekday"));
```

**Expected:** weekend, then weekday.

**Verify:** Control: changing `case SATURDAY, SUNDAY -> "weekend";` to `case SATURDAY, SUNDAY -> "weekend!";` must fail the assertion on `kinds.equals(List.of("weekend", "weekday"))`.

## Exercise 5: Stop at the first match

Task: Search 3, 8, 8 for the first 8 and stop immediately.

Without the break, later matches would overwrite the first index. The sentinel -1 represents absence and cannot be mistaken for index 0.

```java
int[] items = { 3, 8, 8 };
int found = -1;
for (int i = 0; i < items.length; i++) {
  if (items[i] == 8) {
    found = i;
    break;
  }
}
assert found == 1;
```

**Expected:** index 1.

**Verify:** Control: changing `if (items[i] == 8) {` to `if (items[i] != 8) {` must fail the assertion on `found == 1`.

## Exercise 6: Expose a wrong boundary

Task: Compare a loop using i <= length with the valid i < length contract on a one-element array.

The invalid condition reaches index 1 when length 1. This tiny counterexample localizes the off-by-one error more clearly than a large dataset.

```java
boolean failed = false;
int[] single = { 7 };
try {
  for (int i = 0; i <= single.length; i++) {
    int ignored = single[i];
  }
} catch (ArrayIndexOutOfBoundsException expected) {
  failed = true;
}
assert failed;
```

**Expected:** wrong loop raises ArrayIndexOutOfBoundsException.

**Verify:** Control: changing `for (int i = 0; i <= single.length; i++) {` to `for (int i = 0; i < single.length; i++) {` must fail the assertion on `failed`.

## After comparing the answer

Rewrite the reference search loop without `break`, using a loop condition that stops at the first match, and confirm that the same assertion on index 1 still passes.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
