import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        // Exercise 1: Compare integer and decimal division
        int whole = 7 / 2;
        double fractional = 7 / 2.0;
        assert whole == 3 && fractional == 3.5;

        // Exercise 2: Widen before multiplication
        long safe = (long) 50_000 * 50_000;
        int wrapped = 50_000 * 50_000;
        assert safe == 2_500_000_000L;
        assert wrapped != safe;

        // Exercise 3: Detect overflow explicitly
        boolean rejected = false;
        try { Math.addExact(Integer.MAX_VALUE, 1); }
        catch (ArithmeticException expected) { rejected = true; }
        assert rejected;

        // Exercise 4: Preserve decimal source meaning
        var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));
        assert amount.equals(new java.math.BigDecimal("0.30"));

        // Exercise 5: Distinguish value from scale
        var one = new java.math.BigDecimal("1.0");
        var scaled = new java.math.BigDecimal("1.00");
        assert one.compareTo(scaled) == 0 && !one.equals(scaled);

        // Exercise 6: Reject an unsupported exact division
        boolean repeating = false;
        try { java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3")); }
        catch (ArithmeticException expected) { repeating = true; }
        assert repeating;
        assert java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33");
    }
}
