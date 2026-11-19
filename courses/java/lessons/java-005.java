// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Copy array storage: change one input
    // Copy Example A into a scratch `Main.java` and change `int[] original = { 1, 2, 3 };` to
    // `int[] original = { 2, 2, 3 };`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `original[0] == 1 && copy[0] == 9`. Restoring the original line brings back the worked
    // observation: original starts 1; copy starts 9.

    // Exercise 2: Count text units: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert text.codePointCount(1, text.length()) == 2;`. Run Example B with that line,
    // explain why the edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `text.codePointCount(0, text.length()) == 2`; after it the line reads `assert
    // text.codePointCount(0, text.length()) == 2;` again and length 3 code units; 2 code points.

    // Exercise 3: Observe String immutability
    // Convert lowercase red to uppercase and retain both references.
    // Expected: original red; new RED.

    // Exercise 4: Select by code-point offset
    // Find the UTF-16 offset of the second code point and take the remaining substring.
    // Expected: substring is the intact emoji with length 2.

    // Exercise 5: Normalize deliberately
    // Compare composedé ande plus combining acute before and after NFC.
    // Expected: raw strings differ; normalized strings equal.

    // Exercise 6: Reject an invalid array index
    // Read index 3 from a length 3 array and catch the boundary failure.
    // Expected: ArrayIndexOutOfBoundsException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
