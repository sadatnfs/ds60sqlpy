import java.util.*;

public class Main {

  record Point(int x, int y) {}

  record Person(String id, int age) {}

  static final class MutableKey {

    int value;

    MutableKey(int value) {
      this.value = value;
    }

    public int hashCode() {
      return value;
    }

    public boolean equals(Object other) {
      return other instanceof MutableKey key && key.value == value;
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use immutable value keys
    Point a = new Point(0, 0),
      b = new Point(0, 0);
    Map<Point, String> map = new HashMap<>();
    map.put(a, "origin");
    assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");

    // Exercise 2: Sort with a tie-breaker
    List<Person> people = new ArrayList<>(
      List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))
    );
    people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
    assert people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"));

    // Exercise 3: Expose comparator uniqueness
    Set<Person> byAge = new TreeSet<>(Comparator.comparingInt(Person::age));
    byAge.add(new Person("a", 20));
    byAge.add(new Person("b", 20));
    assert byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20));

    // Exercise 4: Demonstrate mutable-key failure
    MutableKey key = new MutableKey(1);
    Map<MutableKey, String> mutable = new HashMap<>();
    mutable.put(key, "value");
    key.value = 2;
    assert mutable.get(key) == null && mutable.size() == 1;

    // Exercise 5: Avoid comparator subtraction
    assert Integer.compare(Integer.MIN_VALUE, 1) < 0;
    assert Integer.MIN_VALUE - 1 > 0;

    // Exercise 6: Keep identity and display separate
    Point left = new Point(1, 2),
      right = new Point(2, 1);
    String labelLeft = "point",
      labelRight = "point";
    assert labelLeft.equals(labelRight) && !left.equals(right);
  }
}
