import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        // Exercise 1: Observe virtual identity
        var virtual=new java.util.concurrent.atomic.AtomicBoolean();Thread task=Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));task.join(2000);
        assert !task.isAlive() && virtual.get();

        // Exercise 2: Use a scoped virtual executor
        try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
            List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();for(int value=1;value<=4;value++){int input=value;futures.add(executor.submit(() -> input*input));}
            List<Integer> results=new ArrayList<>();for(var future:futures)results.add(future.get(2,java.util.concurrent.TimeUnit.SECONDS));
            assert results.equals(List.of(1,4,9,16));
        }

        // Exercise 3: Limit a scarce resource with a semaphore
        var permits=new java.util.concurrent.Semaphore(2);var active=new java.util.concurrent.atomic.AtomicInteger();var maximum=new java.util.concurrent.atomic.AtomicInteger();var entered=new java.util.concurrent.CountDownLatch(2);var release=new java.util.concurrent.CountDownLatch(1);
        try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
            List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();
            for(int i=0;i<6;i++)futures.add(executor.submit(() -> {if(!permits.tryAcquire(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("admission timeout");try{int now=active.incrementAndGet();maximum.accumulateAndGet(now,Math::max);entered.countDown();if(!release.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("gate timeout");return 1;}finally{active.decrementAndGet();permits.release();}}));
            try{assert entered.await(2,java.util.concurrent.TimeUnit.SECONDS);}finally{release.countDown();}
            int completed=0;for(var future:futures)completed+=future.get(3,java.util.concurrent.TimeUnit.SECONDS);assert completed==6 && maximum.get()==2;
        }

        // Exercise 4: Preserve a CPU calculation contract
        int sequential=java.util.stream.IntStream.rangeClosed(1,1000).sum();
        try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
            List<java.util.concurrent.Future<Integer>> parts=new ArrayList<>();for(int p=0;p<4;p++){int start=p*250+1,end=(p+1)*250;parts.add(executor.submit(() -> java.util.stream.IntStream.rangeClosed(start,end).sum()));}
            int total=0;for(var future:parts)total+=future.get(2,java.util.concurrent.TimeUnit.SECONDS);assert total==sequential && total==500500;
        }

        // Exercise 5: Cancel a blocked virtual task
        var started=new java.util.concurrent.CountDownLatch(1);var exited=new java.util.concurrent.CountDownLatch(1);
        try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
            var future=executor.submit(() -> {started.countDown();try{new java.util.concurrent.CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{exited.countDown();}});
            assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);assert future.cancel(true);assert exited.await(2,java.util.concurrent.TimeUnit.SECONDS);
        }

        // Exercise 6: Keep a blocking wait outside a monitor
        Object monitor=new Object();var waiting=new java.util.concurrent.CountDownLatch(1);var finish=new java.util.concurrent.CountDownLatch(1);int[] state={7};var snapshot=new java.util.concurrent.atomic.AtomicInteger();
        Thread worker=Thread.ofVirtual().start(() -> {synchronized(monitor){snapshot.set(state[0]);}waiting.countDown();try{finish.await(2,java.util.concurrent.TimeUnit.SECONDS);}catch(InterruptedException error){Thread.currentThread().interrupt();}});
        assert waiting.await(2,java.util.concurrent.TimeUnit.SECONDS);synchronized(monitor){state[0]=8;}finish.countDown();worker.join(2000);
        assert !worker.isAlive() && snapshot.get()==7 && state[0]==8;
    }
}
