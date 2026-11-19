# java-011: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equal hashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.

**Equality contract:** Rules defining when two values represent the same logical identity.

**Hash code:** A bucket-selection value consistent with equality.

**Comparator:** A rule ordering two values and identifying ties.

## Reading the reference

Records generate component-based equals and hashCode. Comparator.comparing selects a primary sort key; thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, not toString. A key should remain stable while stored. For numeric ordering use Integer.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.

## Exercise 1: Use immutable value keys: change one input

Task: Copy Example A into a scratch `Main.java` and change `Point a = new Point(0, 0),` to `Point a = new Point(1, 0),`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.

The unchanged code is the part that Example A adds:

```java
Point a = new Point(0, 0),
  b = new Point(0, 0);
Map<Point, String> map = new HashMap<>();
map.put(a, "origin");
assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`. Restoring the original line brings back the worked observation: lookup with the other returns origin; hashes equal.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Sort with a tie-breaker: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.

The unchanged code is the part that Example B adds:

```java
List<Person> people = new ArrayList<>(
  List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))
);
people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
assert people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"));
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; after it the line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))` again and IDs c, a, b.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))` for this input.

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

**Verify:** Keep an assertion equivalent to `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`. As a control, change `byAge.add(new Person("a", 20));` to `byAge.add(new Person("a", 21));`: the run must fail with an `AssertionError` from the assertion on `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `mutable.get(key) == null && mutable.size() == 1`. As a control, change `MutableKey key = new MutableKey(1);` to `MutableKey key = new MutableKey(2);`: the run must fail with an `AssertionError` from the assertion on `mutable.get(key) == null && mutable.size() == 1`. Restore the line before continuing.

## Exercise 5: Avoid comparator subtraction

Task: Compare Integer.MIN_VALUE and 1 using Integer.compare.

A comparator must preserve ordering for the whole accepted range. Arithmetic subtraction can wrap and violate that contract.

```java
assert Integer.compare(Integer.MIN_VALUE, 1) < 0;
assert Integer.MIN_VALUE - 1 > 0;
```

**Expected:** negative result; subtraction overflows positive.

**Verify:** Keep an assertion equivalent to `Integer.MIN_VALUE - 1 > 0`. As a control, change `assert Integer.MIN_VALUE - 1 > 0;` to `assert Integer.MIN_VALUE + 1 > 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `labelLeft.equals(labelRight) && !left.equals(right)`. As a control, change `String labelLeft = "point",` to `String labelLeft = "point!",`: the run must fail with an `AssertionError` from the assertion on `labelLeft.equals(labelRight) && !left.equals(right)`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
