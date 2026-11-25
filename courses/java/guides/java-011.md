# java-011: Equality, hashing and ordering

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-010`

## Learning objectives

Implement consistent equals, hashCode and Comparator ordering and show the failures that inconsistent keys cause.

The six exercises practice these steps:

- Use immutable value keys.
- Sort with a tie-breaker.
- Expose comparator uniqueness.
- Demonstrate mutable-key failure.
- Avoid comparator subtraction.
- Keep identity and display separate.

## Purpose and mental model

Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equal hashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.

## Vocabulary and concepts

**Equality contract:** Rules defining when two values represent the same logical identity.

**Hash code:** A bucket-selection value consistent with equality.

**Comparator:** A rule ordering two values and identifying ties.

## How to run this lesson

`Point` and `Person` are records and `MutableKey` is a small class with a deliberately mutable field, all declared inside `Main`; Exercise 4 demonstrates a broken key on purpose, so a lookup that returns null is the expected result.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Records generate component-based equals and hashCode. Comparator.comparing selects a primary sort key; thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, not toString. A key should remain stable while stored. For numeric ordering use Integer.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.

## Worked example / walkthrough

### Example A: Use immutable value keys

The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.

```java
import java.util.*;

public class Main {

  record Point(int x, int y) {}

  record Person(String id, int age) {}

  static final class MutableKey {

    int value;

    MutableKey(int value) {
      this.value = value;
    }

    public int hashCode() {
      return value;
    }

    public boolean equals(Object other) {
      return other instanceof MutableKey key && key.value == value;
    }
  }

  public static void main(String[] args) throws Exception {
    Point a = new Point(0, 0),
      b = new Point(0, 0);
    Map<Point, String> map = new HashMap<>();
    map.put(a, "origin");
    assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");
  }
}
```

**Expected:** lookup with the other returns origin; hashes equal.

### Example B: Sort with a tie-breaker

The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.

```java
import java.util.*;

public class Main {

  record Point(int x, int y) {}

  record Person(String id, int age) {}

  static final class MutableKey {

    int value;

    MutableKey(int value) {
      this.value = value;
    }

    public int hashCode() {
      return value;
    }

    public boolean equals(Object other) {
      return other instanceof MutableKey key && key.value == value;
    }
  }

  public static void main(String[] args) throws Exception {
    Point a = new Point(0, 0),
      b = new Point(0, 0);
    Map<Point, String> map = new HashMap<>();
    map.put(a, "origin");
    assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");

    List<Person> people = new ArrayList<>(
      List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))
    );
    people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
    assert people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"));
  }
}
```

**Expected:** IDs c, a, b.

## Prediction before your attempt

Before running Example A, decide whether two separately constructed `Point(0, 0)` values are the same object, whether they are `equals`, and whether a map lookup with the second finds the value stored under the first. For Example B, write the sorted IDs for b aged 20, a aged 20 and c aged 18 when the comparator uses age and then ID. Before Exercise 3, predict the size of a `TreeSet` that compares only age after two different 20-year-olds are added.

## Exercises

1. **Use immutable value keys: change one input.** Change `Point a = new Point(0, 0),` to `Point a = new Point(1, 0),` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`.
   **Verify:** Name the value that makes `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")` false, then restore the line.

2. **Sort with a tie-breaker: debug a regression.** A regression in Example B's new code makes one line read `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; the repaired line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))`.
   **Verify:** Explain how the changed token alters the value that `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))` tests.

3. **Expose comparator uniqueness.** Insert two different people of age 20 into a TreeSet comparing age only.
   **Expected:** set size 1 despite unequal records.
   **Verify:** Control: changing `byAge.add(new Person("a", 20));` to `byAge.add(new Person("a", 21));` must fail the assertion on `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`.

4. **Demonstrate mutable-key failure.** Insert a key with hash 1, mutate its hash field to 2, and attempt lookup with the same object.
   **Expected:** lookup fails in this fixture while map size remains 1.
   **Verify:** Control: changing `MutableKey key = new MutableKey(1);` to `MutableKey key = new MutableKey(2);` must fail the assertion on `mutable.get(key) == null && mutable.size() == 1`.

5. **Avoid comparator subtraction.** Compare Integer.MIN_VALUE and 1 using Integer.compare.
   **Expected:** negative result; subtraction overflows positive.
   **Verify:** Control: changing `assert Integer.MIN_VALUE - 1 > 0;` to `assert Integer.MIN_VALUE + 1 > 0;` inside the assertion must make it fail.

6. **Keep identity and display separate.** Give two Points the same formatted label but different coordinates; compare values.
   **Expected:** display labels equal; points unequal.
   **Verify:** Control: changing `String labelLeft = "point",` to `String labelLeft = "point!",` must fail the assertion on `labelLeft.equals(labelRight) && !left.equals(right)`.

## Common pitfalls and diagnosis

Overriding `equals` without `hashCode` breaks hash collections: two equal keys land in different buckets and lookups miss. A comparator that returns 0 for unequal objects makes a `TreeSet` or `TreeMap` treat them as duplicates, so the second person disappears without an error. Writing a comparator as `a - b` overflows for extreme values and reverses the order; use `Integer.compare`. And mutating a field that `hashCode` reads after the key is stored strands the entry in its old bucket.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First compare `Point(1, 0)` with `Point(0, 0)` component by component. Then note that `&&` stops at the first false conjunct, so the map lookup never runs. Finally, explain which part of the record's generated `equals` reports the difference.
- **Exercise 2:** First sort the edited people by age alone: c is 18, b is 20 and a is now 21. Then check whether the ID tie-breaker is ever needed for this data. Finally, compare the resulting IDs with c, a, b and explain why the tie-breaker case is no longer tested.
- **Exercise 3:** First build a `TreeSet` with `Comparator.comparingInt(Person::age)` and add two people aged 20 with different IDs. Then read the set size and compare the two records with `equals`. Finally, explain why the set used the comparator, not `equals`, to decide membership.
- **Exercise 4:** First store a `MutableKey` whose value is 1 and then assign 2 to its field. Then look the same object up and read the map size. Finally, explain why the map searches the bucket for hash 2 while the entry still sits in the bucket chosen for hash 1.
- **Exercise 5:** First assert that `Integer.compare(Integer.MIN_VALUE, 1)` is negative. Then evaluate `Integer.MIN_VALUE - 1` and observe that it wraps to a positive value. Finally, explain how a subtraction comparator would sort the smallest `int` after 1.
- **Exercise 6:** First give two `Point` values with different coordinates the same display label. Then compare the labels with `equals` and the points with `equals`. Finally, explain why the label would be a bad map key for these points.

## Self-check and retrieval

From memory, state the rule that links `equals` and `hashCode` and why unequal objects may still share a hash. Explain why a `TreeSet` that compares only age loses a person, why the mutated `MutableKey` cannot be found, and why `Integer.MIN_VALUE - 1` is positive.

## Next step

Continue with `java-012`: Generics and variance. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-011: Equality, hashing and ordering.
Read courses/java/guides/java-011.md and courses/java/lessons/java-011.java. Direct prerequisites: `java-010`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
