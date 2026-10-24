import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        // Exercise 1: Retrieve a bounded result
        try(var executor=java.util.concurrent.Executors.newFixedThreadPool(2)) {
            var future=executor.submit(() -> 42);
            assert future.get(2,java.util.concurrent.TimeUnit.SECONDS)==42;
        }

        // Exercise 2: Preserve task failure identity
        try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
            var failed=executor.submit(() -> {throw new IllegalArgumentException("bad fixture");});boolean observed=false;
            try{failed.get(2,java.util.concurrent.TimeUnit.SECONDS);}catch(java.util.concurrent.ExecutionException expected){observed=expected.getCause() instanceof IllegalArgumentException;}
            assert observed;
        }

        // Exercise 3: Separate wait timeout from task completion
        var gate=new java.util.concurrent.CountDownLatch(1);
        try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
            var future=executor.submit(() -> {gate.await();return 7;});boolean timedOut=false;
            try{future.get(20,java.util.concurrent.TimeUnit.MILLISECONDS);}catch(java.util.concurrent.TimeoutException expected){timedOut=true;}finally{gate.countDown();}
            assert timedOut && future.get(2,java.util.concurrent.TimeUnit.SECONDS)==7;
        }

        // Exercise 4: Cancel cooperatively
        var started=new java.util.concurrent.CountDownLatch(1);var exited=new java.util.concurrent.CountDownLatch(1);
        try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
            var future=executor.submit(() -> {started.countDown();try{new java.util.concurrent.CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{exited.countDown();}});
            assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);assert future.cancel(true);
            assert exited.await(2,java.util.concurrent.TimeUnit.SECONDS) && future.isCancelled();
        }

        // Exercise 5: Reject work after shutdown
        var closed=java.util.concurrent.Executors.newSingleThreadExecutor();closed.shutdown();boolean rejected=false;
        try{closed.submit(() -> 1);}catch(java.util.concurrent.RejectedExecutionException expected){rejected=true;}
        assert rejected && closed.awaitTermination(2,java.util.concurrent.TimeUnit.SECONDS);

        // Exercise 6: Enforce a bounded queue
        var hold=new java.util.concurrent.CountDownLatch(1);var running=new java.util.concurrent.CountDownLatch(1);
        try(var bounded=new java.util.concurrent.ThreadPoolExecutor(1,1,0,java.util.concurrent.TimeUnit.SECONDS,new java.util.concurrent.ArrayBlockingQueue<Runnable>(1),new java.util.concurrent.ThreadPoolExecutor.AbortPolicy())) {
            var first=bounded.submit(() -> {running.countDown();hold.await();return 1;});assert running.await(2,java.util.concurrent.TimeUnit.SECONDS);
            var second=bounded.submit(() -> 2);boolean overloaded=false;
            try{bounded.submit(() -> 3);}catch(java.util.concurrent.RejectedExecutionException expected){overloaded=true;}finally{hold.countDown();}
            assert overloaded && first.get(2,java.util.concurrent.TimeUnit.SECONDS)==1 && second.get(2,java.util.concurrent.TimeUnit.SECONDS)==2;
        }
    }
}
