// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Guard a nullable value: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert !nonempty;` to `assert
    // nonempty;` inside its assertion. Before running it with `java -ea Main`, predict whether
    // the assertion still holds and explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `!nonempty`. Restoring the original line brings back the worked observation: condition
    // false with no NullPointerException.

    // Exercise 2: Trace a prefix sum: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `sum -= values[i];`. Run Example B with that line, use the failing
    // assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; after it the line reads `sum +=
    // values[i];` again and prefix sums 2, 6, 12; final 12.

    // Exercise 3: Handle an empty loop
    // Run the same sum pattern over an empty int array.
    // Expected: sum 0 and zero iterations.

    // Exercise 4: Choose a value with a switch expression
    // Classify Saturday and Wednesday with one exhaustive switch expression over
    // java.time.DayOfWeek.
    // Expected: weekend, then weekday.

    // Exercise 5: Stop at the first match
    // Search 3, 8, 8 for the first 8 and stop immediately.
    // Expected: index 1.

    // Exercise 6: Expose a wrong boundary
    // Compare a loop using i <= length with the valid i < length contract on a one-element
    // array.
    // Expected: wrong loop raises ArrayIndexOutOfBoundsException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
