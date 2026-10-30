# Build context is this package directory. The base images must be prepared first.
ARG CPP_IMAGE=ds60sqlpy-worker-cpp20:1.1.0
ARG SPARK_IMAGE=ds60sqlpy-worker-spark-local-python:1.1.0
FROM ${CPP_IMAGE} AS native
USER root
WORKDIR /src
COPY native /src/native
COPY tooling /src/tooling
# This explicit image preparation stage downloads only SHA256-pinned source.
# For offline preparation, use the separate tooling/README.md command sequence.
RUN python3 tooling/prepare.py --destination /tmp/tmbad-sdk --allow-download \
    && python3 tooling/build_native.py --sdk /tmp/tmbad-sdk --output /tmp/tmbad-native --compiler g++-12

FROM ${SPARK_IMAGE} AS jvm
USER root
COPY jvm /src/jvm
COPY python /src/python
COPY tooling/python-build-requirements.txt /src/python-build-requirements.txt
RUN python3 -m pip install --require-hashes -r /src/python-build-requirements.txt \
    && python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/wheels /src/python
RUN python3 /src/jvm/build.py --spark-home /opt/spark --output /tmp/spark-tmbad.jar

FROM ${SPARK_IMAGE}
USER root
COPY native /src/native
COPY tooling /src/tooling
COPY jvm /src/jvm
COPY python /src/python
COPY docs /src/docs
COPY studies /src/studies
COPY LICENSE README.md AGENTS.md /src/
COPY --from=native /tmp/tmbad-native /tmp/tmbad-native
COPY --from=native /tmp/tmbad-sdk /tmp/tmbad-sdk
COPY --from=jvm /tmp/spark-tmbad.jar /tmp/spark-tmbad.jar
COPY --from=jvm /tmp/spark-tmbad.jar.json /tmp/spark-tmbad.jar.json
COPY --from=jvm /tmp/wheels /tmp/wheels
RUN python3 /src/tooling/assemble.py --native-build /tmp/tmbad-native --sdk /tmp/tmbad-sdk \
      --jar /tmp/spark-tmbad.jar --output /opt/spark-tmbad \
    && python3 -m pip install --no-index --no-deps /tmp/wheels/ds60_spark_tmbad-*.whl \
    && /opt/spark-tmbad/tmbad-worker --describe >/opt/spark-tmbad/runtime-description.json \
    && python3 -c 'from ds60_spark_tmbad import PreparedRuntime; PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")' \
    && rm -rf /tmp/tmbad-native /tmp/tmbad-sdk /tmp/wheels /tmp/spark-tmbad.jar /tmp/spark-tmbad.jar.json
RUN mkdir -p /work && chown 65534:65534 /work
ENV SPARK_TMBAD_MANIFEST=/opt/spark-tmbad/artifact.json \
    JAVA_TOOL_OPTIONS=-Duser.home=/tmp
WORKDIR /work
USER 65534:65534
HEALTHCHECK NONE
# Pass the user's Spark application explicitly; never start a cluster on import.
ENTRYPOINT ["/opt/spark/bin/spark-submit", "--jars", "/opt/spark-tmbad/spark-tmbad.jar"]
CMD ["--help"]
