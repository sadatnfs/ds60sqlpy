ARG BASE_IMAGE=ds60sqlpy-worker-scala-jvm:2.1.0
FROM ${BASE_IMAGE}
USER root
COPY install.py /tmp/install-pinot.py
RUN python3 /tmp/install-pinot.py && rm /tmp/install-pinot.py
ENV PINOT_HOME=/opt/pinot LOG_DIR=/tmp/pinot-logs PINOT_LOG_DIR=/tmp/pinot-logs
LABEL org.ds60.workshop.kind="apache-pinot-binary" \
    org.ds60.upstream.product="Apache Pinot" org.ds60.upstream.version="1.5.1" \
    org.ds60.upstream.route="official-checksum-verified-binary"
WORKDIR /opt/pinot
# Pinot runs as the unprivileged nobody account. The state and staging mount
# points are owned by it so new named volumes inherit a writable owner; the
# tmpfs config and data mounts in compose.yaml default to mode 1777.
RUN install -d -o 65534 -g 65534 -m 0750 /state /staging
USER 65534:65534
ENTRYPOINT ["/opt/pinot/bin/pinot-admin.sh"]
