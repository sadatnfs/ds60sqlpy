import java.util.*;

public class Main {

  static int parsePositive(String text) {
    if (text == null || text.isBlank()) throw new IllegalArgumentException(
      "positive integer text required"
    );
    int value = Integer.parseInt(text);
    if (value <= 0) throw new IllegalArgumentException("positive value required");
    return value;
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a predicate
    java.util.function.Predicate<Integer> positive = value -> value > 0;
    assert positive.test(3) && !positive.test(0) && !positive.test(-1);

    // Exercise 2: Compose transformations
    java.util.function.Function<String, String> strip = String::strip;
    java.util.function.Function<String, String> upper = value -> value.toUpperCase(Locale.ROOT);
    assert strip.andThen(upper).apply(" red ").equals("RED");

    // Exercise 3: Distinguish composition order
    java.util.function.Function<Integer, Integer> addOne = value -> value + 1;
    java.util.function.Function<Integer, Integer> twice = value -> value * 2;
    assert addOne.andThen(twice).apply(3) == 8;
    assert addOne.compose(twice).apply(3) == 7;

    // Exercise 4: Capture a stable threshold
    int threshold = 10;
    java.util.function.Predicate<Integer> enough = value -> value >= threshold;
    assert !enough.test(9) && enough.test(10) && enough.test(11);

    // Exercise 5: Expose mutable captured state
    List<String> captured = new ArrayList<>();
    java.util.function.Consumer<String> append = captured::add;
    append.accept("a");
    append.accept("b");
    assert captured.equals(List.of("a", "b"));

    // Exercise 6: Use a named function for a contract
    java.util.function.Function<String, Integer> parser = Main::parsePositive;
    assert parser.apply("7") == 7;
    boolean blank = false;
    try {
      parser.apply(" ");
    } catch (IllegalArgumentException expected) {
      blank = true;
    }
    assert blank;
  }
}
