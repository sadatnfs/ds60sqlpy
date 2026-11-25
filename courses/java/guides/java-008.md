# java-008: Constructors, records and invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-007`

## Learning objectives

Write records and constructors that normalize, copy and validate their components so every instance is valid.

The six exercises practice these steps:

- Normalize at construction.
- Copy caller-owned collections.
- Use value equality.
- Reject blank identity.
- Protect the exposed collection.
- Reject null collection members.

## Purpose and mental model

A record is a concise carrier for a fixed set of components, with generated accessors, equality, hashing and a descriptive string. It is shallowly immutable: the component references cannot be reassigned, but a mutable object referenced by a component can still change. A compact constructor can validate and normalize incoming component values before the record is created. Defensive copying is necessary when the record owns a collection. Constructor validation should reject invalid domain state consistently, so every successfully created value can be trusted to satisfy its invariant. Records are appropriate for value-like data, not a substitute for every stateful object.

## Vocabulary and concepts

**Record:** A value-oriented class with declared components and generated methods.

**Compact constructor:** Validation and normalization code for record components.

**Defensive copy:** An owned copy preventing external mutation through shared storage.

## How to run this lesson

`Order` is a record declared inside `Main` whose compact constructor trims the ID and copies the item list; Exercises 4 to 6 expect exceptions from that constructor or its list and catch them.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

record Order(String id, List<String> items) declares component accessors id() and items(). In a compact constructor, assign a normalized parameter such asid=id.strip(); implicit field assignment occurs afterward. List.copyOf makes an unmodifiable shallow copy, preventing later structural changes through the caller list. It also rejects null elements, which becomes part of the chosen contract.

## Worked example / walkthrough

### Example A: Normalize at construction

Normalization occurs once at the boundary. Every later accessor sees the canonical ID, rather than requiring callers to remember to trim it.

```java
import java.util.*;

public class Main {

  record Order(String id, List<String> items) {
    Order {
      Objects.requireNonNull(id, "id");
      id = id.strip();
      if (id.isEmpty()) throw new IllegalArgumentException("blank id");
      items = List.copyOf(items);
    }
  }

  public static void main(String[] args) throws Exception {
    Order order = new Order(" A ", List.of("x"));
    assert order.id().equals("A") && order.items().equals(List.of("x"));
  }
}
```

**Expected:** ID A and items[x].

### Example B: Copy caller-owned collections

Without the copy, a caller could change the record observed value after construction. Final component references alone would not prevent that mutation.

```java
import java.util.*;

public class Main {

  record Order(String id, List<String> items) {
    Order {
      Objects.requireNonNull(id, "id");
      id = id.strip();
      if (id.isEmpty()) throw new IllegalArgumentException("blank id");
      items = List.copyOf(items);
    }
  }

  public static void main(String[] args) throws Exception {
    Order order = new Order(" A ", List.of("x"));
    assert order.id().equals("A") && order.items().equals(List.of("x"));

    List<String> supplied = new ArrayList<>(List.of("x"));
    Order copied = new Order("B", supplied);
    supplied.add("y");
    assert copied.items().equals(List.of("x"));
  }
}
```

**Expected:** record retains its original single item.

## Prediction before your attempt

Before running Example A, write the value `order.id()` returns for the input " A " and say where the trimming happens. For Example B, predict the record's items after the caller appends to the list it passed in. Then predict whether two `Order` values built from equal components are `equals`, and whether they are the same object.

## Exercises

1. **Normalize at construction: change one input.** Change `Order order = new Order(" A ", List.of("x"));` to `Order order = new Order(" A !", List.of("x"));` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `order.id().equals("A") && order.items().equals(List.of("x"))`.
   **Verify:** Name the value that makes `order.id().equals("A") && order.items().equals(List.of("x"))` false, then restore the line.

2. **Copy caller-owned collections: debug a regression.** A regression in Example B's new code makes one line read `List<String> supplied = new ArrayList<>(List.of("x!"));`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `copied.items().equals(List.of("x"))`; the repaired line reads `List<String> supplied = new ArrayList<>(List.of("x"));`.
   **Verify:** Explain how the changed token alters the value that `copied.items().equals(List.of("x"))` tests.

3. **Use value equality.** Construct another Order with normalized A and item x.
   **Expected:** equals true and equal hashCode.
   **Verify:** Control: changing `Order same = new Order("A", List.of("x"));` to `Order same = new Order("A!", List.of("x"));` must fail the assertion on `order.equals(same) && order.hashCode() == same.hashCode()`.

4. **Reject blank identity.** Construct an Order with an all-space ID.
   **Expected:** IllegalArgumentException.
   **Verify:** Control: changing `blank = true;` to `blank = false;` must fail the assertion on `blank`.

5. **Protect the exposed collection.** Attempt to add to order.items().
   **Expected:** UnsupportedOperationException.
   **Verify:** Control: changing `protectedItems = true;` to `protectedItems = false;` must fail the assertion on `protectedItems`.

6. **Reject null collection members.** Try creating an Order whose items contains null.
   **Expected:** NullPointerException from the declared copy policy.
   **Verify:** Control: changing `nullItem = true;` to `nullItem = false;` must fail the assertion on `nullItem`.

## Common pitfalls and diagnosis

A record's components are final, but final is shallow: storing the caller's `ArrayList` directly lets the caller change the record later, so copy it with `List.copyOf` in the compact constructor. Validate after normalizing, or an ID of three spaces passes a non-empty test and then trims to blank. And `List.copyOf` rejects null elements with `NullPointerException`, so allowing missing items would need an explicit design rather than a silent pass.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First apply the compact constructor's trim to " A !" and write the resulting ID. Then compare it with the "A" the assertion expects. Finally, note that the items still match, so only the ID half of the condition fails.
- **Exercise 2:** First write the list the caller supplies after the edit. Then follow the defensive copy into the record and compare `items()` with `List.of("x")`. Finally, explain why the later append to `supplied` is not what breaks the assertion.
- **Exercise 3:** First build a second `Order` from "A" and `List.of("x")`. Then compare it with the first using `equals` and compare the two hash codes. Finally, explain which generated methods make two separate objects equal.
- **Exercise 4:** First pass an ID made only of spaces inside a `try` block. Then catch `IllegalArgumentException` and record it. Finally, confirm that the constructor trims before it tests for blank, so whitespace cannot slip through.
- **Exercise 5:** First call `order.items().add("y")` inside a `try` block. Then catch `UnsupportedOperationException`. Finally, explain why `items()` returns the record's own unmodifiable copy rather than the caller's list.
- **Exercise 6:** First build a list containing null, for example with `Arrays.asList("x", null)`, and pass it to the constructor. Then catch the `NullPointerException` that `List.copyOf` throws. Finally, explain why this rejection is a deliberate policy rather than an accident.

## Self-check and retrieval

Explain from memory what a compact constructor can do that an accessor cannot, why `List.copyOf` is both a defensive copy and an unmodifiable list, and how record equality differs from the identity equality of an ordinary class that does not override `equals`.

## Next step

Continue with `java-009`: Exceptions and resource lifetime. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-008: Constructors, records and invariants.
Read courses/java/guides/java-008.md and courses/java/lessons/java-008.java. Direct prerequisites: `java-007`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
