// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Inspect a platform module
    // ReadString.class module andpackage names.
    // Expected: modulejava.base;packagejava.lang.

    // Exercise 2: Inspect the classroom classpath context
    // ReadMain.class module metadata.
    // Expected: Main belongs to the unnamed module in the standardclasspath launch.

    // Exercise 3: Compile two real modules
    // Create the owned greeting/application fixture andcompile both with--module-source-path.
    // Expected: compiler exit0 andmodule-info.class files present.

    // Exercise 4: Inspect declared dependencies andexports
    // Read the compiled descriptors withModuleFinder.
    // Expected: app requirescourse.greeting;library exportsedu.example.greeting.

    // Exercise 5: Run the modular application
    // Launch the compiled app in a fresh childJVM with the fixed module path.
    // Expected: stdoutHello, modules! andexit0.

    // Exercise 6: Reject a missing module dependency
    // Compile an app requiringcourse.missing instead ofcourse.greeting.
    // Expected: nonzero compiler exit andcaptured diagnostic.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
