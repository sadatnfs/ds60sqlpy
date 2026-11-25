// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use immutable value keys: change one input
    // Change `Point a = new Point(0, 0),` to `Point a = new Point(1, 0),` in Example A and
    // predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `a.equals(b)
    // && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`.

    // Exercise 2: Sort with a tie-breaker: debug a regression
    // A regression in Example B's new code makes one line read `List.of(new Person("b", 20), new
    // Person("a", 21), new Person("c", 18))`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; the repaired
    // line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))`.

    // Exercise 3: Expose comparator uniqueness
    // Insert two different people of age 20 into a TreeSet comparing age only.
    // Expected: set size 1 despite unequal records.

    // Exercise 4: Demonstrate mutable-key failure
    // Insert a key with hash 1, mutate its hash field to 2, and attempt lookup with the same
    // object.
    // Expected: lookup fails in this fixture while map size remains 1.

    // Exercise 5: Avoid comparator subtraction
    // Compare Integer.MIN_VALUE and 1 using Integer.compare.
    // Expected: negative result; subtraction overflows positive.

    // Exercise 6: Keep identity and display separate
    // Give two Points the same formatted label but different coordinates; compare values.
    // Expected: display labels equal; points unequal.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
