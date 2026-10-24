# java-024: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections,remote quotas and memory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java 21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations,preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ,so version the explanation. Keep blocking work outside a monitor when the state contract permits it,or redesign the synchronization carefully. This lesson checks thread identity,lifetime,cancellation and a semaphore admission limit without making throughput claims.

**Virtual thread:** A lightweight Java thread scheduled over carrier threads.

**Carrier:** An operating-system thread executing virtual-thread work.

**Backpressure:** A limit on admitted resource-consuming operations.

**Pinning in Java 21:** A condition preventing a blocked virtual thread from releasing its carrier.

## Reading the reference

Thread.ofVirtual starts a virtual thread;isVirtual identifies it. Executors.newVirtualThreadPerTaskExecutor creates a new virtual thread for each admitted task. A Semaphore can bound simultaneous access to a scarce resource independently of thread count. Future.get andlatches provide bounded completion evidence. Cooperative interruption remains necessary,just as with platform threads.

## Exercise 1: Observe virtual identity

Task: Start a virtual thread that records isVirtual and join it.

The identity check establishes the actual thread type. It does not measure performance or the number of carrier threads used.

```java
var virtual=new java.util.concurrent.atomic.AtomicBoolean();Thread task=Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));task.join(2000);
assert !task.isAlive() && virtual.get();
```

**Expected:** true and terminated.

**Verify:** Compare the program values or named exception with true and terminated. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Use a scoped virtual executor

Task: Submit four square calculations and retrieve their results with timeouts.

The executor lifetime encloses its tasks. Capturing a separate effectively-final input per submission avoids confusing loop-state ownership.

```java
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();for(int value=1;value<=4;value++){int input=value;futures.add(executor.submit(() -> input*input));}
    List<Integer> results=new ArrayList<>();for(var future:futures)results.add(future.get(2,java.util.concurrent.TimeUnit.SECONDS));
    assert results.equals(List.of(1,4,9,16));
}
```

**Expected:** 1,4,9,16.

**Verify:** Compare the program values or named exception with 1,4,9,16. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Limit a scarce resource with a semaphore

Task: Run six tasks but allow only two inside a gated resource section.

Thread creation is separate from resource admission. The semaphore protects the scarce section even when many virtual threads exist.

```java
var permits=new java.util.concurrent.Semaphore(2);var active=new java.util.concurrent.atomic.AtomicInteger();var maximum=new java.util.concurrent.atomic.AtomicInteger();var entered=new java.util.concurrent.CountDownLatch(2);var release=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();
    for(int i=0;i<6;i++)futures.add(executor.submit(() -> {if(!permits.tryAcquire(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("admission timeout");try{int now=active.incrementAndGet();maximum.accumulateAndGet(now,Math::max);entered.countDown();if(!release.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("gate timeout");return 1;}finally{active.decrementAndGet();permits.release();}}));
    try{assert entered.await(2,java.util.concurrent.TimeUnit.SECONDS);}finally{release.countDown();}
    int completed=0;for(var future:futures)completed+=future.get(3,java.util.concurrent.TimeUnit.SECONDS);assert completed==6 && maximum.get()==2;
}
```

**Expected:** maximum active count2;all six complete.

**Verify:** Compare the program values or named exception with maximum active count2;all six complete. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Preserve a CPU calculation contract

Task: Compare a sequential sum1..1000 with four partitioned virtual tasks.

Correct partitioning is checked independently of timing. Virtual threads do not promise to accelerate CPU-bound arithmetic.

```java
int sequential=java.util.stream.IntStream.rangeClosed(1,1000).sum();
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> parts=new ArrayList<>();for(int p=0;p<4;p++){int start=p*250+1,end=(p+1)*250;parts.add(executor.submit(() -> java.util.stream.IntStream.rangeClosed(start,end).sum()));}
    int total=0;for(var future:parts)total+=future.get(2,java.util.concurrent.TimeUnit.SECONDS);assert total==sequential && total==500500;
}
```

**Expected:** both500500;no speed claim.

**Verify:** Compare the program values or named exception with both500500;no speed claim. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Cancel a blocked virtual task

Task: Interrupt a virtual task waiting on a latch and observe its cleanup signal.

Lightweight scheduling does not change cancellation into forcible termination. Task code still owns resource cleanup and interruption response.

```java
var started=new java.util.concurrent.CountDownLatch(1);var exited=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    var future=executor.submit(() -> {started.countDown();try{new java.util.concurrent.CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{exited.countDown();}});
    assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);assert future.cancel(true);assert exited.await(2,java.util.concurrent.TimeUnit.SECONDS);
}
```

**Expected:** Future cancelled;task exits cooperatively.

**Verify:** Compare the program values or named exception with Future cancelled;task exits cooperatively. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Keep a blocking wait outside a monitor

Task: Read a state snapshot inside a synchronized block,then wait on a latch after leaving it.

This design releases the monitor before blocking. It avoids the illustrated Java 21 monitor-held blocking pattern,but it does not measure carrier pinning or prove a general performance improvement.

```java
Object monitor=new Object();var waiting=new java.util.concurrent.CountDownLatch(1);var finish=new java.util.concurrent.CountDownLatch(1);int[] state={7};var snapshot=new java.util.concurrent.atomic.AtomicInteger();
Thread worker=Thread.ofVirtual().start(() -> {synchronized(monitor){snapshot.set(state[0]);}waiting.countDown();try{finish.await(2,java.util.concurrent.TimeUnit.SECONDS);}catch(InterruptedException error){Thread.currentThread().interrupt();}});
assert waiting.await(2,java.util.concurrent.TimeUnit.SECONDS);synchronized(monitor){state[0]=8;}finish.countDown();worker.join(2000);
assert !worker.isAlive() && snapshot.get()==7 && state[0]==8;
```

**Expected:** caller can acquire the monitor while the worker is waiting.

**Verify:** Compare the program values or named exception with caller can acquire the monitor while the worker is waiting. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
