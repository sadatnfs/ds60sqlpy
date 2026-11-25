# java-011: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equal hashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.

**Equality contract:** Rules defining when two values represent the same logical identity.

**Hash code:** A bucket-selection value consistent with equality.

**Comparator:** A rule ordering two values and identifying ties.

## Reading the reference

Records generate component-based equals and hashCode. Comparator.comparing selects a primary sort key; thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, not toString. A key should remain stable while stored. For numeric ordering use Integer.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.

## Exercise 1: Use immutable value keys: change one input

Task: Change `Point a = new Point(0, 0),` to `Point a = new Point(1, 0),` in Example A and predict which assertion fails and why.

The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.

The unchanged code is the part that Example A adds:

```java
Point a = new Point(0, 0),
  b = new Point(0, 0);
Map<Point, String> map = new HashMap<>();
map.put(a, "origin");
assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`.

**Verify:** Name the value that makes `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")` false, then restore the line.

## Exercise 2: Sort with a tie-breaker: debug a regression

Task: A regression in Example B's new code makes one line read `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))`. Repair it using the failing assertion.

The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.

The unchanged code is the part that Example B adds:

```java
List<Person> people = new ArrayList<>(
  List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))
);
people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
assert people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"));
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; the repaired line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))`.

**Verify:** Explain how the changed token alters the value that `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))` tests.

## Exercise 3: Expose comparator uniqueness

Task: Insert two different people of age 20 into a TreeSet comparing age only.

TreeSet treats comparator result 0 as equivalent for its membership rule. The comparator must reflect the uniqueness contract the caller actually wants.

```java
Set<Person> byAge = new TreeSet<>(Comparator.comparingInt(Person::age));
byAge.add(new Person("a", 20));
byAge.add(new Person("b", 20));
assert byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20));
```

**Expected:** set size 1 despite unequal records.

**Verify:** Control: changing `byAge.add(new Person("a", 20));` to `byAge.add(new Person("a", 21));` must fail the assertion on `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`.

## Exercise 4: Demonstrate mutable-key failure

Task: Insert a key with hash 1, mutate its hash field to 2, and attempt lookup with the same object.

The entry remains in a bucket selected by the original hash. Mutation does not notifyHashMap to relocate it, so stable key state is essential.

```java
MutableKey key = new MutableKey(1);
Map<MutableKey, String> mutable = new HashMap<>();
mutable.put(key, "value");
key.value = 2;
assert mutable.get(key) == null && mutable.size() == 1;
```

**Expected:** lookup fails in this fixture while map size remains 1.

**Verify:** Control: changing `MutableKey key = new MutableKey(1);` to `MutableKey key = new MutableKey(2);` must fail the assertion on `mutable.get(key) == null && mutable.size() == 1`.

## Exercise 5: Avoid comparator subtraction

Task: Compare Integer.MIN_VALUE and 1 using Integer.compare.

A comparator must preserve ordering for the whole accepted range. Arithmetic subtraction can wrap and violate that contract.

```java
assert Integer.compare(Integer.MIN_VALUE, 1) < 0;
assert Integer.MIN_VALUE - 1 > 0;
```

**Expected:** negative result; subtraction overflows positive.

**Verify:** Control: changing `assert Integer.MIN_VALUE - 1 > 0;` to `assert Integer.MIN_VALUE + 1 > 0;` inside the assertion must make it fail.

## Exercise 6: Keep identity and display separate

Task: Give two Points the same formatted label but different coordinates; compare values.

A human-friendly label is not automatically a unique identifier. Using display text as a map key can merge distinct domain values.

```java
Point left = new Point(1, 2),
  right = new Point(2, 1);
String labelLeft = "point",
  labelRight = "point";
assert labelLeft.equals(labelRight) && !left.equals(right);
```

**Expected:** display labels equal; points unequal.

**Verify:** Control: changing `String labelLeft = "point",` to `String labelLeft = "point!",` must fail the assertion on `labelLeft.equals(labelRight) && !left.equals(right)`.

## After comparing the answer

Change the `TreeSet` comparator in your copy to compare age and then ID, and confirm that both 20-year-olds are kept while the set stays sorted by age.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
