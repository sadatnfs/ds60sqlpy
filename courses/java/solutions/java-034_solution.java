import java.util.*;

public class Main {
    interface Catalog {java.util.OptionalLong unitPrice(String id) throws java.io.IOException;}
    record Quote(String item,int quantity,long totalCents,java.time.Instant created){}
    static long total(int quantity,long unitPrice){if(quantity<=0||unitPrice<0)throw new IllegalArgumentException("positive quantity and nonnegative price required");return Math.multiplyExact((long)quantity,unitPrice);}
    record Service(Catalog catalog,java.util.function.Supplier<java.time.Instant> clock,java.util.function.Consumer<String> audit){
        Service{Objects.requireNonNull(catalog);Objects.requireNonNull(clock);Objects.requireNonNull(audit);}
        Quote quote(String id,int quantity) throws java.io.IOException {if(id==null||id.isBlank()||quantity<=0)throw new IllegalArgumentException("valid item and quantity required");long price=catalog.unitPrice(id).orElseThrow(() -> new NoSuchElementException("unknown item"));long amount=total(quantity,price);Quote result=new Quote(id,quantity,amount,clock.get());audit.accept("quoted:"+id);return result;}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Test the pure calculation
        assert total(3,125)==375;boolean invalid=false;try{total(0,125);}catch(IllegalArgumentException expected){invalid=true;}assert invalid;

        // Exercise 2: Compose a deterministic service
        List<String> audit=new ArrayList<>();var instant=java.time.Instant.parse("2026-01-01T00:00:00Z");
        Catalog catalog=id -> id.equals("item-a")?java.util.OptionalLong.of(125):java.util.OptionalLong.empty();
        Service service=new Service(catalog,() -> instant,audit::add);Quote quote=service.quote("item-a",2);
        assert quote.totalCents()==250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"));

        // Exercise 3: Reject an unknown catalog item
        boolean missing=false;try{service.quote("missing",2);}catch(NoSuchElementException expected){missing=true;}
        assert missing && audit.size()==1;

        // Exercise 4: Propagate an infrastructure failure
        List<String> failures=new ArrayList<>();Service unavailable=new Service(id -> {throw new java.io.IOException("catalog unavailable");},() -> instant,failures::add);boolean propagated=false;
        try{unavailable.quote("item-a",1);}catch(java.io.IOException expected){propagated=expected.getMessage().equals("catalog unavailable");}
        assert propagated && failures.isEmpty();

        // Exercise 5: Prove invalid quantity fails before a repository call
        var calls=new java.util.concurrent.atomic.AtomicInteger();Service checked=new Service(id -> {calls.incrementAndGet();return java.util.OptionalLong.of(1);},() -> instant,value -> {});boolean rejected=false;
        try{checked.quote("item-a",-1);}catch(IllegalArgumentException expected){rejected=true;}
        assert rejected && calls.get()==0;

        // Exercise 6: Detect arithmetic overflow without an event
        List<String> overflowAudit=new ArrayList<>();Service expensive=new Service(id -> java.util.OptionalLong.of(Long.MAX_VALUE),() -> instant,overflowAudit::add);boolean overflow=false;
        try{expensive.quote("x",2);}catch(ArithmeticException expected){overflow=true;}
        assert overflow && overflowAudit.isEmpty();
    }
}
