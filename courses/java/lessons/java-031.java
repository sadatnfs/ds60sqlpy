// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Inspect a retained annotation
        // ReadVersion on the knownFriendly provider.
        // Expected: version2.

        // Exercise 2: Invoke a known public method reflectively
        // Findgreet(String) andinvoke it withAda.
        // Expected: Hello, Ada.

        // Exercise 3: Load a real local service descriptor
        // Create the temporaryMETA-INF/services entry anddiscoverGreeting providers.
        // Expected: oneFriendly provider withversion2 andworkinggreet.

        // Exercise 4: Preserve a reflected target failure
        // Invokegreet withblanktext andinspectInvocationTargetException cause.
        // Expected: causeIllegalArgumentException.

        // Exercise 5: Reject missing class andmethod contracts
        // Look up an absent class andan unsupportedgreet(int)signature.
        // Expected: ClassNotFoundException andNoSuchMethodException.

        // Exercise 6: Treat provider metadata as a policy input
        // Accept provider versions1..2 andreject a hypotheticalversion3 under the currentconsumer
        // contract.
        // Expected: version2accepted;version3rejected.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
