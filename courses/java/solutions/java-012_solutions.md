# java-012: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holding List<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard ? super Integer permits adding integers, while reads are only known as Object. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

**Type parameter:** A named placeholder relating types in a declaration.

**Invariance:** Different generic arguments do not imply a subtype relationship.

**Wildcard bound:** A restriction describing safe reads or writes through a generic reference.

## Reading the reference

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated as Number for summation. List<? super Integer> can accept Integer values. Use <T> void copy(List<? extends T> source, List<? super T> target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Exercise 1: Read from a producer: predict an edited check

Task: Change Example A's assertion to `assert sum(List.of(2, 2, 3)) == 6.0;`, predict whether it holds, then run and restore it.

The method needs only to read Number values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

The unchanged code is the part that Example A adds:

```java
assert sum(List.of(1, 2, 3)) == 6.0;
assert sum(List.of(1.5, 2.5)) == 4.0;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `sum(List.of(1, 2, 3)) == 6.0`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `sum(List.of(1, 2, 3)) == 6.0`.

## Exercise 2: Write to a consumer: diagnose an edited check

Task: Example B's new assertion was edited to `assert numbers.equals(List.of(2, 2));`. Explain why it fails for unchanged state and restore it.

A Number list can safely receive Integer values. Reading through the super-bounded reference offers less precise type information because the actual list may contain other supertypes.

The unchanged code is the part that Example B adds:

```java
List<Number> numbers = new ArrayList<>();
addTwo(numbers);
assert numbers.equals(List.of(1, 2));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `numbers.equals(List.of(1, 2))`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `numbers.equals(List.of(1, 2))` accepts.

## Exercise 3: Connect source and destination types

Task: Copy List<Integer> into List<Number> with a bounded generic method.

The same type parameter links the producer and consumer. It permits safe widening without an unchecked cast.

```java
List<Number> destination = new ArrayList<>();
copy(List.of(3, 4), destination);
assert destination.equals(List.of(3, 4));
```

**Expected:** destination contains 3, 4.

**Verify:** Control: changing `copy(List.of(3, 4), destination);` to `copy(List.of(4, 4), destination);` must fail the assertion on `destination.equals(List.of(3, 4))`.

## Exercise 4: Preserve generic return type

Task: Call first on a String list and assign it directly to a String.

The generic signature carries the element type to the return value. A raw Object return would force callers to cast and shift failures to runtime.

```java
String value = first(List.of("alpha", "beta"));
assert value.equals("alpha");
```

**Expected:** result alpha.

**Verify:** Control: changing `String value = first(List.of("alpha", "beta"));` to `String value = first(List.of("alpha!", "beta"));` must fail the assertion on `value.equals("alpha")`.

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

**Verify:** Control: changing `empty = true;` to `empty = false;` must fail the assertion on `empty`.

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

**Verify:** Name an input that would make `strings.isEmpty() && integers.isEmpty()` false and the value that changes.

## After comparing the answer

Try to call `sum` on a `List<String>` in your copy, read the compiler error, and explain which bound rejected it.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
