import java.util.*;

public class Main {

  static final class Probe implements AutoCloseable {

    private final String name;
    private final List<String> events;
    private final boolean fail;

    Probe(String name, List<String> events, boolean fail) {
      this.name = name;
      this.events = events;
      this.fail = fail;
    }

    public void close() throws java.io.IOException {
      events.add("close" + name);
      if (fail) throw new java.io.IOException("close" + name);
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Close on normal completion
    List<String> events = new ArrayList<>();
    try (Probe resource = new Probe("A", events, false)) {
      events.add("body");
    }
    assert events.equals(List.of("body", "closeA"));

    // Exercise 2: Close in reverse order
    events.clear();
    try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {
      events.add("body");
    }
    assert events.equals(List.of("body", "closeB", "closeA"));

    // Exercise 3: Close after body failure
    events.clear();
    boolean bodyFailed = false;
    try (Probe a = new Probe("A", events, false)) {
      throw new IllegalStateException("body");
    } catch (IllegalStateException expected) {
      bodyFailed = true;
    }
    assert bodyFailed && events.equals(List.of("closeA"));

    // Exercise 4: Preserve suppressed close failure
    events.clear();
    try (Probe a = new Probe("A", events, true)) {
      throw new IllegalStateException("body");
    } catch (IllegalStateException expected) {
      assert expected.getMessage().equals("body");
      assert expected.getSuppressed().length == 1;
      assert expected.getSuppressed()[0].getMessage().equals("closeA");
    }

    // Exercise 5: Observe close-only failure
    boolean closeFailed = false;
    try (Probe a = new Probe("A", events, true)) {} catch (java.io.IOException expected) {
      closeFailed = expected.getMessage().equals("closeA");
    }
    assert closeFailed;

    // Exercise 6: Retain a translated cause
    var original = new java.io.IOException("read failed");
    var translated = new IllegalStateException("Cannot load lesson fixture", original);
    assert translated.getCause() == original && translated.getMessage().contains("fixture");
  }
}
