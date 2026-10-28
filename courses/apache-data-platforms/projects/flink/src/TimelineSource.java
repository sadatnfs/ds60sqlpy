import java.io.IOException;
import java.io.Serializable;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import org.apache.flink.api.common.eventtime.Watermark;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.connector.source.Boundedness;
import org.apache.flink.api.connector.source.ReaderOutput;
import org.apache.flink.api.connector.source.Source;
import org.apache.flink.api.connector.source.SourceReader;
import org.apache.flink.api.connector.source.SourceReaderContext;
import org.apache.flink.api.connector.source.SourceSplit;
import org.apache.flink.api.connector.source.SplitEnumerator;
import org.apache.flink.api.connector.source.SplitEnumeratorContext;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.core.io.InputStatus;
import org.apache.flink.core.io.SimpleVersionedSerializer;

/** A real bounded FLIP27 source: one record/watermark command per nonblocking poll. */
public final class TimelineSource
  implements
    Source<WorkshopJobs.Event, TimelineSource.Split, List<TimelineSource.Split>>,
    ResultTypeQueryable<WorkshopJobs.Event> {

  public record Split(int cursor) implements SourceSplit {
    public String splitId() {
      return "fixed-timeline";
    }
  }

  private static final class Command implements Serializable {

    final WorkshopJobs.Event event;
    final long watermark;

    Command(WorkshopJobs.Event event, long watermark) {
      this.event = event;
      this.watermark = watermark;
    }
  }

  private final List<Command> commands;

  public TimelineSource(String source) throws IOException {
    Path path = Path.of(source);
    if (
      !source.equals("/state/input/timeline.txt") ||
      Files.isSymbolicLink(path) ||
      Files.size(path) > 8192
    ) {
      throw new IllegalArgumentException("Expected the bounded owned timeline source");
    }
    var values = new ArrayList<Command>();
    for (String line : Files.readAllLines(path)) {
      String[] fields = line.split(",", -1);
      if (fields.length == 2 && fields[0].equals("W")) {
        values.add(new Command(null, Long.parseLong(fields[1])));
      } else if (
        fields.length == 5 &&
        fields[0].equals("E") &&
        (fields[2].equals("east") || fields[2].equals("west"))
      ) {
        values.add(
          new Command(
            new WorkshopJobs.Event(
              Long.parseLong(fields[1]),
              fields[2],
              Long.parseLong(fields[3]),
              Long.parseLong(fields[4])
            ),
            0
          )
        );
      } else {
        throw new IllegalArgumentException("Unsupported fixed timeline command");
      }
      if (values.size() > 32) throw new IllegalArgumentException("Timeline exceeds command bound");
    }
    if (values.size() != 7) throw new IllegalArgumentException("Expected seven timeline commands");
    commands = List.copyOf(values);
  }

  public Boundedness getBoundedness() {
    return Boundedness.BOUNDED;
  }

  public TypeInformation<WorkshopJobs.Event> getProducedType() {
    return TypeInformation.of(WorkshopJobs.Event.class);
  }

  public SourceReader<WorkshopJobs.Event, Split> createReader(SourceReaderContext context) {
    return new SourceReader<>() {
      private Split split;
      private boolean noMore;
      private final CompletableFuture<Void> available = new CompletableFuture<>();

      public void start() {
        context.sendSplitRequest();
      }

      public InputStatus pollNext(ReaderOutput<WorkshopJobs.Event> output) {
        if (split == null) return noMore ? InputStatus.END_OF_INPUT : InputStatus.NOTHING_AVAILABLE;
        if (split.cursor() >= commands.size()) return InputStatus.END_OF_INPUT;
        Command command = commands.get(split.cursor());
        split = new Split(split.cursor() + 1);
        if (command.event == null) output.emitWatermark(new Watermark(command.watermark));
        else output.collect(command.event, command.event.timestamp);
        return split.cursor() < commands.size()
          ? InputStatus.MORE_AVAILABLE
          : InputStatus.END_OF_INPUT;
      }

      public List<Split> snapshotState(long checkpointId) {
        return split == null ? List.of() : List.of(split);
      }

      public CompletableFuture<Void> isAvailable() {
        return available;
      }

      public void addSplits(List<Split> added) {
        if (added.size() != 1 || split != null) throw new IllegalStateException(
          "One fixed timeline split is expected"
        );
        split = added.get(0);
        available.complete(null);
      }

      public void notifyNoMoreSplits() {
        noMore = true;
        available.complete(null);
      }

      public void close() {}
    };
  }

  private static final class Enumerator implements SplitEnumerator<Split, List<Split>> {

    private final SplitEnumeratorContext<Split> context;
    private final ArrayDeque<Split> pending;

    Enumerator(SplitEnumeratorContext<Split> context, List<Split> values) {
      this.context = context;
      pending = new ArrayDeque<>(values);
    }

    private void assign(int reader) {
      if (!pending.isEmpty()) context.assignSplit(pending.removeFirst(), reader);
      context.signalNoMoreSplits(reader);
    }

    public void start() {}

    public void handleSplitRequest(int subtaskId, String hostname) {
      assign(subtaskId);
    }

    public void addSplitsBack(List<Split> splits, int subtaskId) {
      pending.addAll(splits);
      for (int reader : context.registeredReaders().keySet()) {
        if (pending.isEmpty()) break;
        assign(reader);
      }
    }

    public void addReader(int subtaskId) {}

    public List<Split> snapshotState(long checkpointId) {
      return List.copyOf(pending);
    }

    public void close() {}
  }

  public SplitEnumerator<Split, List<Split>> createEnumerator(
    SplitEnumeratorContext<Split> context
  ) {
    return new Enumerator(context, List.of(new Split(0)));
  }

  public SplitEnumerator<Split, List<Split>> restoreEnumerator(
    SplitEnumeratorContext<Split> context,
    List<Split> state
  ) {
    return new Enumerator(context, state);
  }

  private static Split decode(int version, byte[] bytes) throws IOException {
    if (version != 1 || bytes.length != 4) throw new IOException(
      "Unsupported timeline split format"
    );
    int cursor = ByteBuffer.wrap(bytes).getInt();
    if (cursor < 0 || cursor > 32) throw new IOException("Invalid timeline cursor");
    return new Split(cursor);
  }

  public SimpleVersionedSerializer<Split> getSplitSerializer() {
    return new SimpleVersionedSerializer<>() {
      public int getVersion() {
        return 1;
      }

      public byte[] serialize(Split split) {
        return ByteBuffer.allocate(4).putInt(split.cursor()).array();
      }

      public Split deserialize(int version, byte[] bytes) throws IOException {
        return decode(version, bytes);
      }
    };
  }

  public SimpleVersionedSerializer<List<Split>> getEnumeratorCheckpointSerializer() {
    return new SimpleVersionedSerializer<>() {
      public int getVersion() {
        return 1;
      }

      public byte[] serialize(List<Split> splits) throws IOException {
        if (splits.size() > 1) throw new IOException("Too many timeline splits");
        ByteBuffer buffer = ByteBuffer.allocate(4 + splits.size() * 4).putInt(splits.size());
        for (Split split : splits) buffer.putInt(split.cursor());
        return buffer.array();
      }

      public List<Split> deserialize(int version, byte[] bytes) throws IOException {
        if (version != 1 || (bytes.length != 4 && bytes.length != 8)) throw new IOException(
          "Invalid enumerator format"
        );
        ByteBuffer buffer = ByteBuffer.wrap(bytes);
        int count = buffer.getInt();
        if (count < 0 || count > 1 || bytes.length != 4 + 4 * count) throw new IOException(
          "Invalid split count"
        );
        return count == 0
          ? List.of()
          : List.of(decode(1, ByteBuffer.allocate(4).putInt(buffer.getInt()).array()));
      }
    };
  }
}
