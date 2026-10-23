# java-006: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.

**List:** An ordered collection retaining duplicates.

**Set:** A collection of unique equal elements.

**Map:** A mapping from unique keys to associated values.

## Reading the reference

List.of creates a fixed unmodifiable list; newArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

## Exercise 1: Retain sequence multiplicity

Task: Create a mutable list red,blue,red and append green.

A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.

```java
List<String> colors = new ArrayList<>(List.of("red", "blue", "red")); colors.add("green");
assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;
```

**Expected:** size 4; red appears twice.

**Verify:** Compare the program values or named exception with size 4; red appears twice. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Count with a map

Task: Count each color withMap.merge.

The merge function defines how repeated keys combine. Replacingput on every iteration would retain only the final contribution1.

```java
Map<String, Integer> counts = new HashMap<>();
for (String color : colors) counts.merge(color, 1, Integer::sum);
assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));
```

**Expected:** red2,blue1,green1.

**Verify:** Compare the program values or named exception with red2,blue1,green1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Inspect set insertion

Task: Insertred twice into a HashSet and inspect return values.

The boolean return indicates whether membership changed. It does not count how many times the input value was observed.

```java
Set<String> unique = new HashSet<>();
assert unique.add("red"); assert !unique.add("red"); assert unique.size() == 1;
```

**Expected:** first true,second false,size1.

**Verify:** Compare the program values or named exception with first true,second false,size1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Create deterministic output order

Task: Sort the count-map keys before presenting them.

A HashMap may iterate consistently in one run without promising that order. Sorting makes the presentation contract independent of internal hashing layout.

```java
List<String> keys = new ArrayList<>(counts.keySet()); Collections.sort(keys);
assert keys.equals(List.of("blue", "green", "red"));
```

**Expected:** blue,green,red.

**Verify:** Compare the program values or named exception with blue,green,red. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Distinguish lookup from insertion

Task: Readmissing withgetOrDefault0 and compare map size.

A fallback value is not a stored entry. This distinction matters when zero is a legitimate observation and absence has different meaning.

```java
int before = counts.size(); int absent = counts.getOrDefault("missing", 0);
assert absent == 0 && counts.size() == before && !counts.containsKey("missing");
```

**Expected:** value0;map stillsize3.

**Verify:** Compare the program values or named exception with value0;map stillsize3. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Respect unmodifiable fixtures

Task: Try adding toList.of(1,2) and catch the specific exception.

An unmodifiable collection prevents structural mutation through that interface. Mutable elements inside such a collection still need their own ownership policy.

```java
boolean fixed = false;
try { List.of(1, 2).add(3); } catch (UnsupportedOperationException expected) { fixed = true; }
assert fixed;
```

**Expected:** UnsupportedOperationException.

**Verify:** Compare the program values or named exception with UnsupportedOperationException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
