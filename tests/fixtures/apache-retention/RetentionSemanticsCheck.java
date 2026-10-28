import java.nio.file.Path;
import java.util.List;

public final class RetentionSemanticsCheck {

  private static int rejected = 0;

  private static void reject(List<RetentionSemantics.Event> records, long end) {
    try {
      RetentionSemantics.validate(records, end);
    } catch (IllegalStateException expected) {
      rejected++;
      return;
    }
    throw new AssertionError("Unexpected acceptance of an invalid retained log");
  }

  public static void main(String[] args) throws Exception {
    var all = RetentionSemantics.completeFixture();
    var original = RetentionSemantics.validate(all, 3);
    var compacted = RetentionSemantics.validate(List.of(all.get(1), all.get(2)), 3);
    if (
      original.observedRecords() != 3 ||
      compacted.observedRecords() != 2 ||
      !original.latest().equals(compacted.latest()) ||
      !compacted.offsets().equals(List.of(1L, 2L))
    ) throw new AssertionError("Valid compaction changed latest state");
    reject(List.of(), 3);
    reject(List.of(all.get(0), all.get(2)), 3);
    reject(List.of(all.get(0), all.get(1)), 3);
    reject(List.of(all.get(1)), 3);
    reject(List.of(all.get(2)), 3);
    reject(List.of(all.get(1), all.get(1), all.get(2)), 3);
    reject(List.of(new RetentionSemantics.Event(0, "acct-1", "wrong"), all.get(1), all.get(2)), 3);
    reject(List.of(new RetentionSemantics.Event(1, "acct-1", "v1"), all.get(2)), 3);
    reject(List.of(all.get(1), new RetentionSemantics.Event(2, "acct-2", null)), 3);
    reject(List.of(all.get(1), all.get(2), new RetentionSemantics.Event(3, "acct-3", "v4")), 3);
    reject(all, 2);
    reject(all, 4);
    String source = RetentionSemantics.sourceSha(Path.of(args[0]));
    if (!source.matches("[a-f0-9]{64}")) throw new AssertionError("Invalid source digest");
    System.out.println(
      "{\"passed\":true,\"semantic_only\":true,\"valid_cases\":2,\"rejected_cases\":" +
        rejected +
        ",\"source_sha256\":\"" +
        source +
        "\"}"
    );
  }
}
