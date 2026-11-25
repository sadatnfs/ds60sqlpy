// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip explicit UTF-8: change one input
    // Rebuild Example A from memory and propose one input change that makes the assertion on
    // `java.nio.file.Files.readString(path,
    // java.nio.charset.StandardCharsets.UTF_8).equals(text)` fail.
    // Expected: The rebuild passes and the changed copy fails as predicted.

    // Exercise 2: Distinguish a path from existence: debug a regression
    // A regression in Example B's new code makes one line read `var missing =
    // root.resolve("missing.txt!");`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `missing.getFileName().toString().equals("missing.txt") &&
    // !java.nio.file.Files.exists(missing)`; the repaired line reads `var missing =
    // root.resolve("missing.txt");`.

    // Exercise 3: Close a directory stream
    // Create two files and count them through a try-with-resources Files.list stream.
    // Expected: count 2.

    // Exercise 4: Request atomic replacement honestly
    // Write old and staged files, request ATOMIC_MOVE, then verify the selected outcome without
    // claiming a fallback is atomic.
    // Expected: either target new with staged absent, or explicit unsupported result retaining
    // old.

    // Exercise 5: Expose a lexical path escape
    // Resolve../outside under an owned root and normalize it before checking containment.
    // Expected: normalized path is outside the root.

    // Exercise 6: Verify cleanup after failure
    // Throw inside the owned temporary scope and confirm the directory is removed by the helper.
    // Expected: original exception propagated; owned directory absent.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
