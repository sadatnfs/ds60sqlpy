import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Retain sequence multiplicity
    List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
    colors.add("green");
    assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;

    // Exercise 2: Count with a map
    Map<String, Integer> counts = new HashMap<>();
    for (String color : colors) counts.merge(color, 1, Integer::sum);
    assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));

    // Exercise 3: Inspect set insertion
    Set<String> unique = new HashSet<>();
    assert unique.add("red");
    assert !unique.add("red");
    assert unique.size() == 1;

    // Exercise 4: Create deterministic output order
    List<String> keys = new ArrayList<>(counts.keySet());
    Collections.sort(keys);
    assert keys.equals(List.of("blue", "green", "red"));

    // Exercise 5: Distinguish lookup from insertion
    int before = counts.size();
    int absent = counts.getOrDefault("missing", 0);
    assert absent == 0 && counts.size() == before && !counts.containsKey("missing");

    // Exercise 6: Respect unmodifiable fixtures
    boolean fixed = false;
    try {
      List.of(1, 2).add(3);
    } catch (UnsupportedOperationException expected) {
      fixed = true;
    }
    assert fixed;
  }
}
