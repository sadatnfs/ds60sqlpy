// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Inspect a retained annotation
    // Read Version on the known Friendly provider.
    // Expected: version 2.

    // Exercise 2: Invoke a known public method reflectively
    // Findgreet(String) and invoke it with Ada.
    // Expected: Hello, Ada.

    // Exercise 3: Load a real local service descriptor
    // Create the temporaryMETA-INF/services entry and discover Greeting providers.
    // Expected: oneFriendly provider with version 2 andworkinggreet.

    // Exercise 4: Preserve a reflected target failure
    // Invokegreet with blank text and inspect InvocationTargetException cause.
    // Expected: causeIllegalArgumentException.

    // Exercise 5: Reject missing class and method contracts
    // Look up an absent class and an unsupportedgreet(int)signature.
    // Expected: ClassNotFoundException and NoSuchMethodException.

    // Exercise 6: Treat provider metadata as a policy input
    // Accept provider versions1..2 and reject a hypotheticalversion3 under the current consumer
    // contract.
    // Expected: version 2 accepted;version 3 rejected.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
