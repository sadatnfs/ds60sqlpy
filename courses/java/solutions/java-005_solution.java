import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        // Exercise 1: Copy array storage
        int[] original = {1, 2, 3}; int[] copy = Arrays.copyOf(original, original.length); copy[0] = 9;
        assert original[0] == 1 && copy[0] == 9;

        // Exercise 2: Count text units
        String text = "A\ud83d\ude42";
        assert text.length() == 3;
        assert text.codePointCount(0, text.length()) == 2;

        // Exercise 3: Observe String immutability
        String lower = "red"; String upper = lower.toUpperCase(Locale.ROOT);
        assert lower.equals("red") && upper.equals("RED");

        // Exercise 4: Select by code-point offset
        int offset = text.offsetByCodePoints(0, 1); String emoji = text.substring(offset);
        assert emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1;

        // Exercise 5: Normalize deliberately
        String composed = "é"; String decomposed = "é";
        assert !composed.equals(decomposed);
        assert java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed);

        // Exercise 6: Reject an invalid array index
        boolean invalid = false;
        try { int ignored = original[3]; } catch (ArrayIndexOutOfBoundsException expected) { invalid = true; }
        assert invalid;
    }
}
