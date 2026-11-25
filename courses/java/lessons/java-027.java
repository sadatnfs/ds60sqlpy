// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Compile a literal application: predict an edited check
    // Change Example A's assertion to `assert
    // java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));`, predict
    // whether it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`.

    // Exercise 2: Create a runnable archive: diagnose an edited check
    // Example B's new assertion was edited to `assert
    // archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");`.
    // Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; the
    // restored assertion passes.

    // Exercise 3: Compare two builds with fixed metadata
    // Package the same classes twice with the same timestamp.
    // Expected: archive byte hashes equal in this prepared JDK.

    // Exercise 4: Execute the packaged entrypoint
    // Run the JAR in a bounded child JVM.
    // Expected: stdout build-ok; exit 0.

    // Exercise 5: Detect a changed source identity
    // Hash two source strings differing in their printed message.
    // Expected: different SHA-256 digests.

    // Exercise 6: Record an explicit dependency contract
    // Represent H2 as version 2.5.252 with a required verified hash field and reject a moving
    // LATEST label.
    // Expected: exact version accepted; LATEST not treated as a pin.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
