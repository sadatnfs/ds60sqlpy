# java-012: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holding List<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard ? super Integer permits adding integers, while reads are only known as Object. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

**Type parameter:** A named placeholder relating types in a declaration.

**Invariance:** Different generic arguments do not imply a subtype relationship.

**Wildcard bound:** A restriction describing safe reads or writes through a generic reference.

## Reading the reference

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated as Number for summation. List<? super Integer> can accept Integer values. Use <T> void copy(List<? extends T> source, List<? super T> target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Exercise 1: Read from a producer: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert sum(List.of(1, 2, 3)) == 6.0;` to `assert sum(List.of(2, 2, 3)) == 6.0;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

The method needs only to read Number values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

The unchanged code is the part that Example A adds:

```java
assert sum(List.of(1, 2, 3)) == 6.0;
assert sum(List.of(1.5, 2.5)) == 4.0;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `sum(List.of(1, 2, 3)) == 6.0`. Restoring the original line brings back the worked observation: sums 6.0 and 4.0.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `sum(List.of(1, 2, 3)) == 6.0`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Write to a consumer: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert numbers.equals(List.of(2, 2));`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

A Number list can safely receive Integer values. Reading through the super-bounded reference offers less precise type information because the actual list may contain other supertypes.

The unchanged code is the part that Example B adds:

```java
List<Number> numbers = new ArrayList<>();
addTwo(numbers);
assert numbers.equals(List.of(1, 2));
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `numbers.equals(List.of(1, 2))`; after it the line reads `assert numbers.equals(List.of(1, 2));` again and list contains 1, 2.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `numbers.equals(List.of(1, 2))` accepts.

## Exercise 3: Connect source and destination types

Task: Copy List<Integer> into List<Number> with a bounded generic method.

The same type parameter links the producer and consumer. It permits safe widening without an unchecked cast.

```java
List<Number> destination = new ArrayList<>();
copy(List.of(3, 4), destination);
assert destination.equals(List.of(3, 4));
```

**Expected:** destination contains 3, 4.

**Verify:** Keep an assertion equivalent to `destination.equals(List.of(3, 4))`. As a control, change `copy(List.of(3, 4), destination);` to `copy(List.of(4, 4), destination);`: the run must fail with an `AssertionError` from the assertion on `destination.equals(List.of(3, 4))`. Restore the line before continuing.

## Exercise 4: Preserve generic return type

Task: Call first on a String list and assign it directly to a String.

The generic signature carries the element type to the return value. A raw Object return would force callers to cast and shift failures to runtime.

```java
String value = first(List.of("alpha", "beta"));
assert value.equals("alpha");
```

**Expected:** result alpha.

**Verify:** Keep an assertion equivalent to `value.equals("alpha")`. As a control, change `String value = first(List.of("alpha", "beta"));` to `String value = first(List.of("alpha!", "beta"));`: the run must fail with an `AssertionError` from the assertion on `value.equals("alpha")`. Restore the line before continuing.

## Exercise 5: Handle an empty input contract

Task: Call first on an empty list and require a named failure.

Type safety does not establish nonemptiness. A separate value-level precondition is still needed for an operation that requires an element.

```java
boolean empty = false;
try {
  first(List.of());
} catch (NoSuchElementException expected) {
  empty = true;
}
assert empty;
```

**Expected:** NoSuchElementException.

**Verify:** Keep an assertion equivalent to `empty`. As a control, change `empty = true;` to `empty = false;`: the run must fail with an `AssertionError` from the assertion on `empty`. Restore the line before continuing.

## Exercise 6: Observe erasure carefully

Task: Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does not permit unsafe assignments.

Erasure describes runtime representation. It does not repeal the compiler rule that List<Integer> cannot be assigned toList<Number>. Do not use raw casts to bypass that rule.

```java
var strings = new ArrayList<String>();
var integers = new ArrayList<Integer>();
assert strings.getClass().equals(integers.getClass());
assert strings.isEmpty() && integers.isEmpty();
```

**Expected:** runtime classes equal; compile-time contracts remain distinct.

**Verify:** Keep an assertion equivalent to `strings.isEmpty() && integers.isEmpty()` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
