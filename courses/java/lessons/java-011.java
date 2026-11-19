// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use immutable value keys: change one input
    // Copy Example A into a scratch `Main.java` and change `Point a = new Point(0, 0),` to
    // `Point a = new Point(1, 0),`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`. Restoring
    // the original line brings back the worked observation: lookup with the other returns
    // origin; hashes equal.

    // Exercise 2: Sort with a tie-breaker: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))`.
    // Run Example B with that line, use the failing assertion to locate the defect and repair it
    // without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; after it the
    // line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))` again
    // and IDs c, a, b.

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
