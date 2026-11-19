# java-006: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.

**List:** An ordered collection retaining duplicates.

**Set:** A collection of unique equal elements.

**Map:** A mapping from unique keys to associated values.

## Reading the reference

List.of creates a fixed unmodifiable list; new ArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

## Exercise 1: Retain sequence multiplicity: change one input

Task: Copy Example A into a scratch `Main.java` and change `List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));` to `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.

The unchanged code is the part that Example A adds:

```java
List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
colors.add("green");
assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `colors.size() == 4 && Collections.frequency(colors, "red") == 2`. Restoring the original line brings back the worked observation: size 4; red appears twice.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `colors.size() == 4 && Collections.frequency(colors, "red") == 2` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Count with a map: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (String color : colors) counts.merge(color, 2, Integer::sum);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The merge function defines how repeated keys combine. Replacing put on every iteration would retain only the final contribution 1.

The unchanged code is the part that Example B adds:

```java
Map<String, Integer> counts = new HashMap<>();
for (String color : colors) counts.merge(color, 1, Integer::sum);
assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; after it the line reads `for (String color : colors) counts.merge(color, 1, Integer::sum);` again and red 2, blue 1, green 1.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))` for this input.

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

**Verify:** Keep an assertion equivalent to `firstAdded && !secondAdded && unique.size() == 1`. As a control, change `boolean firstAdded = unique.add("red");` to `boolean firstAdded = unique.add("red!");`: the run must fail with an `AssertionError` from the assertion on `firstAdded && !secondAdded && unique.size() == 1`. Restore the line before continuing.

## Exercise 4: Create deterministic output order

Task: Sort the count-map keys before presenting them.

A HashMap may iterate consistently in one run without promising that order. Sorting makes the presentation contract independent of internal hashing layout.

```java
List<String> keys = new ArrayList<>(counts.keySet());
Collections.sort(keys);
assert keys.equals(List.of("blue", "green", "red"));
```

**Expected:** blue, green, red.

**Verify:** Keep an assertion equivalent to `keys.equals(List.of("blue", "green", "red"))`. As a control, change `assert keys.equals(List.of("blue", "green", "red"));` to `assert keys.equals(List.of("blue!", "green", "red"));` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 5: Distinguish lookup from insertion

Task: Read missing with getOrDefault 0 and compare map size.

A fallback value is not a stored entry. This distinction matters when zero is a legitimate observation and absence has different meaning.

```java
int before = counts.size();
int absent = counts.getOrDefault("missing", 0);
assert absent == 0 && counts.size() == before && !counts.containsKey("missing");
```

**Expected:** value 0; map still size 3.

**Verify:** Keep an assertion equivalent to `absent == 0 && counts.size() == before && !counts.containsKey("missing")`. As a control, change `int absent = counts.getOrDefault("missing", 0);` to `int absent = counts.getOrDefault("missing", 1);`: the run must fail with an `AssertionError` from the assertion on `absent == 0 && counts.size() == before && !counts.containsKey("missing")`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `fixed`. As a control, change `fixed = true;` to `fixed = false;`: the run must fail with an `AssertionError` from the assertion on `fixed`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
