import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
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

/** Real transaction visibility and the boundary of producer idempotence. */
public final class TransactionProbe {

  private static final String TOPIC = "classroom-transactions";
  private static final String BOOTSTRAP = "kafka:9092";

  private static Properties producerProperties() {
    var properties = new Properties();
    properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
    properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
    properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
    properties.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
    properties.put(ProducerConfig.ACKS_CONFIG, "all");
    properties.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "ds60-workshop-transaction-writer");
    properties.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, "3000");
    properties.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "15000");
    properties.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, "10000");
    properties.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, "15000");
    return properties;
  }

  private static KafkaConsumer<String, String> consumer(String isolation) {
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
    properties.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, isolation);
    properties.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG, "5000");
    properties.put(ConsumerConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, "10000");
    properties.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "10");
    properties.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, "65536");
    properties.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, "65536");
    return new KafkaConsumer<>(properties);
  }

  private static void ensureTopic() throws Exception {
    Map<String, Object> settings = new HashMap<>();
    settings.put("bootstrap.servers", BOOTSTRAP);
    settings.put("request.timeout.ms", "5000");
    settings.put("default.api.timeout.ms", "10000");
    try (Admin admin = Admin.create(settings)) {
      var wanted = Map.of(
        TopicConfig.CLEANUP_POLICY_CONFIG,
        "delete",
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
        description.partitions().get(0).replicas().size() != 1
      ) {
        throw new IllegalStateException("Unexpected transaction fixture topology");
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
            "Unexpected transaction retention policy; retained state was not reset"
          );
        }
      }
    }
  }

  private static long lastOffset() {
    var partition = new TopicPartition(TOPIC, 0);
    try (var consumer = consumer("read_uncommitted")) {
      return consumer.endOffsets(List.of(partition), Duration.ofSeconds(10)).get(partition);
    }
  }

  private static void produceWhenEmpty() throws Exception {
    if (lastOffset() != 0) {
      return; // Retain existing evidence; validation below rejects partial or unexpected data.
    }
    try (var producer = new KafkaProducer<String, String>(producerProperties())) {
      producer.initTransactions();
      producer.beginTransaction();
      producer
        .send(new ProducerRecord<>(TOPIC, "order-1", "committed-a"))
        .get(10, TimeUnit.SECONDS);
      producer.commitTransaction();
      producer.beginTransaction();
      producer.send(new ProducerRecord<>(TOPIC, "order-2", "aborted-b")).get(10, TimeUnit.SECONDS);
      producer.abortTransaction();
      producer.beginTransaction();
      producer
        .send(new ProducerRecord<>(TOPIC, "same-business-id", "duplicate-business-call"))
        .get(10, TimeUnit.SECONDS);
      producer
        .send(new ProducerRecord<>(TOPIC, "same-business-id", "duplicate-business-call"))
        .get(10, TimeUnit.SECONDS);
      producer.commitTransaction();
    }
  }

  private static List<String> read(String isolation) {
    var partition = new TopicPartition(TOPIC, 0);
    var values = new ArrayList<String>();
    try (var consumer = consumer(isolation)) {
      consumer.assign(List.of(partition));
      consumer.seekToBeginning(List.of(partition));
      long end = consumer.endOffsets(List.of(partition), Duration.ofSeconds(10)).get(partition);
      long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
      while (consumer.position(partition, Duration.ofSeconds(5)) < end) {
        if (System.nanoTime() >= deadline) {
          throw new IllegalStateException("Bounded consumer deadline exceeded");
        }
        for (var record : consumer.poll(Duration.ofMillis(250))) {
          values.add(record.key() + "|" + record.value());
          if (values.size() > 4) {
            throw new IllegalStateException("Unexpected records; no reset performed");
          }
        }
      }
    }
    Collections.sort(values);
    return values;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 0) {
      throw new IllegalArgumentException("This bounded probe accepts no arguments");
    }
    ensureTopic();
    produceWhenEmpty();
    var committed = read("read_committed");
    var uncommitted = read("read_uncommitted");
    var expected = List.of(
      "order-1|committed-a",
      "same-business-id|duplicate-business-call",
      "same-business-id|duplicate-business-call"
    );
    if (!committed.equals(expected)) {
      throw new IllegalStateException("Committed records differ: " + committed);
    }
    var expectedAll = new ArrayList<>(expected);
    expectedAll.add("order-2|aborted-b");
    Collections.sort(expectedAll);
    if (!uncommitted.equals(expectedAll)) {
      throw new IllegalStateException("Uncommitted records differ: " + uncommitted);
    }
    System.out.println(
      "{\"schema_version\":1,\"passed\":true,\"committed_records\":3," +
        "\"uncommitted_records\":4,\"aborted_hidden\":true," +
        "\"separate_duplicate_send_calls_retained\":2," +
        "\"configured_cleanup_policy\":\"delete\",\"configured_retention_ms\":-1,\"configured_retention_bytes\":-1}"
    );
  }
}
