import java.util.*;

public class Main {

  static int clamp(int value, int lower, int upper) {
    if (lower > upper) throw new IllegalArgumentException("invalid bounds");
    return Math.max(lower, Math.min(value, upper));
  }

  static int brokenClamp(int value, int lower, int upper) {
    return value < lower ? upper : Math.min(value, upper);
  }

  @FunctionalInterface
  interface Action {
    void run() throws Exception;
  }

  static void expect(Class<? extends Throwable> type, Action action) {
    try {
      action.run();
    } catch (Throwable error) {
      if (type.isInstance(error)) return;
      throw new AssertionError("wrong exception", error);
    }
    throw new AssertionError("expected " + type.getSimpleName());
  }

  static int[] reverse(int[] values) {
    int[] result = values.clone();
    for (int i = 0, j = result.length - 1; i < j; i++, j--) {
      int temporary = result[i];
      result[i] = result[j];
      result[j] = temporary;
    }
    return result;
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use independent table cases
    int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };
    for (int[] row : cases) assert clamp(row[0], 0, 5) == row[1];

    // Exercise 2: Check a boundary failure
    expect(IllegalArgumentException.class, () -> clamp(3, 5, 2));

    // Exercise 3: Test an idempotence property
    for (int value = -10; value <= 10; value++) {
      int once = clamp(value, 0, 5);
      assert clamp(once, 0, 5) == once;
    }

    // Exercise 4: Detect a broken implementation
    boolean caught = false;
    for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;
    assert caught;

    // Exercise 5: Verify the exception checker itself
    boolean checkerFailed = false;
    try {
      expect(IllegalArgumentException.class, () -> {});
    } catch (AssertionError expected) {
      checkerFailed = true;
    }
    assert checkerFailed;

    // Exercise 6: Test a fresh transfer property
    for (int[] original : List.of(new int[0], new int[] { 4 }, new int[] { 1, 2, 3 })) {
      int[] first = reverse(original);
      int[] second = reverse(first);
      assert Arrays.equals(second, original);
      if (original.length > 1) assert first[0] == original[original.length - 1];
    }
  }
}
