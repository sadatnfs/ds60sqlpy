import java.util.*;

public class Main {
    static Optional<Integer> lookup(Map<String,Integer> data,String id){if(id==null||id.isBlank())throw new IllegalArgumentException("nonblank id required");return Optional.ofNullable(data.get(id));}
    static Optional<Integer> tryParse(String text){try{return Optional.of(Integer.parseInt(text));}catch(NumberFormatException error){return Optional.empty();}}
    public static void main(String[] args) throws Exception {
        // Exercise 1: Represent a missing lookup
        Map<String,Integer> data=Map.of("a",7);
        Optional<Integer> known=Optional.ofNullable(data.get("a")); Optional<Integer> missing=Optional.ofNullable(data.get("b"));
        assert known.orElseThrow()==7 && missing.isEmpty();

        // Exercise 2: Transform only present values
        assert known.map(value -> value*2).orElseThrow()==14;
        assert missing.map(value -> value*2).isEmpty();

        // Exercise 3: Compare eager and lazy fallback
        var calls=new java.util.concurrent.atomic.AtomicInteger();
        assert known.orElse(calls.incrementAndGet())==7 && calls.get()==1;
        assert known.orElseGet(calls::incrementAndGet)==7 && calls.get()==1;

        // Exercise 4: Reject malformed lookup input
        boolean invalid=false;
        try { lookup(data," "); } catch(IllegalArgumentException expected){invalid=true;}
        assert invalid && lookup(data,"b").isEmpty();

        // Exercise 5: Flatten a nullable transformation
        assert Optional.of("12").flatMap(Main::tryParse).orElseThrow()==12;
        assert Optional.of("bad").flatMap(Main::tryParse).isEmpty();

        // Exercise 6: Expose unsafeget
        boolean absent=false;
        try { Optional.empty().get(); } catch(NoSuchElementException expected){absent=true;}
        assert absent;
    }
}
