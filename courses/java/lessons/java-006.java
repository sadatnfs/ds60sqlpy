// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Retain sequence multiplicity: change one input
    // Copy Example A into a scratch `Main.java` and change `List<String> colors = new
    // ArrayList<>(List.of("red", "blue", "red"));` to `List<String> colors = new
    // ArrayList<>(List.of("red!", "blue", "red"));`. Before running it with `java -ea Main`,
    // predict which assertion fails and which value it now sees; then run it and restore the
    // original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `colors.size() == 4 && Collections.frequency(colors, "red") == 2`. Restoring the original
    // line brings back the worked observation: size 4; red appears twice.

    // Exercise 2: Count with a map: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `for (String color : colors) counts.merge(color, 2, Integer::sum);`. Run
    // Example B with that line, use the failing assertion to locate the defect and repair it
    // without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; after it the line reads `for
    // (String color : colors) counts.merge(color, 1, Integer::sum);` again and red 2, blue 1,
    // green 1.

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
