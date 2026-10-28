#!/usr/bin/env bash
set -euo pipefail
mkdir -p /tmp/ds60-java-client
javac -proc:none -cp '/opt/kafka/libs/*' -d /tmp/ds60-java-client /project/TransactionProbe.java
exec java -Xms32m -Xmx128m -cp '/tmp/ds60-java-client:/opt/kafka/libs/*' TransactionProbe
