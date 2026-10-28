import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.config.ConfigResource;
import org.apache.kafka.common.config.TopicConfig;
import org.apache.kafka.common.errors.TopicExistsException;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;

/** Actual bounded Kafka compacted-log readback, not a forced-cleaner demonstration. */
public final class RetentionProbe {

  private static final String TOPIC = "classroom-compacted";
  private static final String BOOTSTRAP = "kafka:9092";

  private static void ensureTopicAndPolicy() throws Exception {
    var properties = new Properties();
    properties.put("bootstrap.servers", BOOTSTRAP);
    properties.put("request.timeout.ms", "5000");
    properties.put("default.api.timeout.ms", "10000");
    try (Admin admin = Admin.create(properties)) {
      var wanted = Map.of(
        TopicConfig.CLEANUP_POLICY_CONFIG,
        "compact",
        TopicConfig.RETENTION_MS_CONFIG,
        "-1",
        TopicConfig.RETENTION_BYTES_CONFIG,
        "-1"
      );
      try {
        admin
          .createTopics(List.of(new NewTopic(TOPIC, 1, (short) 1).configs(wanted)))
          .all()
          .get(10, TimeUnit.SECONDS);
      } catch (ExecutionException error) {
        if (!(error.getCause() instanceof TopicExistsException)) {
          throw error;
        }
      }
      var description = admin
        .describeTopics(List.of(TOPIC))
        .allTopicNames()
        .get(10, TimeUnit.SECONDS)
        .get(TOPIC);
      if (
        description.partitions().size() != 1 ||
        description.partitions().get(0).partition() != 0 ||
        description.partitions().get(0).replicas().size() != 1
      ) {
        throw new IllegalStateException("Expected one partition and replication factor 1");
      }
      var resource = new ConfigResource(ConfigResource.Type.TOPIC, TOPIC);
      var actual = admin
        .describeConfigs(List.of(resource))
        .all()
        .get(10, TimeUnit.SECONDS)
        .get(resource);
      for (var expected : wanted.entrySet()) {
        if (
          actual.get(expected.getKey()) == null ||
          !expected.getValue().equals(actual.get(expected.getKey()).value())
        ) {
          throw new IllegalStateException(
            "Unexpected actual topic policy: " +
              expected.getKey() +
              "; retained data was not altered or reset"
          );
        }
      }
    }
  }

  private static KafkaConsumer<String, String> consumer() {
    var properties = new Properties();
    properties.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
    properties.put(
      ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
      StringDeserializer.class.getName()
    );
    properties.put(
      ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
      StringDeserializer.class.getName()
    );
    properties.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
    properties.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_uncommitted");
    properties.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG, "5000");
    properties.put(ConsumerConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, "10000");
    properties.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "4");
    properties.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, "65536");
    properties.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, "65536");
    return new KafkaConsumer<>(properties);
  }

  private static long endOffset() {
    var partition = new TopicPartition(TOPIC, 0);
    try (var client = consumer()) {
      return client.endOffsets(List.of(partition), Duration.ofSeconds(10)).get(partition);
    }
  }

  private static void initializeOnlyWhenEmpty() throws Exception {
    long end = endOffset();
    if (end != 0) {
      if (end != 3) {
        throw new IllegalStateException("Unexpected retained source offset; no reset performed");
      }
      return;
    }
    var properties = new Properties();
    properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
    properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
    properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
    properties.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
    properties.put(ProducerConfig.ACKS_CONFIG, "all");
    properties.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, "3000");
    properties.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "15000");
    properties.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, "10000");
    try (var producer = new KafkaProducer<String, String>(properties)) {
      for (var event : RetentionSemantics.completeFixture()) {
        var metadata = producer
          .send(new ProducerRecord<>(TOPIC, 0, event.key(), event.value()))
          .get(10, TimeUnit.SECONDS);
        if (metadata.offset() != event.offset()) {
          throw new IllegalStateException(
            "Fixture append offset differs; preserve and inspect partial state"
          );
        }
      }
    }
  }

  private static RetentionSemantics.Verified readToActualEnd() {
    var partition = new TopicPartition(TOPIC, 0);
    var records = new ArrayList<RetentionSemantics.Event>();
    try (var client = consumer()) {
      client.assign(List.of(partition));
      client.seekToBeginning(List.of(partition));
      long end = client.endOffsets(List.of(partition), Duration.ofSeconds(10)).get(partition);
      if (end != 3) {
        throw new IllegalStateException("Unexpected source end offset before read");
      }
      long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
      while (client.position(partition, Duration.ofSeconds(5)) < end) {
        if (System.nanoTime() >= deadline) {
          throw new IllegalStateException("Bounded retained-log read deadline exceeded");
        }
        for (var record : client.poll(Duration.ofMillis(250))) {
          records.add(new RetentionSemantics.Event(record.offset(), record.key(), record.value()));
          if (records.size() > 3) {
            throw new IllegalStateException("Unexpected additional retained records");
          }
        }
      }
      long finalEnd = client.endOffsets(List.of(partition), Duration.ofSeconds(10)).get(partition);
      if (finalEnd != end) {
        throw new IllegalStateException("Source changed during the bounded read");
      }
      return RetentionSemantics.validate(records, end);
    }
  }

  private static String quote(String value) {
    return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 0) {
      throw new IllegalArgumentException("This bounded probe accepts no arguments");
    }
    String sourceSha = RetentionSemantics.sourceSha(Path.of("/project/retention-events.txt"));
    ensureTopicAndPolicy();
    initializeOnlyWhenEmpty();
    var verified = readToActualEnd();
    String offsets = verified
      .offsets()
      .stream()
      .map(String::valueOf)
      .collect(Collectors.joining(","));
    String latest = verified
      .latest()
      .entrySet()
      .stream()
      .map(entry -> quote(entry.getKey()) + ":" + quote(entry.getValue()))
      .collect(Collectors.joining(","));
    System.out.println(
      "{\"schema_version\":1,\"passed\":true,\"configured_cleanup_policy\":\"compact\"," +
        "\"source_sha256\":" +
        quote(sourceSha) +
        ",\"source_end_offset\":3," +
        "\"observed_log_records\":" +
        verified.observedRecords() +
        ",\"retained_offsets\":[" +
        offsets +
        "]," +
        "\"latest_key_state\":{" +
        latest +
        "},\"physical_compaction_demonstrated\":false}"
    );
  }
}
