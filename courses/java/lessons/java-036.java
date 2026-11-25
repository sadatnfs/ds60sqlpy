// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the compiler target: predict an edited check
    // Change Example A's assertion to `assert magic == 0xCAFEBABE && major == 66;`, predict
    // whether it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `magic ==
    // 0xCAFEBABE && major == 65`.

    // Exercise 2: Inspect packaged launch metadata: diagnose an edited check
    // Example B's new assertion was edited to `assert
    // jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App!") &&`. Explain
    // why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&
    // jar.getJarEntry("App.class") != null`; the restored assertion passes.

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
