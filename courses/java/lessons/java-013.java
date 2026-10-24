// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a predicate
    // Create a Predicate<Integer> accepting positive values and test3,0,-1.
    // Expected: true,false,false.

    // Exercise 2: Compose transformations
    // Strip a string,then uppercase it withLocale.ROOT.
    // Expected: inputspace red space becomesRED.

    // Exercise 3: Distinguish composition order
    // Compose add1 andmultiply2 usingandThen andcompose on3.
    // Expected: andThen8;compose7.

    // Exercise 4: Capture a stable threshold
    // Capture local threshold10 in a predicate and test9,10,11.
    // Expected: false,true,true under>=.

    // Exercise 5: Expose mutable captured state
    // Capture a list in aConsumer and append two values.
    // Expected: captured list becomesa,b.

    // Exercise 6: Use a named function for a contract
    // Pass a method reference to a parser that rejects blank input and parses a positive
    // integer.
    // Expected: 7 accepted;blank rejected.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
