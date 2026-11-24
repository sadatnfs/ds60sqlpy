// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Establish a numerical oracle: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert sum(1000) == 500_500L &&
    // sum(1000) == (1000L * 1001) / 2;` to `assert sum(1001) == 500_500L && sum(1000) == (1000L
    // * 1001) / 2;` inside its assertion. Before running it with `java -ea Main`, predict
    // whether the assertion still holds and explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `sum(1000)
    // == 500_500L && sum(1000) == (1000L * 1001) / 2`. Restoring the original line brings back
    // the worked observation: 500500.

    // Exercise 2: Warm up without hiding results: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `for (int i = 0; i < 100; i++) sink = sum(1001);`. Run Example B with that
    // line, use the failing assertion to locate the defect and repair it without changing the
    // assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `sink == 500_500L`; after it the line reads `for (int i = 0; i < 100; i++) sink =
    // sum(1000);` again and sink 500500 after warmup.

    // Exercise 3: Measure repeated work with a checksum
    // Time 20 calculations and sum their outputs.
    // Expected: checksum 10010000; elapsed nanoseconds nonnegative.

    // Exercise 4: Record and read an actual JFR event
    // Create a bounded recording with one Calculation event containing input 100 and output 5050.
    // Expected: one matching event with the declared fields.

    // Exercise 5: Collect a small timing distribution
    // Measure the same bounded work five times and inspect sorted samples.
    // Expected: five nonnegative samples; minimum<=maximum; checksums preserved.

    // Exercise 6: Keep instrumented and uninstrumented claims separate
    // Record warmup, workload and profiling state beside a measurement; refuse a universal
    // speedup claim.
    // Expected: metadata names 100 warmups and profiling false; universal claim false.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
