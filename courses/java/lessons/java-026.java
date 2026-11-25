// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Inspect a platform module: predict an edited check
    // Change Example A's assertion to `assert
    // String.class.getPackageName().equals("java.lang!");`, predict whether it holds, then run
    // and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `String.class.getPackageName().equals("java.lang")`.

    // Exercise 2: Inspect the classroom classpath context: diagnose an edited check
    // Example B's new assertion was edited to `assert Main.class.getModule().isNamed();`.
    // Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `!Main.class.getModule().isNamed()`; the restored assertion passes.

    // Exercise 3: Compile two real modules
    // Create the owned greeting/application fixture and compile both with --module-source-path.
    // Expected: compiler exit 0 and module-info.class files present.

    // Exercise 4: Inspect declared dependencies and exports
    // Read the compiled descriptors with ModuleFinder.
    // Expected: app requires course.greeting; library exports edu.example.greeting.

    // Exercise 5: Run the modular application
    // Launch the compiled app in a fresh child JVM with the fixed module path.
    // Expected: stdout Hello, modules! and exit 0.

    // Exercise 6: Reject a missing module dependency
    // Compile an app requiring course.missing instead of course.greeting.
    // Expected: nonzero compiler exit and captured diagnostic.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
