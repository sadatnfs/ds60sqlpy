// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the compiler target
    // Compile thefixture with--release21 andinspect itsclassheader.
    // Expected: magicCAFEBABE;majorversion65.

    // Exercise 2: Inspect packaged launch metadata
    // Open thebuiltJAR andcheckMain-Class andApp.class.
    // Expected: Main-ClassApp;classentrypresent.

    // Exercise 3: Run a fresh-process self-test
    // Launch theJAR with--self-test through a bounded childJVM.
    // Expected: exit0 andoutputrelease-ok.

    // Exercise 4: Verify an invalid launch fails clearly
    // Run thesameJAR withanunsupportedargument.
    // Expected: exit2 andunknown argument diagnostic.

    // Exercise 5: Reject artifact tampering before execution
    // Hash theJAR,fliponebyte,andcalltheintegrity gate.
    // Expected: SecurityException;originalbytesrestored forcleanup.

    // Exercise 6: Record runtime-image scope androllback identity
    // Inspectwhetherjlinkexists,andwrite a record distinguishinglocalJARacceptance
    // fromanunbuiltcustomruntime.
    // Expected: previousartifactv1 retained;custom_runtime_builtFalse.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
