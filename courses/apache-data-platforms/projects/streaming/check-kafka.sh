#!/usr/bin/env bash
set -euo pipefail
export KAFKA_HEAP_OPTS='-Xms32m -Xmx128m'

verify_study_policy() {
  local file=$1
  if ! grep -Eq '^[[:space:]]*cleanup\.policy=delete([[:space:]]|$)' "$file" ||
    ! grep -Eq '^[[:space:]]*retention\.ms=-1([[:space:]]|$)' "$file" ||
    ! grep -Eq '^[[:space:]]*retention\.bytes=-1([[:space:]]|$)' "$file"; then
    echo 'Unexpected actual study-topic retention policy; no data or configuration was reset.' >&2
    return 2
  fi
}

verify_study_topology() {
  local file=$1
  grep -Eq 'PartitionCount:[[:space:]]*2([[:space:]]|$)' "$file" || {
    echo 'Expected actual partition count 2.' >&2
    return 2
  }
  grep -Eq 'ReplicationFactor:[[:space:]]*1([[:space:]]|$)' "$file" || {
    echo 'Expected actual replication factor 1.' >&2
    return 2
  }
  awk '
    {
      partition=""; replicas="";
      for(i=1;i<=NF;i++) {
        if($i=="Partition:") partition=$(i+1);
        if($i=="Replicas:") replicas=$(i+1);
      }
      if(partition!="") {
        if(partition !~ /^[01]$/ || replicas !~ /^[0-9]+$/ || seen[partition]++) bad=1;
        count++;
      }
    }
    END {if(bad || count!=2 || seen[0]!=1 || seen[1]!=1) exit 2}
  ' "$file" || {
    echo 'Actual per-partition replica metadata differs; no fixture was reset.' >&2
    return 2
  }
}

parse_study_offsets() {
  awk -F: '
    NF!=3 || $1!="classroom-events" || $2!~/^[01]$/ || $3!~/^[0-3]$/ {bad=1; next}
    {if(seen[$2]++) bad=1; ends[$2]=$3; count++}
    END {
      if(bad || count!=2 || seen[0]!=1 || seen[1]!=1 || ends[0]+ends[1]>3) exit 2;
      printf "%d %d %d\n",ends[0],ends[1],ends[0]+ends[1];
    }
  ' "$1" || {
    echo 'Unexpected partition end offsets; no fixture was reset.' >&2
    return 2
  }
}

main() {
  local topic=classroom-events kafka=/opt/kafka/bin count end0 end1 source_sha positions
  [[ $# == 0 ]] || {
    echo 'This fixed probe accepts no arguments.' >&2
    return 2
  }
  "$kafka/kafka-topics.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --create --if-not-exists \
    --topic "$topic" --partitions 2 --replication-factor 1 \
    --config cleanup.policy=delete --config retention.ms=-1 --config retention.bytes=-1 \
    >/tmp/topic-check.log 2>&1
  "$kafka/kafka-topics.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --describe --topic "$topic" \
    >/tmp/topic-metadata.log 2>&1
  verify_study_topology /tmp/topic-metadata.log
  "$kafka/kafka-configs.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --entity-type topics \
    --entity-name "$topic" --describe --all >/tmp/topic-policy.log 2>&1
  verify_study_policy /tmp/topic-policy.log
  "$kafka/kafka-get-offsets.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --topic "$topic" --time latest \
    >/tmp/topic-offsets.log
  positions=$(parse_study_offsets /tmp/topic-offsets.log) || return 2
  read -r end0 end1 count <<<"$positions"
  if [[ $count == 0 ]]; then
    "$kafka/kafka-console-producer.sh" --bootstrap-server kafka:9092 --topic "$topic" \
      --reader-property parse.key=true --reader-property 'key.separator=|' \
      --command-property acks=all --command-property enable.idempotence=true \
      --command-property request.timeout.ms=3000 --command-property delivery.timeout.ms=15000 \
      --command-property max.block.ms=10000 \
      </project/events.txt
  elif [[ $count != 3 ]]; then
    echo 'Existing topic differs from the bounded fixture; no reset or deletion performed.' >&2
    return 2
  fi
  "$kafka/kafka-console-consumer.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --topic "$topic" \
    --from-beginning --max-messages 3 --timeout-ms 15000 \
    --formatter-property print.key=true --formatter-property 'key.separator=|' \
    >/tmp/received.txt 2>/tmp/consumer-check.log
  LC_ALL=C sort /project/events.txt >/tmp/expected-sorted.txt
  LC_ALL=C sort /tmp/received.txt >/tmp/received-sorted.txt
  diff -u /tmp/expected-sorted.txt /tmp/received-sorted.txt
  "$kafka/kafka-get-offsets.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --topic "$topic" --time latest \
    >/tmp/topic-offsets.log
  positions=$(parse_study_offsets /tmp/topic-offsets.log) || return 2
  read -r end0 end1 count <<<"$positions"
  [[ $count == 3 ]] || {
    echo 'Expected exactly three persisted source records.' >&2
    return 2
  }
  if "$kafka/kafka-topics.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --create --topic invalid-replication \
    --partitions 1 --replication-factor 2 >/tmp/invalid-topic.log 2>&1; then
    echo 'Unexpected success with replication factor larger than the broker set.' >&2
    return 2
  fi
  grep -Eq 'InvalidReplicationFactorException|Replication factor: 2 larger than available brokers: 1' /tmp/invalid-topic.log || {
    echo 'Topic creation failed for an unexpected reason; inspect retained diagnostics.' >&2
    return 2
  }
  if "$kafka/kafka-topics.sh" --bootstrap-server kafka:9092 --command-config /project/check-client.properties --describe \
    --topic ds60-nonexistent >/tmp/missing-topic.log 2>&1; then
    echo 'Unexpected success for an unknown topic.' >&2
    return 2
  fi
  grep -q 'does not exist' /tmp/missing-topic.log || {
    echo 'Missing-topic check failed for an unexpected reason.' >&2
    return 2
  }
  source_sha=$(sha256sum /project/events.txt | awk '{print $1}')
  [[ $source_sha =~ ^[a-f0-9]{64}$ ]] || {
    echo 'Invalid source SHA256.' >&2
    return 2
  }
  printf '{"schema_version":1,"product":"Apache Kafka","records":3,"partitions":2,"replication_factor":1,"exact_keyed_payloads":true,"invalid_replication_rejected":true,"missing_topic_rejected":true,"configured_cleanup_policy":"delete","configured_retention_ms":-1,"configured_retention_bytes":-1,"source_sha256":"%s","partition_end_offsets":{"0":%s,"1":%s},"passed":true}\n' "$source_sha" "$end0" "$end1"
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then main "$@"; fi
