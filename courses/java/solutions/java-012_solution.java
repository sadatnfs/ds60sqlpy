import java.util.*;

public class Main {

  static double sum(List<? extends Number> values) {
    double total = 0;
    for (Number value : values) total += value.doubleValue();
    return total;
  }

  static void addTwo(List<? super Integer> values) {
    values.add(1);
    values.add(2);
  }

  static <T> void copy(List<? extends T> source, List<? super T> target) {
    target.addAll(source);
  }

  static <T> T first(List<T> values) {
    if (values.isEmpty()) throw new NoSuchElementException("empty list");
    return values.get(0);
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read from a producer
    assert sum(List.of(1, 2, 3)) == 6.0;
    assert sum(List.of(1.5, 2.5)) == 4.0;

    // Exercise 2: Write to a consumer
    List<Number> numbers = new ArrayList<>();
    addTwo(numbers);
    assert numbers.equals(List.of(1, 2));

    // Exercise 3: Connect source and destination types
    List<Number> destination = new ArrayList<>();
    copy(List.of(3, 4), destination);
    assert destination.equals(List.of(3, 4));

    // Exercise 4: Preserve generic return type
    String value = first(List.of("alpha", "beta"));
    assert value.equals("alpha");

    // Exercise 5: Handle an empty input contract
    boolean empty = false;
    try {
      first(List.of());
    } catch (NoSuchElementException expected) {
      empty = true;
    }
    assert empty;

    // Exercise 6: Observe erasure carefully
    var strings = new ArrayList<String>();
    var integers = new ArrayList<Integer>();
    assert strings.getClass().equals(integers.getClass());
    assert strings.isEmpty() && integers.isEmpty();
  }
}
