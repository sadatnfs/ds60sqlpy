# java-013: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A lambda supplies the behavior of a functional interface, an interface with one abstract method. It can make a small transformation or predicate easier to pass around, but it does not remove the need for a contract. Captured local variables must be final or effectively final, meaning their binding is not reassigned after initialization. Capturing a reference does not make the referenced object immutable. A lambda that appends to a shared list still has a side effect and may be unsafe in a parallel stream. Separate pure transformations from actions when possible, and use named methods when a lambda becomes difficult to explain.

**Functional interface:** An interface with one abstract method that a lambda can implement.

**Capture:** Using a surrounding local value from inside a lambda.

**Pure transformation:** A computation that returns a value without changing external state.

## Reading the reference

Predicate<T> returns boolean, Function<T, R> maps a value to another value, and Consumer<T> performs an action without returning a result. Method references such as String::strip are compact forms of compatible lambdas. Function.andThen applies the first function before the second; compose reverses that composition order. A captured primitive value is read from its stable local binding, while a captured mutable object can still change internally.

## Exercise 1: Use a predicate: predict an edited check

Task: Change Example A's assertion to `assert positive.test(3) && !positive.test(1) && !positive.test(-1);`, predict whether it holds, then run and restore it.

The predicate has a single purpose and no side effects. Boundary zero is checked explicitly rather than inferred from a positive example.

The unchanged code is the part that Example A adds:

```java
java.util.function.Predicate<Integer> positive = value -> value > 0;
assert positive.test(3) && !positive.test(0) && !positive.test(-1);
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `positive.test(3) && !positive.test(0) && !positive.test(-1)`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `positive.test(3) && !positive.test(0) && !positive.test(-1)`.

## Exercise 2: Compose transformations: diagnose an edited check

Task: Example B's new assertion was edited to `assert strip.andThen(upper).apply(" red !").equals("RED");`. Explain why it fails for unchanged state and restore it.

The composition order is explicit. For transformations that do not commute, reversing the order changes the result.

The unchanged code is the part that Example B adds:

```java
java.util.function.Function<String, String> strip = String::strip;
java.util.function.Function<String, String> upper = value -> value.toUpperCase(Locale.ROOT);
assert strip.andThen(upper).apply(" red ").equals("RED");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `strip.andThen(upper).apply(" red ").equals("RED")`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `strip.andThen(upper).apply(" red ").equals("RED")` accepts.

## Exercise 3: Distinguish composition order

Task: Compose add 1 and multiply 2 using andThen and compose on 3.

A small noncommuting example makes the API semantics visible. Reading compose as if it were andThen is a common source of subtle pipeline errors.

```java
java.util.function.Function<Integer, Integer> addOne = value -> value + 1;
java.util.function.Function<Integer, Integer> twice = value -> value * 2;
assert addOne.andThen(twice).apply(3) == 8;
assert addOne.compose(twice).apply(3) == 7;
```

**Expected:** andThen gives 8; compose 7.

**Verify:** Control: changing `assert addOne.compose(twice).apply(3) == 7;` to `assert addOne.compose(twice).apply(4) == 7;` inside the assertion must make it fail.

## Exercise 4: Capture a stable threshold

Task: Capture local threshold 10 in a predicate and test 9, 10, 11.

The local binding is effectively final because it is not reassigned. Changing the threshold later requires a different state design rather than silently mutating a captured primitive.

```java
int threshold = 10;
java.util.function.Predicate<Integer> enough = value -> value >= threshold;
assert !enough.test(9) && enough.test(10) && enough.test(11);
```

**Expected:** false, true, true under>=.

**Verify:** Control: changing `java.util.function.Predicate<Integer> enough = value -> value >= threshold;` to `java.util.function.Predicate<Integer> enough = value -> value > threshold;` must fail the assertion on `!enough.test(9) && enough.test(10) && enough.test(11)`.

## Exercise 5: Expose mutable captured state

Task: Capture a list in a Consumer and append two values.

The reference binding is stable, but the list remains mutable. This action should not be treated as a pure mapper or assumed safe under concurrent execution.

```java
List<String> captured = new ArrayList<>();
java.util.function.Consumer<String> append = captured::add;
append.accept("a");
append.accept("b");
assert captured.equals(List.of("a", "b"));
```

**Expected:** captured list becomes a, b.

**Verify:** Control: changing `append.accept("a");` to `append.accept("a!");` must fail the assertion on `captured.equals(List.of("a", "b"))`.

## Exercise 6: Use a named function for a contract

Task: Pass a method reference to a parser that rejects blank input and parses a positive integer.

A named helper makes validation and failure behavior easier to document than a long inline lambda. Function syntax does not imply that exceptions disappear.

```java
java.util.function.Function<String, Integer> parser = Main::parsePositive;
assert parser.apply("7") == 7;
boolean blank = false;
try {
  parser.apply(" ");
} catch (IllegalArgumentException expected) {
  blank = true;
}
assert blank;
```

**Expected:** 7 accepted; blank rejected.

**Verify:** Control: changing `blank = true;` to `blank = false;` must fail the assertion on `blank`.

## After comparing the answer

Rewrite the threshold predicate in your copy as a method `static boolean enough(int value)` and pass it as `Main::enough`; confirm that the three checks still give false, true, true.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
