import java.util.*;

public class Main {

  static final class Publication {

    int data;
    volatile boolean ready;
  }

  static void joinBounded(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("thread did not terminate");
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Publish a result through join
    int[] result = { 0 };
    Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);
    joinBounded(worker);
    assert result[0] == 42;

    // Exercise 2: Publish initial state through start
    int[] input = { 7 };
    var observed = new java.util.concurrent.atomic.AtomicInteger();
    Thread reader = Thread.ofPlatform().start(() -> observed.set(input[0]));
    joinBounded(reader);
    assert observed.get() == 7;

    // Exercise 3: Force a lost update
    int[] counter = { 0 };
    var barrier = new java.util.concurrent.CyclicBarrier(2);
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable increment = () -> {
      try {
        int saved = counter[0];
        barrier.await(2, java.util.concurrent.TimeUnit.SECONDS);
        counter[0] = saved + 1;
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(increment),
      b = Thread.ofPlatform().start(increment);
    joinBounded(a);
    joinBounded(b);
    assert failure.get() == null && counter[0] == 1;

    // Exercise 4: Use a volatile publication flag
    Publication publication = new Publication();
    var seen = new java.util.concurrent.atomic.AtomicInteger(-1);
    Thread consumer = Thread.ofPlatform().start(() -> {
      long deadline = System.nanoTime() + 2_000_000_000L;
      while (!publication.ready && System.nanoTime() < deadline) Thread.onSpinWait();
      if (publication.ready) seen.set(publication.data);
    });
    Thread producer = Thread.ofPlatform().start(() -> {
      publication.data = 99;
      publication.ready = true;
    });
    joinBounded(producer);
    joinBounded(consumer);
    assert seen.get() == 99;

    // Exercise 5: Distinguish run from start
    Thread caller = Thread.currentThread();
    var identity = new java.util.concurrent.atomic.AtomicReference<Thread>();
    Runnable action = () -> identity.set(Thread.currentThread());
    action.run();
    assert identity.get() == caller;

    // Exercise 6: Respond to interruption
    var started = new java.util.concurrent.CountDownLatch(1);
    var waiting = new java.util.concurrent.CountDownLatch(1);
    var interrupted = new java.util.concurrent.atomic.AtomicBoolean();
    Thread blocked = Thread.ofPlatform().start(() -> {
      started.countDown();
      try {
        waiting.await();
      } catch (InterruptedException expected) {
        Thread.currentThread().interrupt();
        interrupted.set(Thread.currentThread().isInterrupted());
      }
    });
    assert started.await(2, java.util.concurrent.TimeUnit.SECONDS);
    blocked.interrupt();
    joinBounded(blocked);
    assert interrupted.get();
  }
}
