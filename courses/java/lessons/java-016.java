// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip explicit UTF-8
    // WriteCafé and an emoji to an owned temporary file,then read it withUTF-8.
    // Expected: exact text equality.

    // Exercise 2: Distinguish a path from existence
    // Resolve a missing child inside the temporary directory and inspect existence before
    // creating it.
    // Expected: path object exists;filesystem entry absent.

    // Exercise 3: Close a directory stream
    // Create two files and count them through atry-with-resourcesFiles.list stream.
    // Expected: count2.

    // Exercise 4: Request atomic replacement honestly
    // Write old and staged files,requestATOMIC_MOVE,then verify the selected outcome without
    // claiming a fallback is atomic.
    // Expected: either targetnew withstagedabsent,or explicit unsupported result retainingold.

    // Exercise 5: Expose a lexical path escape
    // Resolve../outside under an owned root and normalize it before checking containment.
    // Expected: normalized path is outside the root.

    // Exercise 6: Verify cleanup after failure
    // Throw inside the owned temporary scope and confirm the directory is removed by the helper.
    // Expected: original exception propagated;owned directory absent.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
