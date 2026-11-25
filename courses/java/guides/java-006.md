# java-006: Lists, sets and maps

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-005`

## Learning objectives

Choose a List, Set or Map for a counting task and produce deterministic output from unordered collections.

The six exercises practice these steps:

- Retain sequence multiplicity.
- Count with a map.
- Inspect set insertion.
- Create deterministic output order.
- Distinguish lookup from insertion.
- Respect unmodifiable fixtures.

## Purpose and mental model

Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.

## Vocabulary and concepts

**List:** An ordered collection retaining duplicates.

**Set:** A collection of unique equal elements.

**Map:** A mapping from unique keys to associated values.

## How to run this lesson

Exercise 4 sorts the keys because `HashMap` iteration order is unspecified and can change with capacity or JDK version, so never treat the order one run prints as a contract.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

List.of creates a fixed unmodifiable list; new ArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

## Worked example / walkthrough

### Example A: Retain sequence multiplicity

A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
    colors.add("green");
    assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;
  }
}
```

**Expected:** size 4; red appears twice.

### Example B: Count with a map

The merge function defines how repeated keys combine. Replacing put on every iteration would retain only the final contribution 1.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
    colors.add("green");
    assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;

    Map<String, Integer> counts = new HashMap<>();
    for (String color : colors) counts.merge(color, 1, Integer::sum);
    assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));
  }
}
```

**Expected:** red 2, blue 1, green 1.

## Prediction before your attempt

Before running Example A, write the size of the color list after appending green and how many times red appears. For Example B, predict each color's count after `merge(color, 1, Integer::sum)` and what the counts would be if the loop used `put(color, 1)` instead (every count would be 1). Then predict the two booleans that `HashSet.add` returns when red is inserted twice.

## Exercises

1. **Retain sequence multiplicity: change one input.** Change `List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));` to `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `colors.size() == 4 && Collections.frequency(colors, "red") == 2`.
   **Verify:** Name the value that makes `colors.size() == 4 && Collections.frequency(colors, "red") == 2` false, then restore the line.

2. **Count with a map: debug a regression.** A regression in Example B's new code makes one line read `for (String color : colors) counts.merge(color, 2, Integer::sum);`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; the repaired line reads `for (String color : colors) counts.merge(color, 1, Integer::sum);`.
   **Verify:** Explain how the changed token alters the value that `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))` tests.

3. **Inspect set insertion.** Insert red twice into a HashSet and inspect return values.
   **Expected:** first true, second false, size 1.
   **Verify:** Control: changing `boolean firstAdded = unique.add("red");` to `boolean firstAdded = unique.add("red!");` must fail the assertion on `firstAdded && !secondAdded && unique.size() == 1`.

4. **Create deterministic output order.** Sort the count-map keys before presenting them.
   **Expected:** blue, green, red.
   **Verify:** Control: changing `assert keys.equals(List.of("blue", "green", "red"));` to `assert keys.equals(List.of("blue!", "green", "red"));` inside the assertion must make it fail.

5. **Distinguish lookup from insertion.** Read missing with getOrDefault 0 and compare map size.
   **Expected:** value 0; map still size 3.
   **Verify:** Control: changing `int absent = counts.getOrDefault("missing", 0);` to `int absent = counts.getOrDefault("missing", 1);` must fail the assertion on `absent == 0 && counts.size() == before && !counts.containsKey("missing")`.

6. **Respect unmodifiable fixtures.** Try adding to List.of(1, 2) and catch the specific exception.
   **Expected:** UnsupportedOperationException.
   **Verify:** Control: changing `fixed = true;` to `fixed = false;` must fail the assertion on `fixed`.

## Common pitfalls and diagnosis

Picking the wrong collection silently loses information. Converting the color list to a `Set` drops the second red, and `put` in a counting loop overwrites the previous count instead of adding to it. Two more traps: `getOrDefault` returns a fallback without storing it, so the map size does not change, and `List.of` returns an unmodifiable list whose `add` compiles but throws `UnsupportedOperationException` when it runs.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First write the list after the edit: red!, blue, red and then green. Then count how many elements equal "red" exactly. Finally, compare that count and the size with the two parts of the assertion and say which part fails.
- **Exercise 2:** First trace `merge` for each color when 2 is the value stored for a new key. Then compare the resulting map with red 2, blue 1, green 1. Finally, explain which argument of `merge` is the starting value and which is the combining function.
- **Exercise 3:** First keep the boolean returned by each `add` call. Then insert red twice and read the set size. Finally, explain why the second `add` returns false without throwing.
- **Exercise 4:** First copy the map's key set into a new `ArrayList`. Then sort that list with `Collections.sort`. Finally, compare it with `List.of("blue", "green", "red")` and explain why the map itself made no ordering promise.
- **Exercise 5:** First record the map size before the lookup. Then call `getOrDefault("missing", 0)` and keep the value. Finally, assert that the value is 0, the size is unchanged and `containsKey("missing")` is false.
- **Exercise 6:** First call `add` on `List.of(1, 2)` inside a `try` block. Then catch `UnsupportedOperationException` and record it. Finally, explain why this fails at run time even though the `List` interface declares `add`.

## Self-check and retrieval

Explain from memory what a list keeps that a set discards, what `Map.merge` does for a new key and for an existing one, and why printing a `HashMap` is not a stable output contract. Then say how you would tell "absent" from "present with count 0" in a map.

## Next step

Continue with `java-007`: Classes and encapsulation. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-006: Lists, sets and maps.
Read courses/java/guides/java-006.md and courses/java/lessons/java-006.java. Direct prerequisites: `java-005`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
