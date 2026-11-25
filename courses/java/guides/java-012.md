# java-012: Generics and variance

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-011`

## Learning objectives

Use generic types and bounded wildcards so producers, consumers and return types stay type-safe.

The six exercises practice these steps:

- Read from a producer.
- Write to a consumer.
- Connect source and destination types.
- Preserve generic return type.
- Handle an empty input contract.
- Observe erasure carefully.

## Purpose and mental model

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holding List<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard ? super Integer permits adding integers, while reads are only known as Object. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

## Vocabulary and concepts

**Type parameter:** A named placeholder relating types in a declaration.

**Invariance:** Different generic arguments do not imply a subtype relationship.

**Wildcard bound:** A restriction describing safe reads or writes through a generic reference.

## How to run this lesson

Exercise 6 has no recorded control edit because its evidence is a comparison of runtime classes; the unsafe assignment it discusses must stay out of the program, since `javac` rejects it.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated as Number for summation. List<? super Integer> can accept Integer values. Use <T> void copy(List<? extends T> source, List<? super T> target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Worked example / walkthrough

### Example A: Read from a producer

The method needs only to read Number values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

```java
import java.util.*;

public class Main {

  static double sum(List<? extends Number> values) {
    double total = 0;
    for (Number value : values) total += value.doubleValue();
    return total;
  }

  static void addTwo(List<? super Integer> values) {
    values.add(1);
    values.add(2);
  }

  static <T> void copy(List<? extends T> source, List<? super T> target) {
    target.addAll(source);
  }

  static <T> T first(List<T> values) {
    if (values.isEmpty()) throw new NoSuchElementException("empty list");
    return values.get(0);
  }

  public static void main(String[] args) throws Exception {
    assert sum(List.of(1, 2, 3)) == 6.0;
    assert sum(List.of(1.5, 2.5)) == 4.0;
  }
}
```

**Expected:** sums 6.0 and 4.0.

### Example B: Write to a consumer

A Number list can safely receive Integer values. Reading through the super-bounded reference offers less precise type information because the actual list may contain other supertypes.

```java
import java.util.*;

public class Main {

  static double sum(List<? extends Number> values) {
    double total = 0;
    for (Number value : values) total += value.doubleValue();
    return total;
  }

  static void addTwo(List<? super Integer> values) {
    values.add(1);
    values.add(2);
  }

  static <T> void copy(List<? extends T> source, List<? super T> target) {
    target.addAll(source);
  }

  static <T> T first(List<T> values) {
    if (values.isEmpty()) throw new NoSuchElementException("empty list");
    return values.get(0);
  }

  public static void main(String[] args) throws Exception {
    assert sum(List.of(1, 2, 3)) == 6.0;
    assert sum(List.of(1.5, 2.5)) == 4.0;

    List<Number> numbers = new ArrayList<>();
    addTwo(numbers);
    assert numbers.equals(List.of(1, 2));
  }
}
```

**Expected:** list contains 1, 2.

## Prediction before your attempt

Before running Example A, predict whether `sum` accepts both `List.of(1, 2, 3)` and `List.of(1.5, 2.5)`, and what each returns as a `double`. For Example B, decide whether `addTwo` may receive a `List<Number>`, and what type a read through `List<? super Integer>` has (only `Object`). Then predict whether `List<Integer>` can be assigned to a `List<Number>` variable: it cannot, because the second variable would allow adding a `Double` to the first list.

## Exercises

1. **Read from a producer: predict an edited check.** Change Example A's assertion to `assert sum(List.of(2, 2, 3)) == 6.0;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `sum(List.of(1, 2, 3)) == 6.0`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `sum(List.of(1, 2, 3)) == 6.0`.

2. **Write to a consumer: diagnose an edited check.** Example B's new assertion was edited to `assert numbers.equals(List.of(2, 2));`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `numbers.equals(List.of(1, 2))`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `numbers.equals(List.of(1, 2))` accepts.

3. **Connect source and destination types.** Copy List<Integer> into List<Number> with a bounded generic method.
   **Expected:** destination contains 3, 4.
   **Verify:** Control: changing `copy(List.of(3, 4), destination);` to `copy(List.of(4, 4), destination);` must fail the assertion on `destination.equals(List.of(3, 4))`.

4. **Preserve generic return type.** Call first on a String list and assign it directly to a String.
   **Expected:** result alpha.
   **Verify:** Control: changing `String value = first(List.of("alpha", "beta"));` to `String value = first(List.of("alpha!", "beta"));` must fail the assertion on `value.equals("alpha")`.

5. **Handle an empty input contract.** Call first on an empty list and require a named failure.
   **Expected:** NoSuchElementException.
   **Verify:** Control: changing `empty = true;` to `empty = false;` must fail the assertion on `empty`.

6. **Observe erasure carefully.** Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does not permit unsafe assignments.
   **Expected:** runtime classes equal; compile-time contracts remain distinct.
   **Verify:** Name an input that would make `strings.isEmpty() && integers.isEmpty()` false and the value that changes.

## Common pitfalls and diagnosis

The intuition that `List<Integer>` is a kind of `List<Number>` is wrong, and casting through a raw `List` to force it moves the failure to a later `ClassCastException` far from the cause. Remember the producer-extends, consumer-super rule: read from `? extends`, write to `? super`. Generics also do not check values, so `first` on an empty list still needs its own `NoSuchElementException`, and erasure means you cannot test `instanceof List<String>` at run time.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First compute `sum(List.of(2, 2, 3))` from the edited assertion. Then compare it with the 6.0 that the assertion still expects. Finally, decide whether the method or the edited claim is wrong, and restore the original elements.
- **Exercise 2:** First write the contents of `numbers` after `addTwo` appends 1 and 2. Then compare it with `List.of(2, 2)` from the edited assertion. Finally, explain why the method's wildcard is not involved in this failure.
- **Exercise 3:** First declare `copy` with one type parameter `T`, a source of `List<? extends T>` and a destination of `List<? super T>`. Then call it with a `List<Integer>` and an empty `ArrayList<Number>`. Finally, compare the destination with 3, 4 and say which type the compiler inferred for `T`.
- **Exercise 4:** First declare `static <T> T first(List<T> values)`. Then assign `first(List.of("alpha", "beta"))` to a `String` without a cast. Finally, explain how the type argument flows from the list to the return value.
- **Exercise 5:** First call `first` on an empty list inside a `try` block. Then catch `NoSuchElementException` and record it. Finally, explain why the type system cannot rule out an empty list.
- **Exercise 6:** First create an `ArrayList<String>` and an `ArrayList<Integer>`. Then compare their `getClass()` values with `==`. Finally, explain why erasure makes them equal at run time while the compiler still rejects assigning one to the other.

## Self-check and retrieval

From memory, explain why lists are invariant and what would go wrong if they were not. Then say which wildcard `sum` uses and why it cannot add, which wildcard `addTwo` uses and why its reads are `Object`, and how the type parameter in `copy` links source and destination.

## Next step

Continue with `java-013`: Lambdas and functional interfaces. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-012: Generics and variance.
Read courses/java/guides/java-012.md and courses/java/lessons/java-012.java. Direct prerequisites: `java-011`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
