// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read from a producer
    // Sum `List.of(1, 2, 3)` and `List.of(1.5, 2.5)` through List<?extends Number>.
    // Expected: sums 6.0 and 4.0.

    // Exercise 2: Write to a consumer
    // Append integers1,2 to a List<Number> through List<?superInteger>.
    // Expected: listcontains1,2.

    // Exercise 3: Connect source and destination types
    // CopyList<Integer> intoList<Number> with a bounded generic method.
    // Expected: destinationcontains3,4.

    // Exercise 4: Preserve generic return type
    // Callfirst on a String list and assign directly toString.
    // Expected: result alpha.

    // Exercise 5: Handle an empty input contract
    // Callfirst on an empty list and require a named failure.
    // Expected: NoSuchElementException.

    // Exercise 6: Observe erasure carefully
    // Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does
    // not permit unsafe assignments.
    // Expected: runtime classes equal; compile-time contracts remain distinct.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
