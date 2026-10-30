// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the compiler target
    // Compile the fixture with --release 21 and inspect its class header.
    // Expected: magic CAFEBABE; major version 65.

    // Exercise 2: Inspect packaged launch metadata
    // Open thebuiltJAR andcheckMain-Class andApp.class.
    // Expected: Main-ClassApp;class entry present.

    // Exercise 3: Run a fresh-process self-test
    // Launch the JAR with--self-test through a bounded childJVM.
    // Expected: exit 0 andoutputrelease-ok.

    // Exercise 4: Verify an invalid launch fails clearly
    // Run thesameJAR with an unsupported argument.
    // Expected: exit2 and unknown argument diagnostic.

    // Exercise 5: Reject artifact tampering before execution
    // Hash the JAR,fliponebyte,and call the integrity gate.
    // Expected: SecurityException;original bytes restored for cleanup.

    // Exercise 6: Record runtime-image scope and rollback identity
    // Inspect whether jlink exists,and write a record distinguishing local JAR acceptance
    // fromanunbuiltcustomruntime.
    // Expected: previous artifact v1 retained; custom_runtime_built False.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
