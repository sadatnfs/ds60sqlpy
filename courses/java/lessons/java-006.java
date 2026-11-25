// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Retain sequence multiplicity: change one input
    // Change `List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));` to
    // `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));` in Example A and
    // predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `colors.size() == 4 && Collections.frequency(colors, "red") == 2`.

    // Exercise 2: Count with a map: debug a regression
    // A regression in Example B's new code makes one line read `for (String color : colors)
    // counts.merge(color, 2, Integer::sum);`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; the repaired line reads `for
    // (String color : colors) counts.merge(color, 1, Integer::sum);`.

    // Exercise 3: Inspect set insertion
    // Insert red twice into a HashSet and inspect return values.
    // Expected: first true, second false, size 1.

    // Exercise 4: Create deterministic output order
    // Sort the count-map keys before presenting them.
    // Expected: blue, green, red.

    // Exercise 5: Distinguish lookup from insertion
    // Read missing with getOrDefault 0 and compare map size.
    // Expected: value 0; map still size 3.

    // Exercise 6: Respect unmodifiable fixtures
    // Try adding to List.of(1, 2) and catch the specific exception.
    // Expected: UnsupportedOperationException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
