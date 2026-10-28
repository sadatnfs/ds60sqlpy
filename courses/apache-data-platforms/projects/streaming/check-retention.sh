#!/usr/bin/env bash
set -euo pipefail
mkdir -p /tmp/ds60-retention-client
javac -proc:none -cp '/opt/kafka/libs/*' -d /tmp/ds60-retention-client \
  /project/RetentionSemantics.java /project/RetentionProbe.java
exec java -Xms32m -Xmx128m -cp '/tmp/ds60-retention-client:/opt/kafka/libs/*' RetentionProbe
