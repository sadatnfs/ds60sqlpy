// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read an admitted owned file: change one input
    // Change `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");` to
    // `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello!");` in Example A and
    // predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `new
    // String(readBounded(root, "input.txt", 10),
    // java.nio.charset.StandardCharsets.UTF_8).equals("hello")`.

    // Exercise 2: Reject lexical traversal and absolute paths: debug a regression
    // A regression changed `rejected = true;` to `rejected = false;` in Example B's new code.
    // Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `rejected`; the repaired line reads `rejected = true;`.

    // Exercise 3: Enforce the byte limit after reading a bounded amount
    // Write five bytes and request a four-byte maximum.
    // Expected: IOException for oversized content.

    // Exercise 4: Reject symbolic-link access under the declared policy
    // Create a link inside the owned root to another owned file and attempt to read through it.
    // Expected: link rejected when platform supports creation; unsupported capability recorded
    // explicitly.

    // Exercise 5: Keep operation names out of code execution
    // Admit only read_fixture and reject run_shell.
    // Expected: unknown operation IllegalArgumentException.

    // Exercise 6: Build a restricted diagnostic record
    // Copy only request_id, operation and status from a map containing token and source_text.
    // Expected: diagnostic excludes both sensitive fields.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
