import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Guard a nullable value
    String text = null;
    boolean nonempty = text != null && !text.isEmpty();
    assert !nonempty;

    // Exercise 2: Trace a prefix sum
    int[] values = { 2, 4, 6 };
    int sum = 0;
    List<Integer> prefixes = new ArrayList<>();
    for (int i = 0; i < values.length; i++) {
      sum += values[i];
      prefixes.add(sum);
    }
    assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;

    // Exercise 3: Handle an empty loop
    int emptySum = 0;
    int iterations = 0;
    for (int value : new int[0]) {
      emptySum += value;
      iterations++;
    }
    assert emptySum == 0 && iterations == 0;

    // Exercise 4: Count a half-open interval
    List<Integer> visited = new ArrayList<>();
    for (int i = 0; i < 5; i++) visited.add(i);
    assert visited.equals(List.of(0, 1, 2, 3, 4));

    // Exercise 5: Stop at the first match
    int[] items = { 3, 8, 8 };
    int found = -1;
    for (int i = 0; i < items.length; i++) {
      if (items[i] == 8) {
        found = i;
        break;
      }
    }
    assert found == 1;

    // Exercise 6: Expose a wrong boundary
    boolean failed = false;
    int[] single = { 7 };
    try {
      for (int i = 0; i <= single.length; i++) {
        int ignored = single[i];
      }
    } catch (ArrayIndexOutOfBoundsException expected) {
      failed = true;
    }
    assert failed;
  }
}
