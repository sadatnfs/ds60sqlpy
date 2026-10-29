ARG BASE_IMAGE=ds60sqlpy-worker-scala-jvm:1.1.0
FROM ${BASE_IMAGE}
USER root
COPY install.py /tmp/install-pinot.py
RUN python3 /tmp/install-pinot.py && rm /tmp/install-pinot.py
ENV PINOT_HOME=/opt/pinot LOG_DIR=/tmp/pinot-logs PINOT_LOG_DIR=/tmp/pinot-logs
LABEL org.ds60.workshop.kind="apache-pinot-binary" \
    org.ds60.upstream.product="Apache Pinot" org.ds60.upstream.version="1.5.1" \
    org.ds60.upstream.route="official-checksum-verified-binary"
WORKDIR /opt/pinot
ENTRYPOINT ["/opt/pinot/bin/pinot-admin.sh"]
