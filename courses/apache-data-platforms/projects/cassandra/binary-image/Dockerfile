ARG BASE_IMAGE=ds60sqlpy-worker-scala-jvm:1.0.1
FROM ${BASE_IMAGE}
ARG TARGETARCH
USER root
COPY install.py /tmp/install-cassandra.py
COPY requirements.amd64.lock requirements.arm64.lock /tmp/cassandra-locks/
RUN python3 /tmp/install-cassandra.py \
    && python3 -m pip install --no-cache-dir --only-binary=:all: --require-hashes \
        -r /tmp/cassandra-locks/requirements.${TARGETARCH}.lock \
    && rm -rf /tmp/install-cassandra.py /tmp/cassandra-locks
RUN apt-get update && apt-get install -y --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*
ENV CASSANDRA_HOME=/opt/cassandra CASSANDRA_CONF=/tmp/cassandra-conf \
    CASSANDRA_LOG_DIR=/state/logs MAX_HEAP_SIZE=768M MAX_DIRECT_MEMORY_SIZE=256M \
    HOME=/tmp/home
LABEL org.ds60.workshop.kind="apache-cassandra-binary" \
    org.ds60.upstream.product="Apache Cassandra" org.ds60.upstream.version="5.0.9" \
    org.ds60.upstream.route="official-checksum-verified-binary"
USER 1000:1000
