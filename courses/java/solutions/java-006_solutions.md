# java-006: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.

**List:** An ordered collection retaining duplicates.

**Set:** A collection of unique equal elements.

**Map:** A mapping from unique keys to associated values.

## Reading the reference

List.of creates a fixed unmodifiable list; new ArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

## Exercise 1: Retain sequence multiplicity: change one input

Task: Change `List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));` to `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));` in Example A and predict which assertion fails and why.

A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.

The unchanged code is the part that Example A adds:

```java
List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
colors.add("green");
assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `colors.size() == 4 && Collections.frequency(colors, "red") == 2`.

**Verify:** Name the value that makes `colors.size() == 4 && Collections.frequency(colors, "red") == 2` false, then restore the line.

## Exercise 2: Count with a map: debug a regression

Task: A regression in Example B's new code makes one line read `for (String color : colors) counts.merge(color, 2, Integer::sum);`. Repair it using the failing assertion.

The merge function defines how repeated keys combine. Replacing put on every iteration would retain only the final contribution 1.

The unchanged code is the part that Example B adds:

```java
Map<String, Integer> counts = new HashMap<>();
for (String color : colors) counts.merge(color, 1, Integer::sum);
assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; the repaired line reads `for (String color : colors) counts.merge(color, 1, Integer::sum);`.

**Verify:** Explain how the changed token alters the value that `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))` tests.

## Exercise 3: Inspect set insertion

Task: Insert red twice into a HashSet and inspect return values.

The boolean return indicates whether membership changed. It does not count how many times the input value was observed.

```java
Set<String> unique = new HashSet<>();
boolean firstAdded = unique.add("red");
boolean secondAdded = unique.add("red");
assert firstAdded && !secondAdded && unique.size() == 1;
```

**Expected:** first true, second false, size 1.

**Verify:** Control: changing `boolean firstAdded = unique.add("red");` to `boolean firstAdded = unique.add("red!");` must fail the assertion on `firstAdded && !secondAdded && unique.size() == 1`.

## Exercise 4: Create deterministic output order

Task: Sort the count-map keys before presenting them.

A HashMap may iterate consistently in one run without promising that order. Sorting makes the presentation contract independent of internal hashing layout.

```java
List<String> keys = new ArrayList<>(counts.keySet());
Collections.sort(keys);
assert keys.equals(List.of("blue", "green", "red"));
```

**Expected:** blue, green, red.

**Verify:** Control: changing `assert keys.equals(List.of("blue", "green", "red"));` to `assert keys.equals(List.of("blue!", "green", "red"));` inside the assertion must make it fail.

## Exercise 5: Distinguish lookup from insertion

Task: Read missing with getOrDefault 0 and compare map size.

A fallback value is not a stored entry. This distinction matters when zero is a legitimate observation and absence has different meaning.

```java
int before = counts.size();
int absent = counts.getOrDefault("missing", 0);
assert absent == 0 && counts.size() == before && !counts.containsKey("missing");
```

**Expected:** value 0; map still size 3.

**Verify:** Control: changing `int absent = counts.getOrDefault("missing", 0);` to `int absent = counts.getOrDefault("missing", 1);` must fail the assertion on `absent == 0 && counts.size() == before && !counts.containsKey("missing")`.

## Exercise 6: Respect unmodifiable fixtures

Task: Try adding to List.of(1, 2) and catch the specific exception.

An unmodifiable collection prevents structural mutation through that interface. Mutable elements inside such a collection still need their own ownership policy.

```java
boolean fixed = false;
try {
  List.of(1, 2).add(3);
} catch (UnsupportedOperationException expected) {
  fixed = true;
}
assert fixed;
```

**Expected:** UnsupportedOperationException.

**Verify:** Control: changing `fixed = true;` to `fixed = false;` must fail the assertion on `fixed`.

## After comparing the answer

Replace the sorted key list in your copy with a `TreeMap` built from the counts and confirm that it iterates blue, green, red without a separate sort.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
