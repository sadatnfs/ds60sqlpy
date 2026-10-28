import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.functions.OpenContext;
import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringEncoder;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.connector.source.lib.NumberSequenceSource;
import org.apache.flink.api.connector.source.util.ratelimit.RateLimiterStrategy;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.GlobalConfiguration;
import org.apache.flink.configuration.PipelineOptions;
import org.apache.flink.connector.datagen.source.DataGeneratorSource;
import org.apache.flink.connector.file.sink.FileSink;
import org.apache.flink.connector.file.src.FileSource;
import org.apache.flink.connector.file.src.reader.TextLineInputFormat;
import org.apache.flink.core.fs.Path;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.streaming.api.functions.sink.filesystem.rollingpolicies.OnCheckpointRollingPolicy;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.types.Row;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

/** Fixed, bounded actual Flink jobs; services and dependencies are prepared separately. */
public final class WorkshopJobs {

  public static final OutputTag<Event> LATE = new OutputTag<Event>("late-events") {};

  public static final class Event implements java.io.Serializable {

    public long id;
    public String key;
    public long timestamp;
    public long amount;

    public Event() {}

    public Event(long id, String key, long timestamp, long amount) {
      this.id = id;
      this.key = key;
      this.timestamp = timestamp;
      this.amount = amount;
    }
  }

  public static final class ParseOrder implements MapFunction<String, Event> {

    public Event map(String line) {
      String[] fields = line.split(",", -1);
      if (fields.length != 4) throw new IllegalArgumentException(
        "Expected four fixed source fields"
      );
      String key = fields[1];
      if (!key.equals("east") && !key.equals("west")) throw new IllegalArgumentException(
        "Unknown source region"
      );
      return new Event(
        Long.parseLong(fields[0]),
        key,
        Long.parseLong(fields[3]),
        Long.parseLong(fields[2])
      );
    }
  }

  public static final class RunningTotal extends KeyedProcessFunction<String, Event, String> {

    private transient ValueState<Long> total;

    public void open(OpenContext context) throws Exception {
      total = getRuntimeContext().getState(new ValueStateDescriptor<>("total", Types.LONG));
    }

    public void processElement(Event event, Context context, Collector<String> output)
      throws Exception {
      Long old = total.value();
      long next = (old == null ? 0 : old) + event.amount;
      total.update(next);
      output.collect("update," + event.key + "," + event.id + "," + next);
    }
  }

  public static final class WindowTotals
    extends ProcessWindowFunction<Event, String, String, TimeWindow> {

    public void process(
      String key,
      Context context,
      Iterable<Event> values,
      Collector<String> output
    ) {
      long count = 0,
        total = 0;
      for (Event event : values) {
        count++;
        total += event.amount;
      }
      output.collect(
        "window," +
          key +
          "," +
          context.window().getStart() +
          "," +
          context.window().getEnd() +
          "," +
          count +
          "," +
          total
      );
    }
  }

  public static final class LateLine implements MapFunction<Event, String> {

    public String map(Event event) {
      return "late," + event.key + "," + event.id + "," + event.timestamp + "," + event.amount;
    }
  }

  public static final class Inactivity extends KeyedProcessFunction<String, Event, String> {

    private transient ValueState<Long> total;
    private transient ValueState<Long> activeTimer;

    public void open(OpenContext context) throws Exception {
      total = getRuntimeContext().getState(new ValueStateDescriptor<>("total", Types.LONG));
      activeTimer = getRuntimeContext().getState(
        new ValueStateDescriptor<>("active-timer", Types.LONG)
      );
    }

    public void processElement(Event event, Context context, Collector<String> output)
      throws Exception {
      if (event.timestamp < context.timerService().currentWatermark()) {
        context.output(LATE, event);
        return;
      }
      Long prior = total.value();
      long next = (prior == null ? 0 : prior) + event.amount;
      total.update(next);
      Long oldTimer = activeTimer.value();
      if (oldTimer != null) context.timerService().deleteEventTimeTimer(oldTimer);
      long timer = event.timestamp + 500;
      activeTimer.update(timer);
      context.timerService().registerEventTimeTimer(timer);
      output.collect("update," + event.key + "," + event.id + "," + next);
    }

    public void onTimer(long timestamp, OnTimerContext context, Collector<String> output)
      throws Exception {
      Long current = activeTimer.value();
      if (current == null || current != timestamp) return;
      output.collect("timer," + context.getCurrentKey() + "," + timestamp + "," + total.value());
      activeTimer.clear();
      total.clear();
    }
  }

  public static final class ManagedTotal extends RichMapFunction<Long, String> {

    private transient ValueState<Long> total;

    public void open(OpenContext context) throws Exception {
      total = getRuntimeContext().getState(new ValueStateDescriptor<>("sum", Types.LONG));
    }

    public String map(Long id) throws Exception {
      Long prior = total.value();
      long next = (prior == null ? 0 : prior) + id + 1;
      total.update(next);
      return id + "," + next;
    }
  }

  public static final class Payload implements MapFunction<Long, String> {

    public String map(Long id) {
      return id + ":" + "x".repeat(8192);
    }
  }

  public static final class SlowConsumer implements MapFunction<String, String> {

    public String map(String value) throws Exception {
      Thread.sleep(10);
      return value.substring(0, value.indexOf(':'));
    }
  }

  private static void sink(DataStream<String> stream, String output, String uid) {
    FileSink<String> writer = FileSink.forRowFormat(
      new Path(output),
      new SimpleStringEncoder<String>("UTF-8")
    )
      .withRollingPolicy(OnCheckpointRollingPolicy.build())
      .build();
    stream.sinkTo(writer).name("bounded-result-files").uid(uid).setParallelism(1);
  }

