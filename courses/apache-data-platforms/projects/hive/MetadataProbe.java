import java.util.List;
import org.apache.hadoop.hive.conf.HiveConf;
import org.apache.hadoop.hive.metastore.HiveMetaStoreClient;
import org.apache.hadoop.hive.metastore.api.FieldSchema;
import org.apache.hadoop.hive.metastore.api.Partition;
import org.apache.hadoop.hive.metastore.api.Table;

/** Actual independent Thrift metadata read. It does not query data files. */
public final class MetadataProbe {

  static boolean fields(List<FieldSchema> actual, List<String> names, List<String> types) {
    if (actual.size() != names.size()) return false;
    for (int i = 0; i < names.size(); i++) {
      if (
        !actual.get(i).getName().equals(names.get(i)) ||
        !actual.get(i).getType().equals(types.get(i))
      ) return false;
    }
    return true;
  }

  public static void main(String[] args) throws Exception {
    HiveConf conf = new HiveConf();
    conf.set("hive.metastore.uris", "thrift://metastore:9083");
    conf.set("hive.metastore.client.socket.timeout", "10s");
    try (HiveMetaStoreClient client = new HiveMetaStoreClient(conf)) {
      Table table = client.getTable("ds60", "orders");
      List<String> names = List.of("id", "region", "amount");
      List<String> types = List.of("int", "string", "int");
      if (
        !table.getDbName().equals("ds60") ||
        !table.getTableName().equals("orders") ||
        !table.getTableType().equals("EXTERNAL_TABLE") ||
        !table.getSd().getLocation().equals("file:/warehouse/orders") ||
        !fields(table.getSd().getCols(), names, types) ||
        !fields(table.getPartitionKeys(), List.of("day"), List.of("string")) ||
        !client.listPartitionNames("ds60", "orders", (short) 10).equals(List.of("day=2026-01-01"))
      ) {
        throw new IllegalStateException("Retained Thrift table schema/partition contract differs");
      }
      Partition partition = client.getPartition("ds60", "orders", List.of("2026-01-01"));
      if (
        !partition.getValues().equals(List.of("2026-01-01")) ||
        !partition.getSd().getLocation().equals("file:/warehouse/orders/day=2026-01-01") ||
        !fields(partition.getSd().getCols(), names, types)
      ) {
        throw new IllegalStateException("Retained Thrift partition identity differs");
      }
      boolean rejected = false;
      try {
        client.getTable("ds60", "absent_owned_table");
      } catch (org.apache.hadoop.hive.metastore.api.NoSuchObjectException expected) {
        rejected = true;
      }
      if (!rejected) throw new IllegalStateException("Missing table did not fail");
      System.out.println(
        "{\"passed\":true,\"actual_thrift_metadata\":true,\"columns\":3,\"partitions\":1,\"data_files_read\":false,\"missing_table_rejected\":true,\"typed_schema_checked\":true,\"partition_identity_checked\":true}"
      );
    }
  }
}
