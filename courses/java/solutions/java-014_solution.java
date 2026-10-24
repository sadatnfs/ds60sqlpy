import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Filter and sum
    int total = List.of(1, 2, 3, 4)
      .stream()
      .filter(value -> value % 2 == 0)
      .mapToInt(value -> value * value)
      .sum();
    assert total == 20;

    // Exercise 2: Observe laziness with an explicit terminal
    var calls = new java.util.concurrent.atomic.AtomicInteger();
    var pipeline = List.of(1, 2, 3)
      .stream()
      .map(value -> {
        calls.incrementAndGet();
        return value * 2;
      });
    assert calls.get() == 0;
    assert pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3;

    // Exercise 3: Group with a collector
    Map<String, Long> counts = List.of("red", "blue", "red")
      .stream()
      .collect(
        java.util.stream.Collectors.groupingBy(
          value -> value,
          java.util.stream.Collectors.counting()
        )
      );
    assert counts.equals(Map.of("red", 2L, "blue", 1L));

    // Exercise 4: Reject stream reuse
    var once = List.of(1, 2).stream();
    assert once.count() == 2;
    boolean reused = false;
    try {
      once.toList();
    } catch (IllegalStateException expected) {
      reused = true;
    }
    assert reused;

    // Exercise 5: Check the reduction identity
    int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);
    int wrong = List.of(1, 2, 3).stream().reduce(10, Integer::sum);
    assert correct == 6 && wrong == 16;

    // Exercise 6: Expose nonassociative subtraction
    assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;
    assert java.util.stream.IntStream.rangeClosed(1, 100).parallel().sum() == 5050;
  }
}
