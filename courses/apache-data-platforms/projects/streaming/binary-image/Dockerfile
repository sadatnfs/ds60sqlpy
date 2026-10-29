ARG BASE_IMAGE=ds60sqlpy-worker-java21:1.1.0
FROM ${BASE_IMAGE}
USER root
COPY install.py /tmp/install-kafka.py
RUN python3 /tmp/install-kafka.py \
    && rm /tmp/install-kafka.py \
    && mkdir -p /var/lib/kafka/data \
    && chown -R 1000:1000 /var/lib/kafka
USER 1000:1000
LABEL org.ds60.workshop.kind="apache-streaming-binary" \
    org.ds60.upstream.product="Apache Kafka" \
    org.ds60.upstream.version="4.4.0" \
    org.ds60.upstream.route="official-checksum-verified-binary"
