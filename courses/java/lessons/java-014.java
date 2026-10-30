// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Filter and sum
    // Keep even values from 1,2,3,4 and sum their squares.
    // Expected: 20.

    // Exercise 2: Observe laziness with an explicit terminal
    // Create a mapped stream that increments a counter,then consumetoList.
    // Expected: counter0 before terminal and3 after.

    // Exercise 3: Group with a collector
    // Count red,blue,red withgroupingBy and counting.
    // Expected: red2L,blue1L.

    // Exercise 4: Reject stream reuse
    // Consume a stream once,then attempt another terminal operation.
    // Expected: IllegalStateException.

    // Exercise 5: Check the reduction identity
    // Compare sum reduction with identity0 against a deliberately wrong identity10.
    // Expected: correct6;wrong16 in the sequential fixture.

    // Exercise 6: Expose nonassociative subtraction
    // Compare(10-3)-2 with10-(3-2),then use an associative sum for a parallel fixture.
    // Expected: 5 versus 9; parallel sum 5050.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
