#!/usr/bin/env bash
set -euo pipefail
mkdir -p /tmp/ds60-java-consumer
javac -proc:none -cp '/opt/kafka/libs/*' -d /tmp/ds60-java-consumer /project/ConsumerProbe.java
exec java -Xms32m -Xmx128m -cp '/tmp/ds60-java-consumer:/opt/kafka/libs/*' ConsumerProbe
