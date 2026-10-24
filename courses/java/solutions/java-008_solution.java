import java.util.*;

public class Main {
    record Order(String id, List<String> items) {
        Order {
            Objects.requireNonNull(id, "id"); id = id.strip();
            if (id.isEmpty()) throw new IllegalArgumentException("blank id");
            items = List.copyOf(items);
        }
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Normalize at construction
        Order order = new Order(" A ", List.of("x"));
        assert order.id().equals("A") && order.items().equals(List.of("x"));

        // Exercise 2: Copy caller-owned collections
        List<String> supplied = new ArrayList<>(List.of("x")); Order copied = new Order("B", supplied); supplied.add("y");
        assert copied.items().equals(List.of("x"));

        // Exercise 3: Use value equality
        Order same = new Order("A", List.of("x"));
        assert order.equals(same) && order.hashCode() == same.hashCode();

        // Exercise 4: Reject blank identity
        boolean blank = false;
        try { new Order("  ", List.of("x")); } catch (IllegalArgumentException expected) { blank = true; }
        assert blank;

        // Exercise 5: Protect the exposed collection
        boolean protectedItems = false;
        try { order.items().add("z"); } catch (UnsupportedOperationException expected) { protectedItems = true; }
        assert protectedItems;

        // Exercise 6: Reject null collection members
        boolean nullItem = false;
        try { new Order("C", Arrays.asList("x", null)); } catch (NullPointerException expected) { nullItem = true; }
        assert nullItem;
    }
}
