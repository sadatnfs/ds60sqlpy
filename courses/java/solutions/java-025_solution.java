import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Expose a strong retention path
    List<byte[]> retained = new ArrayList<>();
    byte[] payload = new byte[1024];
    payload[0] = 7;
    retained.add(payload);
    payload = null;
    assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;

    // Exercise 2: Remove one ownership path deliberately
    byte[] separate = retained.get(0);
    retained.clear();
    assert retained.isEmpty() && separate[0] == 7;

    // Exercise 3: Inspect a weak reference without timing assumptions
    var weak = new java.lang.ref.WeakReference<>(separate);
    assert weak.get() == separate;
    java.lang.ref.Reference.reachabilityFence(separate);

    // Exercise 4: Separate value size from allocation count
    List<byte[]> blocks = new ArrayList<>();
    for (int i = 0; i < 10; i++) blocks.add(new byte[128]);
    int logical = blocks
      .stream()
      .mapToInt(block -> block.length)
      .sum();
    assert logical == 1280;

    // Exercise 5: Reuse a bounded working buffer
    byte[] buffer = new byte[16];
    int identity = System.identityHashCode(buffer);
    for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);
    assert System.identityHashCode(buffer) == identity && buffer[0] == 9;

    // Exercise 6: Record process memory cautiously
    Runtime runtime = Runtime.getRuntime();
    long total = runtime.totalMemory(),
      free = runtime.freeMemory(),
      maximum = runtime.maxMemory();
    assert total >= 0 && free >= 0 && maximum >= total;
  }
}
