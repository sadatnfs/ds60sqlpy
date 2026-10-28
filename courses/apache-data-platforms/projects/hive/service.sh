#!/usr/bin/env bash
set -euo pipefail
[[ -f /opt/hive/lib/postgres.jar && ! -L /opt/hive/lib/postgres.jar && $(wc -c </opt/hive/lib/postgres.jar) -le 2000000 ]] || exit 2
[[ $(sha256sum /opt/hive/lib/postgres.jar | cut -d ' ' -f 1) == 69020b3bd20984543e817393f2e6c01a890ef2e37a77dd11d6d8508181d079ab ]] || {
  echo 'Pinned JDBC identity differs; no service or schema action occurred.' >&2
  exit 2
}
# A copied config directory is writable; maintained source stays read-only.
mkdir -p /tmp/ds60-hive-conf
cp /opt/hadoop/etc/hadoop/* /tmp/ds60-hive-conf/ 2>/dev/null || true
cp /opt/hive/conf/* /tmp/ds60-hive-conf/ 2>/dev/null || true
cp /workshop-conf/hive-site.xml /tmp/ds60-hive-conf/hive-site.xml
cp /workshop-conf/hive-log4j2.properties /tmp/ds60-hive-conf/hive-log4j2.properties
export HIVE_CONF_DIR=/tmp/ds60-hive-conf
export HADOOP_CONF_DIR=$HIVE_CONF_DIR
export HADOOP_CLIENT_OPTS="${HADOOP_CLIENT_OPTS:--Xms128m -Xmx768m}"
action=${1:?Use a fixed workshop action}
case "$action" in
  initialize | query | negative | explain)
    export HADOOP_CLIENT_OPTS="$HADOOP_CLIENT_OPTS --enable-preview --enable-native-access=ALL-UNNAMED"
    export TERM=dumb
    ;;
esac
case "$action" in
  init-schema)
    # Explicit initialization never upgrades an existing database automatically.
    exec /opt/hive/bin/schematool -dbType postgres -initSchema
    ;;
  verify-schema) exec /opt/hive/bin/schematool -dbType postgres -info ;;
  metastore)
    /opt/hive/bin/schematool -dbType postgres -info
    exec /opt/hive/bin/hive --skiphadoopversion --skiphbasecp --service metastore
    ;;
  hiveserver2)
    export HADOOP_CLASSPATH="/opt/tez/*:/opt/tez/lib/*:${HADOOP_CLASSPATH:-}"
    exec /opt/hive/bin/hive --skiphadoopversion --skiphbasecp --service hiveserver2
    ;;
  initialize)
    exec /opt/hive/bin/beeline -u jdbc:hive2://hiveserver2:10000/default -n hive --silent=true --color=false --showHeader=false --outputformat=tsv2 -e "$(tr '\n' ' ' </project/initialize.hql)"
    ;;
  query)
    exec /opt/hive/bin/beeline -u jdbc:hive2://hiveserver2:10000/default -n hive --silent=true --color=false --showHeader=false --outputformat=tsv2 -e 'SELECT id, region, amount FROM ds60.orders ORDER BY id;'
    ;;
  negative)
    exec /opt/hive/bin/beeline -u jdbc:hive2://hiveserver2:10000/default -n hive --silent=true -e 'SELECT absent_field FROM ds60.orders;'
    ;;
  explain)
    exec /opt/hive/bin/beeline -u jdbc:hive2://hiveserver2:10000/default -n hive --silent=true -e "$(tr '\n' ' ' </project/explain.sql)"
    ;;
  metadata)
    # This separate Java client calls the actual Thrift API without reading Parquet.
    bash /project/verify-metadata.sh /project "${DS60_HIVE_RUNTIME_IMAGE_ID:?Use the fixed launcher}"
    mkdir -p /tmp/ds60-hive-metadata-client
    cp /project/.workshop/metadata-client/classes/MetadataProbe.class /tmp/ds60-hive-metadata-client/MetadataProbe.class
    exec java -cp '/tmp/ds60-hive-metadata-client:/opt/hive/lib/*:/opt/hadoop/share/hadoop/common/*:/opt/hadoop/share/hadoop/common/lib/*:/opt/hadoop/share/hadoop/mapreduce/*:/opt/hadoop/share/hadoop/yarn/*:/opt/hadoop/share/hadoop/yarn/lib/*:/opt/hadoop/share/hadoop/hdfs/*:/opt/hadoop/share/hadoop/hdfs/lib/*' MetadataProbe
    ;;
  *)
    echo 'Unknown fixed service action.' >&2
    exit 2
    ;;
esac
