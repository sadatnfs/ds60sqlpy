ARG BASE_IMAGE=ds60sqlpy-worker-scala-jvm:1.0.0
FROM ${BASE_IMAGE}
USER root
COPY install.py artifact-lock.json /tmp/preparation/
RUN python3 /tmp/preparation/install.py && rm -r /tmp/preparation
ENV FLINK_HOME=/opt/flink FLINK_CONF_DIR=/project/conf PYTHONDONTWRITEBYTECODE=1
WORKDIR /project
USER 1000:1000
ENTRYPOINT ["bash"]
LABEL org.ds60.workshop.kind="apache-flink-binary" org.ds60.upstream.version="2.3.0" \
    org.ds60.upstream.route="official-checksum-verified-binary"
