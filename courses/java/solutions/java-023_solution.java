import java.util.*;

public class Main {

  static final class Counter {

    private int value;

    synchronized void increment() {
      value++;
    }

    synchronized int value() {
      return value;
    }
  }

  static void join(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("worker did not stop");
    }
  }

  static void runTwo(Runnable action) throws Exception {
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable checked = () -> {
      try {
        action.run();
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(checked),
      b = Thread.ofPlatform().start(checked);
    join(a);
    join(b);
    if (failure.get() != null) throw new AssertionError("worker failed", failure.get());
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Protect a compound counter
    Counter counter = new Counter();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counter.increment();
    });
    assert counter.value() == 2000;

    // Exercise 2: Use an atomic increment
    var atomic = new java.util.concurrent.atomic.AtomicInteger();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) atomic.incrementAndGet();
    });
    assert atomic.get() == 2000;

    // Exercise 3: Inspect compare-and-set
    var state = new java.util.concurrent.atomic.AtomicInteger();
    assert state.compareAndSet(0, 1);
    assert !state.compareAndSet(0, 2);
    assert state.get() == 1;

    // Exercise 4: Combine map updates atomically
    var counts = new java.util.concurrent.ConcurrentHashMap<String, Integer>();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counts.merge("x", 1, Integer::sum);
    });
    assert counts.get("x") == 2000;

    // Exercise 5: Bound lock contention
    var lock = new java.util.concurrent.locks.ReentrantLock();
    var acquired = new java.util.concurrent.atomic.AtomicBoolean(true);
    lock.lock();
    try {
      Thread contender = Thread.ofPlatform().start(() -> {
        try {
          boolean ok = lock.tryLock(50, java.util.concurrent.TimeUnit.MILLISECONDS);
          acquired.set(ok);
          if (ok) lock.unlock();
        } catch (InterruptedException error) {
          Thread.currentThread().interrupt();
        }
      });
      join(contender);
      assert !acquired.get();
    } finally {
      lock.unlock();
    }
    assert !lock.isLocked();

    // Exercise 6: Use one global order for two locks
    Object first = new Object(),
      second = new Object();
    int[] total = { 0 };
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) {
        synchronized (first) {
          synchronized (second) {
            total[0]++;
          }
        }
      }
    });
    assert total[0] == 2000;
  }
}
