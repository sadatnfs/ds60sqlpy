# Hive apache-067 command notebook

Both files are read-only here. `iceberg.hql` creates `ds60.orders_iceberg` at `file:///warehouse/orders_iceberg` and inserts the three orders, while `conf/hive-site.xml` shows the catalog settings that statement would depend on in the copied Hive project.

```bash
cat iceberg.hql
cat conf/hive-site.xml
```

This is a prepared Iceberg extension, not an executed default reference. Prepare and test the exact bundled Hive integration, metadata/snapshot identity and second reader before asserting cross-engine compatibility.

QUALIFICATION.md lists Iceberg integration among the Hive extensions that the default Parquet and Thrift path does not qualify. Its receipt needs the metadata file, the snapshot ID and a second engine reading that same snapshot.