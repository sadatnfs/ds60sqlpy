// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Copy array storage: change one input
    // Change `int[] original = { 1, 2, 3 };` to `int[] original = { 2, 2, 3 };` in Example A and
    // predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `original[0]
    // == 1 && copy[0] == 9`.

    // Exercise 2: Count text units: diagnose an edited check
    // Example B's new assertion was edited to `assert text.codePointCount(1, text.length()) ==
    // 2;`. Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `text.codePointCount(0, text.length()) == 2`; the restored assertion passes.

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
