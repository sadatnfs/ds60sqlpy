import java.util.*;

public class Main {
    static volatile long sink;
    static long sum(int n){if(n<0||n>100000)throw new IllegalArgumentException("bounded nonnegative n required");long result=0;for(int i=1;i<=n;i++)result+=i;return result;}
    @jdk.jfr.Name("course.Calculation") @jdk.jfr.Label("Course calculation")
    static class Calculation extends jdk.jfr.Event {long input;long output;}
    public static void main(String[] args) throws Exception {
        // Exercise 1: Establish a numerical oracle
        assert sum(1000)==500_500L && sum(1000)==1000L*1001/2;

        // Exercise 2: Warm up without hiding results
        for(int i=0;i<100;i++)sink=sum(1000);assert sink==500_500L;

        // Exercise 3: Measure repeated work with a checksum
        long start=System.nanoTime(),checksum=0;for(int i=0;i<20;i++)checksum+=sum(1000);long elapsed=System.nanoTime()-start;
        assert checksum==10_010_000L && elapsed>=0;

        // Exercise 4: Record andread an actualJFR event
        var root=java.nio.file.Files.createTempDirectory("ds60-jfr-");var file=root.resolve("fixture.jfr");
        try {
            assert jdk.jfr.FlightRecorder.isAvailable();
            try(var recording=new jdk.jfr.Recording()) {
                recording.enable("course.Calculation").withoutThreshold();recording.start();var event=new Calculation();event.input=100;event.begin();event.output=sum(100);event.end();event.commit();recording.stop();recording.dump(file);
            }
            var events=jdk.jfr.consumer.RecordingFile.readAllEvents(file).stream().filter(event -> event.getEventType().getName().equals("course.Calculation")).toList();
            assert events.size()==1 && events.get(0).getLong("input")==100 && events.get(0).getLong("output")==5050;
        } finally {java.nio.file.Files.deleteIfExists(file);java.nio.file.Files.deleteIfExists(root);}

        // Exercise 5: Collect a small timing distribution
        long[] samples=new long[5];for(int run=0;run<samples.length;run++){long begin=System.nanoTime();sink=sum(1000);samples[run]=System.nanoTime()-begin;assert sink==500_500L;}
        Arrays.sort(samples);assert samples.length==5 && samples[0]>=0 && samples[0]<=samples[4];

        // Exercise 6: Keep instrumented anduninstrumented claims separate
        Map<String,Object> receipt=Map.of("warmup_iterations",100,"n",1000,"measured_iterations",20,"profiling_during_timing",false,"universal_speedup_claim",false);
        assert receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false);
    }
}
