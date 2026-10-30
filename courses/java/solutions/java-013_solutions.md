# java-013: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A lambda supplies the behavior of a functional interface, an interface with one abstract method. It can make a small transformation or predicate easier to pass around, but it does not remove the need for a contract. Captured local variables must be final or effectively final, meaning their binding is not reassigned after initialization. Capturing a reference does not make the referenced object immutable. A lambda that appends to a shared list still has a side effect and may be unsafe in a parallel stream. Separate pure transformations from actions when possible, and use named methods when a lambda becomes difficult to explain.

**Functional interface:** An interface with one abstract method that a lambda can implement.

**Capture:** Using a surrounding local value from inside a lambda.

**Pure transformation:** A computation that returns a value without changing external state.

## Reading the reference

Predicate<T> returns boolean, Function<T,R> maps a value to another value, and Consumer<T> performs an action without returning a result. Method references such asString::strip are compact forms of compatible lambdas. Function.andThen applies the first function before the second;compose reverses that composition order. A captured primitive value is read from its stable local binding, while a captured mutable object can still change internally.

## Exercise 1: Use a predicate

Task: Create a Predicate<Integer> accepting positive values and test 3,0,-1.

The predicate has a single purpose and no side effects. Boundary zero is checked explicitly rather than inferred from a positive example.

```java
java.util.function.Predicate<Integer> positive = value -> value > 0;
assert positive.test(3) && !positive.test(0) && !positive.test(-1);
```

**Expected:** true, false, false.

**Verify:** Compare the program values or named exception with true, false, false. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Compose transformations

Task: Strip a string,then uppercase it withLocale.ROOT.

The composition order is explicit. For transformations that do not commute, reversing the order changes the result.

```java
java.util.function.Function<String, String> strip = String::strip;
java.util.function.Function<String, String> upper = value -> value.toUpperCase(Locale.ROOT);
assert strip.andThen(upper).apply(" red ").equals("RED");
```

**Expected:** input space red space becomesRED.

**Verify:** Compare the program values or named exception with input space red space becomesRED. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Distinguish composition order

Task: Compose add1 andmultiply2 usingandThen and compose on3.

A small noncommuting example makes the API semantics visible. Readingcompose as if it wereandThen is a common source of subtle pipeline errors.

```java
java.util.function.Function<Integer, Integer> addOne = value -> value + 1;
java.util.function.Function<Integer, Integer> twice = value -> value * 2;
assert addOne.andThen(twice).apply(3) == 8;
assert addOne.compose(twice).apply(3) == 7;
```

**Expected:** andThen gives 8;compose7.

**Verify:** Compare the program values or named exception with andThen gives 8;compose7. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Capture a stable threshold

Task: Capture local threshold10 in a predicate and test9,10,11.

The local binding is effectively final because it is not reassigned. Changing the threshold later requires a different state design rather than silently mutating a captured primitive.

```java
int threshold = 10;
java.util.function.Predicate<Integer> enough = value -> value >= threshold;
assert !enough.test(9) && enough.test(10) && enough.test(11);
```

**Expected:** false,true,true under>=.

**Verify:** Compare the program values or named exception with false,true,true under>=. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

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

**Expected:** captured list becomesa,b.

**Verify:** Compare the program values or named exception with captured list becomesa,b. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

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

**Verify:** Compare the program values or named exception with 7 accepted; blank rejected. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
