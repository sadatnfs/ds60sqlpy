// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Establish a numerical oracle
    // Sum 1..1000 with a loop and compare with n*(n+1)/2.
    // Expected: 500500.

    // Exercise 2: Warm up without hiding results
    // Run the calculation100times and store each result in a volatile sink.
    // Expected: sink500500 after warmup.

    // Exercise 3: Measure repeated work with a checksum
    // Time20calculations and sum their outputs.
    // Expected: checksum10010000;elapsednanosecondsnonnegative.

    // Exercise 4: Record and read an actualJFR event
    // Create a bounded recording withoneCalculation event containinginput100 andoutput5050.
    // Expected: one matching event with the declared fields.

    // Exercise 5: Collect a small timing distribution
    // Measure the same bounded work five times and inspect sorted samples.
    // Expected: five nonnegative samples;minimum<=maximum;checksums preserved.

    // Exercise 6: Keep instrumented anduninstrumented claims separate
    // Record warmup,workload andprofiling state beside a measurement;refuse a universal speedup
    // claim.
    // Expected: metadata names 100 warmups and profiling false; universal claim false.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
