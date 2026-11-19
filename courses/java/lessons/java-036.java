// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the compiler target: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert magic == 0xCAFEBABE && major
    // == 65;` to `assert magic == 0xCAFEBABE && major == 66;` inside its assertion. Before
    // running it with `java -ea Main`, predict whether the assertion still holds and explain
    // why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `magic ==
    // 0xCAFEBABE && major == 65`. Restoring the original line brings back the worked
    // observation: magic CAFEBABE; major version 65.

    // Exercise 2: Inspect packaged launch metadata: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App!") &&`.
    // Run Example B with that line, explain why the edited assertion now fails for the same
    // program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&
    // jar.getJarEntry("App.class") != null`; after it the line reads `assert
    // jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&` again and
    // main-Class App; class entry present.

    // Exercise 3: Run a fresh-process self-test
    // Launch the JAR with --self-test through a bounded child JVM.
    // Expected: exit 0 and output release-ok.

    // Exercise 4: Verify an invalid launch fails clearly
    // Run the same JAR with an unsupported argument.
    // Expected: exit 2 and unknown argument diagnostic.

    // Exercise 5: Reject artifact tampering before execution
    // Hash the JAR, flip one byte, and call the integrity gate.
    // Expected: SecurityException; original bytes restored for cleanup.

    // Exercise 6: Record runtime-image scope and rollback identity
    // Inspect whether jlink exists, and write a record distinguishing local JAR acceptance from
    // an unbuilt custom runtime.
    // Expected: previous artifact v1 retained; custom_runtime_built False.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
