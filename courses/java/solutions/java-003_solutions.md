# java-003: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error. A switch expression chooses one value from several labeled cases, and the compiler can check that every possible input has a case.

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

**Switch expression:** A switch that evaluates to one value and must cover every possible input.

## Reading the reference

if selects a branch. && evaluates the right operand only when the left is true; || evaluates it only when needed. A for loop has initialization, condition and update. Use index < length for zero-based arrays. The prefix-sum invariant starts with index 0, sum 0, then adds exactly the element at the current index before advancing. Break exits the loop; continue skips to the next iteration and can accidentally bypass an update in a while loop. In a switch expression, each case label is followed by -> and one result; labels never fall through, and an expression switch must cover every value of its input type.

## Exercise 1: Guard a nullable value: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert !nonempty;` to `assert nonempty;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

The right operand is not evaluated when the left is false. Reversing the operands would attempt the method call before the guard.

The unchanged code is the part that Example A adds:

```java
String text = null;
boolean nonempty = text != null && !text.isEmpty();
assert !nonempty;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `!nonempty`. Restoring the original line brings back the worked observation: condition false with no NullPointerException.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `!nonempty`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Trace a prefix sum: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `sum -= values[i];`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; after it the line reads `sum += values[i];` again and prefix sums 2, 6, 12; final 12.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `prefixes.equals(List.of(2, 6, 12)) && sum == 12` for this input.

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

**Verify:** Keep an assertion equivalent to `emptySum == 0 && iterations == 0`. As a control, change `int emptySum = 0;` to `int emptySum = 1;`: the run must fail with an `AssertionError` from the assertion on `emptySum == 0 && iterations == 0`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `kinds.equals(List.of("weekend", "weekday"))`. As a control, change `case SATURDAY, SUNDAY -> "weekend";` to `case SATURDAY, SUNDAY -> "weekend!";`: the run must fail with an `AssertionError` from the assertion on `kinds.equals(List.of("weekend", "weekday"))`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `found == 1`. As a control, change `if (items[i] == 8) {` to `if (items[i] != 8) {`: the run must fail with an `AssertionError` from the assertion on `found == 1`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `failed`. As a control, change `for (int i = 0; i <= single.length; i++) {` to `for (int i = 0; i < single.length; i++) {`: the run must fail with an `AssertionError` from the assertion on `failed`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
