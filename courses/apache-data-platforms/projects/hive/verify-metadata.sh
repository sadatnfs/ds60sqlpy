#!/usr/bin/env bash
set -euo pipefail
[[ $# == 2 && $2 =~ ^sha256:[a-f0-9]{64}$ ]] || {
  echo 'Use the fixed metadata root and inspected runtime image identity.' >&2
  exit 2
}
root=$1
prepared=$root/.workshop/metadata-client
[[ -d $root && ! -L $root && -d $root/.workshop && ! -L $root/.workshop && -d $prepared && ! -L $prepared && -d $prepared/classes && ! -L $prepared/classes ]] || exit 2
manifest=$prepared/identity.tsv
source=$root/MetadataProbe.java
compiled=$prepared/classes/MetadataProbe.class
for file in "$manifest" "$source" "$compiled"; do
  [[ -f $file && ! -L $file && $(wc -c <"$file") -le 1000000 ]] || {
    echo 'Metadata identity requires bounded regular files.' >&2
    exit 2
  }
done
[[ $(wc -c <"$manifest") -le 4096 ]] || exit 2
schema='' hive='' java='' source_hash='' class_hash=''
while IFS=$'\t' read -r key value; do
  case "$key" in
    schema_version)
      [[ -z $schema && $value == 1 ]] || exit 2
      schema=$value
      ;;
    hive_image_id)
      [[ -z $hive && $value =~ ^sha256:[a-f0-9]{64}$ ]] || exit 2
      hive=$value
      ;;
    java_image_id)
      [[ -z $java && $value =~ ^sha256:[a-f0-9]{64}$ ]] || exit 2
      java=$value
      ;;
    source_sha256)
      [[ -z $source_hash && $value =~ ^[a-f0-9]{64}$ ]] || exit 2
      source_hash=$value
      ;;
    class_sha256)
      [[ -z $class_hash && $value =~ ^[a-f0-9]{64}$ ]] || exit 2
      class_hash=$value
      ;;
    *)
      echo 'Unknown metadata identity field.' >&2
      exit 2
      ;;
  esac
done <"$manifest"
[[ $schema == 1 && -n $java && $hive == "$2" && -n $source_hash && -n $class_hash ]] || {
  echo 'Metadata runtime image identity differs.' >&2
  exit 2
}
# One canonical representation rejects truncation, duplicate keys and hidden fields.
expected=$(printf 'schema_version\t1\nhive_image_id\t%s\njava_image_id\t%s\nsource_sha256\t%s\nclass_sha256\t%s\n' "$hive" "$java" "$source_hash" "$class_hash")
[[ $(cat "$manifest") == "$expected" ]] || exit 2
[[ $(find "$prepared/classes" -mindepth 1 -maxdepth 1 | wc -l) -eq 1 ]] || exit 2
[[ $(sha256sum "$source" | cut -d ' ' -f 1) == "$source_hash" && $(sha256sum "$compiled" | cut -d ' ' -f 1) == "$class_hash" ]] || {
  echo 'Prepared metadata source/class identity differs; no execution occurred.' >&2
  exit 2
}
