import java.util.*;

public class Main {
    static int doubleValue(int x) { return Math.multiplyExact(x, 2); }
    static int positiveArea(int width, int height) {
        if (width <= 0 || height <= 0) throw new IllegalArgumentException("positive dimensions required");
        return Math.multiplyExact(width, height);
    }
    static void reassignInt(int value) { value = 99; }
    static void append(List<Integer> values) { values.add(2); }
    static void replace(List<Integer> values) { values = new ArrayList<>(); }
    static String describe(int value) { return "int"; }
    static String describe(long value) { return "long"; }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Call a pure calculation
        assert doubleValue(7) == 14;
        assert doubleValue(0) == 0;

        // Exercise 2: Validate a precondition
        assert positiveArea(3, 4) == 12;
        boolean badArea = false;
        try { positiveArea(0, 4); } catch (IllegalArgumentException expected) { badArea = true; }
        assert badArea;

        // Exercise 3: Observe copied primitive values
        int original = 5; reassignInt(original); assert original == 5;

        // Exercise 4: Observe shared object mutation
        List<Integer> list = new ArrayList<>(List.of(1)); append(list);
        assert list.equals(List.of(1, 2));

        // Exercise 5: Distinguish reference reassignment
        replace(list); assert list.equals(List.of(1, 2));

        // Exercise 6: Inspect overload selection
        assert describe(1).equals("int");
        assert describe(1L).equals("long");
    }
}
