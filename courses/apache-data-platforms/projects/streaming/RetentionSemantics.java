import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

/** Pure invariant checks shared by the real Kafka reader and compiler-only tests. */
public final class RetentionSemantics {

  public record Event(long offset, String key, String value) {}

  public record Verified(long observedRecords, List<Long> offsets, Map<String, String> latest) {}

  private static final String SOURCE = "acct-1|v1\nacct-1|v2\nacct-2|v3\n";
  private static final Map<Long, Event> ALLOWED = Map.of(
    0L,
    new Event(0, "acct-1", "v1"),
    1L,
    new Event(1, "acct-1", "v2"),
    2L,
    new Event(2, "acct-2", "v3")
  );

  public static String sourceSha(Path path) throws Exception {
    if (Files.isSymbolicLink(path) || !Files.isRegularFile(path) || Files.size(path) > 256) {
      throw new IllegalArgumentException("Expected one bounded regular source fixture");
    }
    byte[] bytes = Files.readAllBytes(path);
    if (!new String(bytes, StandardCharsets.UTF_8).equals(SOURCE)) {
      throw new IllegalArgumentException("Source fixture differs; no broker reset is permitted");
    }
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  public static Verified validate(List<Event> observed, long endOffset) {
    if (endOffset != 3) {
      throw new IllegalStateException("Expected source end offset 3; no reset performed");
    }
    var ordered = new TreeMap<Long, Event>();
    for (Event event : observed) {
      Event expected = ALLOWED.get(event.offset());
      if (
        expected == null ||
        !Objects.equals(expected.key(), event.key()) ||
        !Objects.equals(expected.value(), event.value())
      ) {
        throw new IllegalStateException("Unexpected retained offset/key/value; no reset performed");
      }
      if (ordered.putIfAbsent(event.offset(), event) != null) {
        throw new IllegalStateException("Duplicate retained offset");
      }
    }
    if (!ordered.containsKey(1L) || !ordered.containsKey(2L)) {
      throw new IllegalStateException("Required latest-key records are missing");
    }
    var latest = new TreeMap<String, String>();
    for (Event event : ordered.values()) {
      latest.put(event.key(), event.value());
    }
    if (!latest.equals(Map.of("acct-1", "v2", "acct-2", "v3"))) {
      throw new IllegalStateException("Latest key state differs from the independent oracle");
    }
    return new Verified(
      observed.size(),
      List.copyOf(ordered.keySet()),
      Collections.unmodifiableMap(latest)
    );
  }

  public static List<Event> completeFixture() {
    return new ArrayList<>(List.of(ALLOWED.get(0L), ALLOWED.get(1L), ALLOWED.get(2L)));
  }
}
