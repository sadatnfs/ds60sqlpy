// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Compile a literal application: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert
    // java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));` to `assert
    // java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));` inside its
    // assertion. Before running it with `java -ea Main`, predict whether the assertion still
    // holds and explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`. Restoring the
    // original line brings back the worked observation: compiler exit 0; Hello.class exists.

    // Exercise 2: Create a runnable archive: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert archive.getManifest().getMainAttributes().getValue("Main-
    // Class").equals("Hello!");`. Run Example B with that line, explain why the edited assertion
    // now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; after
    // it the line reads `assert archive.getManifest().getMainAttributes().getValue("Main-
    // Class").equals("Hello");` again and JAR exists and contains Hello.class.

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
