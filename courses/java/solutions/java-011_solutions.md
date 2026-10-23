# java-011: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equalhashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.

**Equality contract:** Rules defining when two values represent the same logical identity.

**Hash code:** A bucket-selection value consistent with equality.

**Comparator:** A rule ordering two values and identifying ties.

## Reading the reference

Records generate component-basedequals andhashCode. Comparator.comparing selects a primary sort key;thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, nottoString. A key should remain stable while stored. For numeric ordering useInteger.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.

## Exercise 1: Use immutable value keys

Task: Create two equalPoint records and insert one into a map.

The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.

```java
Point a=new Point(0,0), b=new Point(0,0); Map<Point,String> map=new HashMap<>(); map.put(a,"origin");
assert a.equals(b) && a.hashCode()==b.hashCode() && map.get(b).equals("origin");
```

**Expected:** lookup with the other returnsorigin;hashes equal.

**Verify:** Compare the program values or named exception with lookup with the other returnsorigin;hashes equal. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Sort with a tie-breaker

Task: Sort people(age20,idb),(age20,ida),(age18,idc) byage thenid.

The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.

```java
List<Person> people=new ArrayList<>(List.of(new Person("b",20),new Person("a",20),new Person("c",18)));
people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
assert people.stream().map(Person::id).toList().equals(List.of("c","a","b"));
```

**Expected:** IDs c,a,b.

**Verify:** Compare the program values or named exception with IDs c,a,b. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Expose comparator uniqueness

Task: Insert two different people ofage20 into aTreeSet comparingage only.

TreeSet treats comparator result0 as equivalent for its membership rule. The comparator must reflect the uniqueness contract the caller actually wants.

```java
Set<Person> byAge=new TreeSet<>(Comparator.comparingInt(Person::age)); byAge.add(new Person("a",20)); byAge.add(new Person("b",20));
assert byAge.size()==1 && !new Person("a",20).equals(new Person("b",20));
```

**Expected:** setsize1 despite unequal records.

**Verify:** Compare the program values or named exception with setsize1 despite unequal records. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Demonstrate mutable-key failure

Task: Insert a key withhash1,mutate its hash field to2,and attempt lookup with the same object.

The entry remains in a bucket selected by the original hash. Mutation does not notifyHashMap to relocate it, so stable key state is essential.

```java
MutableKey key=new MutableKey(1); Map<MutableKey,String> mutable=new HashMap<>(); mutable.put(key,"value"); key.value=2;
assert mutable.get(key)==null && mutable.size()==1;
```

**Expected:** lookup fails in this fixture while mapsize remains1.

**Verify:** Compare the program values or named exception with lookup fails in this fixture while mapsize remains1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Avoid comparator subtraction

Task: CompareInteger.MIN_VALUE and1 usingInteger.compare.

A comparator must preserve ordering for the whole accepted range. Arithmetic subtraction can wrap and violate that contract.

```java
assert Integer.compare(Integer.MIN_VALUE,1)<0;
assert Integer.MIN_VALUE-1>0;
```

**Expected:** negative result;subtraction overflows positive.

**Verify:** Compare the program values or named exception with negative result;subtraction overflows positive. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Keep identity and display separate

Task: Give twoPoints the same formatted label but different coordinates;compare values.

A human-friendly label is not automatically a unique identifier. Using display text as a map key can merge distinct domain values.

```java
Point left=new Point(1,2), right=new Point(2,1); String labelLeft="point",labelRight="point";
assert labelLeft.equals(labelRight) && !left.equals(right);
```

**Expected:** display labels equal;points unequal.

**Verify:** Compare the program values or named exception with display labels equal;points unequal. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
