// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Establish a numerical oracle
        // Sum1..1000 with a loop andcompare withn*(n+1)/2.
        // Expected: 500500.

        // Exercise 2: Warm up without hiding results
        // Run the calculation100times andstore eachresult in a volatile sink.
        // Expected: sink500500 afterwarmup.

        // Exercise 3: Measure repeated work with a checksum
        // Time20calculations andsum their outputs.
        // Expected: checksum10010000;elapsednanosecondsnonnegative.

        // Exercise 4: Record andread an actualJFR event
        // Create a bounded recording withoneCalculation event containinginput100 andoutput5050.
        // Expected: one matching event withthedeclared fields.

        // Exercise 5: Collect a small timing distribution
        // Measure the same boundedworkfive times andinspect sorted samples.
        // Expected: five nonnegative samples;minimum<=maximum;checksums preserved.

        // Exercise 6: Keep instrumented anduninstrumented claims separate
        // Record warmup,workload andprofiling state beside a measurement;refuse a universal speedup
        // claim.
        // Expected: metadata names100warmups andprofilingfalse;universal claimfalse.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
