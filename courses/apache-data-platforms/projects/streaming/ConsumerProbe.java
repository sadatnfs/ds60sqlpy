import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.GroupIdNotFoundException;
import org.apache.kafka.common.serialization.StringDeserializer;

/** Actual committed offsets, replay and independent groups; no rebalance claim. */
public final class ConsumerProbe {

  private static final List<TopicPartition> PARTITIONS = List.of(
    new TopicPartition("classroom-events", 0),
    new TopicPartition("classroom-events", 1)
  );

  private static Properties settings(String group) {
    var p = new Properties();
    p.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
    p.put(ConsumerConfig.GROUP_ID_CONFIG, group);
    p.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    p.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    p.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
    p.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
    p.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG, "5000");
    p.put(ConsumerConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, "10000");
    p.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "10");
    p.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, "65536");
    p.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, "65536");
    return p;
  }

  private static List<String> read(String group, boolean commit) {
    var rows = new ArrayList<String>();
    try (var consumer = new KafkaConsumer<String, String>(settings(group))) {
      consumer.assign(PARTITIONS);
      var end = consumer.endOffsets(PARTITIONS, Duration.ofSeconds(10));
      long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
      while (true) {
        boolean complete = true;
        for (var partition : PARTITIONS) {
          complete &= consumer.position(partition, Duration.ofSeconds(5)) >= end.get(partition);
        }
        if (complete) {
          break;
        }
        if (System.nanoTime() >= deadline) {
          throw new IllegalStateException("Read deadline");
        }
        for (var record : consumer.poll(Duration.ofMillis(250))) {
          rows.add(record.key() + "|" + record.value());
          if (rows.size() > 3) {
            throw new IllegalStateException("Unexpected source records");
          }
        }
      }
      if (commit) {
        var offsets = new HashMap<TopicPartition, OffsetAndMetadata>();
        for (var partition : PARTITIONS) {
          offsets.put(partition, new OffsetAndMetadata(consumer.position(partition)));
        }
        consumer.commitSync(offsets, Duration.ofSeconds(10));
      }
    }
    Collections.sort(rows);
    return rows;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 0) {
      throw new IllegalArgumentException("No arguments accepted");
    }
    String token = UUID.randomUUID().toString();
    String groupA = "ds60-consumer-probe-a-" + token;
    String groupB = "ds60-consumer-probe-b-" + token;
    try {
      var first = read(groupA, false);
      if (first.size() != 3 || !read(groupA, false).equals(first)) {
        throw new IllegalStateException("Uncommitted read did not replay");
      }
      if (!read(groupA, true).equals(first) || !read(groupA, false).isEmpty()) {
        throw new IllegalStateException("Committed offsets were not retained");
      }
      if (!read(groupB, true).equals(first)) {
        throw new IllegalStateException("Independent group did not receive full log");
      }
      System.out.println(
        "{\"passed\":true,\"source_records\":3," +
          "\"uncommitted_replay\":true,\"committed_resume_records\":0," +
          "\"independent_group_records\":3,\"assignment\":\"manual-no-rebalance-claim\"}"
      );
    } finally {
      Map<String, Object> config = new HashMap<>();
      config.put("bootstrap.servers", "kafka:9092");
      config.put("request.timeout.ms", "5000");
      config.put("default.api.timeout.ms", "10000");
      try (Admin admin = Admin.create(config)) {
        for (var result : admin
          .deleteConsumerGroups(List.of(groupA, groupB))
          .deletedGroups()
          .values()) {
          try {
            result.get(10, TimeUnit.SECONDS);
          } catch (ExecutionException error) {
            if (!(error.getCause() instanceof GroupIdNotFoundException)) {
              throw error;
            }
          }
        }
      }
    }
  }
}