  private static void sql(String request, String output) throws Exception {
    Configuration configuration = GlobalConfiguration.loadConfiguration(
      System.getenv("FLINK_CONF_DIR")
    );
    configuration.set(PipelineOptions.NAME, "DS60 sql " + request);
    EnvironmentSettings settings = EnvironmentSettings.newInstance()
      .inBatchMode()
      .withConfiguration(configuration)
      .build();
    TableEnvironment table = TableEnvironment.create(settings);
    table.executeSql(
      "CREATE TEMPORARY TABLE orders (id BIGINT, region STRING, amount BIGINT, event_ms BIGINT) " +
        "WITH ('connector'='filesystem','path'='file:///state/input/orders.csv','format'='csv')"
    );
    var result = table.executeSql(
      "SELECT region, SUM(amount) AS total FROM orders GROUP BY region ORDER BY region"
    );
    var lines = new ArrayList<String>();
    try (var iterator = result.collect()) {
      while (iterator.hasNext()) {
        Row row = iterator.next();
        if (lines.size() >= 2) throw new IllegalStateException(
          "SQL result exceeds the two-group fixture"
        );
        lines.add(row.getField(0) + "," + row.getField(1));
      }
    }
    if (!lines.equals(List.of("east,11", "west,9"))) throw new IllegalStateException(
      "Actual SQL result differs"
    );
    var destination = Paths.get(output);
    Files.createDirectories(destination);
    Files.write(
      destination.resolve("sql-rows.csv"),
      lines,
      StandardCharsets.UTF_8,
      java.nio.file.StandardOpenOption.CREATE_NEW
    );
  }

  public static void main(String[] arguments) throws Exception {
    if (arguments.length != 4) throw new IllegalArgumentException(
      "Use mode, requestID, output and parallelism"
    );
    String mode = arguments[0],
      request = arguments[1],
      output = arguments[2];
    int parallelism = Integer.parseInt(arguments[3]);
    if (
      !request.matches("[a-f0-9]{32}") ||
      !output.equals("/state/results/" + request) ||
      (parallelism != 1 && parallelism != 2)
    ) {
      throw new IllegalArgumentException("Unexpected owned request, output or parallelism");
    }
    if (!List.of("checkpointed", "changed-uid").contains(mode) && parallelism != 1) {
      throw new IllegalArgumentException(
        "Only the explicit compatible state route changes parallelism"
      );
    }
    if (mode.equals("sql")) {
      sql(request, output);
      return;
    }
    if (
      !List.of("bounded", "windows", "state", "checkpointed", "changed-uid", "pressure").contains(
        mode
      )
    ) {
      throw new IllegalArgumentException("Unknown fixed job mode");
    }
    StreamExecutionEnvironment environment = StreamExecutionEnvironment.getExecutionEnvironment();
    environment.setRuntimeMode(RuntimeExecutionMode.STREAMING);
    environment.setParallelism(parallelism);
    environment.setMaxParallelism(128);
    environment.enableCheckpointing(200);
    DataStream<String> result;
    if (mode.equals("bounded")) {
      var source = FileSource.forRecordStreamFormat(
        new TextLineInputFormat(),
        new Path("/state/input/orders.csv")
      ).build();
      result = environment
        .fromSource(source, WatermarkStrategy.noWatermarks(), "fixed-order-file")
        .uid("orders-source")
        .setParallelism(1)
        .map(new ParseOrder())
        .keyBy(event -> event.key)
        .process(new RunningTotal())
        .uid("region-total");
    } else if (mode.equals("windows") || mode.equals("state")) {
      var events = environment
        .fromSource(
          new TimelineSource("/state/input/timeline.txt"),
          WatermarkStrategy.noWatermarks(),
          "explicit-event-time"
        )
        .uid("timeline-source")
        .setParallelism(1);
      if (mode.equals("windows")) {
        var windows = events
          .keyBy(event -> event.key)
          .window(TumblingEventTimeWindows.of(Duration.ofMillis(2000)))
          .sideOutputLateData(LATE)
          .process(new WindowTotals())
          .uid("window-totals");
        result = windows.union(windows.getSideOutput(LATE).map(new LateLine()));
      } else {
        var updates = events
          .keyBy(event -> event.key)
          .process(new Inactivity())
          .uid("inactivity-state");
        result = updates.union(updates.getSideOutput(LATE).map(new LateLine()));
      }
    } else if (mode.equals("pressure")) {
      result = environment
        .fromSource(
          new NumberSequenceSource(0, 499),
          WatermarkStrategy.noWatermarks(),
          "pressure-numbers"
        )
        .uid("pressure-source")
        .map(new Payload())
        .name("pressure-payload-producer")
        .uid("pressure-payload")
        .disableChaining()
        .map(new SlowConsumer())
        .name("bounded-slow-consumer")
        .uid("pressure-consumer")
        .disableChaining();
    } else {
      result = environment
        .fromSource(
          new DataGeneratorSource<Long>(
            value -> value,
            100,
            RateLimiterStrategy.perSecond(5),
            Types.LONG
          ),
          WatermarkStrategy.noWatermarks(),
          "replayable-numbers"
        )
        .uid("numbers-source")
        .keyBy(value -> "all")
        .map(new ManagedTotal())
        .name("checkpointed-total")
        .uid(mode.equals("changed-uid") ? "counter-v2" : "counter-v1");
    }
    sink(result, output, "sink-" + (mode.equals("changed-uid") ? "checkpointed" : mode));
    environment.execute("DS60 " + mode + " " + request);
  }
}
