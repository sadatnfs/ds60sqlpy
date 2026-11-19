// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Inspect a platform module: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert
    // String.class.getPackageName().equals("java.lang");` to `assert
    // String.class.getPackageName().equals("java.lang!");` inside its assertion. Before running
    // it with `java -ea Main`, predict whether the assertion still holds and explain why; then
    // restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `String.class.getPackageName().equals("java.lang")`. Restoring the original line brings
    // back the worked observation: module `java.base`; package `java.lang`.

    // Exercise 2: Inspect the classroom classpath context: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert Main.class.getModule().isNamed();`. Run Example B with that line, explain why the
    // edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `!Main.class.getModule().isNamed()`; after it the line reads `assert
    // !Main.class.getModule().isNamed();` again and main belongs to the unnamed module in the
    // standard classpath launch.

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
