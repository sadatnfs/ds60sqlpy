// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Compile a literal application
        // Build a Hello class whose main printsbuild-ok.
        // Expected: compiler exit0;Hello.class exists.

        // Exercise 2: Create a runnable archive
        // Package the compiled classes withmain-classHello andfixedtimestamp.
        // Expected: JAR exists andcontainsHello.class.

        // Exercise 3: Compare two builds with fixed metadata
        // Package the same classes twice withthe same timestamp.
        // Expected: archive byte hashes equal in this preparedJDK.

        // Exercise 4: Execute the packaged entrypoint
        // Run theJAR in a bounded childJVM.
        // Expected: stdoutbuild-ok;exit0.

        // Exercise 5: Detect a changed source identity
        // Hash two source strings differing in their printedmessage.
        // Expected: differentSHA256digests.

        // Exercise 6: Record an explicit dependency contract
        // Represent H2 asversion2.5.252 witha requiredverifiedhash field andreject a movingLATEST
        // label.
        // Expected: exactversionaccepted;LATESTnot treated as a pin.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
