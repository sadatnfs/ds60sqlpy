# Standalone context: this package directory only. No classroom image is required.
ARG PYTHON_IMAGE=python:3.12.12-slim-bookworm
ARG SPARK_IMAGE=spark:4.0.1-scala2.13-java17-python3-ubuntu
FROM ${SPARK_IMAGE} AS spark-distribution

FROM ${PYTHON_IMAGE} AS runtime-base
USER root
ARG TARGETARCH
ARG PREPARED_OS_PACKAGES=0
RUN case "$PREPARED_OS_PACKAGES" in \
      0) apt-get update && apt-get install -y --no-install-recommends \
           openjdk-17-jdk-headless libgomp1 ca-certificates \
           && rm -rf /var/lib/apt/lists/* ;; \
      1) java -version ;; \
      *) exit 2 ;; esac
COPY --from=spark-distribution /opt/spark /opt/spark
ENV SPARK_HOME=/opt/spark \
    PATH=/opt/spark/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHONPATH="" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYSPARK_PYTHON=/usr/local/bin/python3 PYSPARK_DRIVER_PYTHON=/usr/local/bin/python3 \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" \
    PIP_DISABLE_PIP_VERSION_CHECK=1
FROM runtime-base AS dependencies
ARG TARGETARCH
ARG PREPARED_PYTHON_PACKAGES=0
ARG OFFLINE_PYTHON=0
COPY tooling /opt/spark-likelihood-tooling
RUN case "$PREPARED_PYTHON_PACKAGES:$OFFLINE_PYTHON" in \
      0:0) preparation_flags="" ;; \
      0:1) preparation_flags="--offline" ;; \
      1:0|1:1) preparation_flags="--prepared" ;; \
      *) exit 2 ;; esac \
    && python3 /opt/spark-likelihood-tooling/install_dependencies.py \
         --architecture "$TARGETARCH" --group cpu $preparation_flags \
    && python3 /opt/spark-likelihood-tooling/install_dependencies.py \
         --architecture "$TARGETARCH" --group scientific $preparation_flags \
    && python3 -m pip check

FROM dependencies AS wheel-builder
ARG TARGETARCH
ARG OFFLINE_PYTHON=0
RUN case "$OFFLINE_PYTHON" in \
      0) preparation_flags="" ;; 1) preparation_flags="--offline" ;; *) exit 2 ;; esac \
    && python3 /opt/spark-likelihood-tooling/install_dependencies.py \
         --architecture "$TARGETARCH" --group build $preparation_flags
COPY . /src/package
RUN python3 /src/package/tooling/build_wheel.py --output /opt/spark-likelihood-wheels

FROM runtime-base
USER root
COPY --from=dependencies /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=dependencies /usr/local/bin/ /usr/local/bin/
COPY LICENSE README.md AGENTS.md MANIFEST.in pyproject.toml /opt/spark-likelihood/
COPY src /opt/spark-likelihood/src
COPY docs /opt/spark-likelihood/docs
COPY examples /opt/spark-likelihood/examples
COPY tests /opt/spark-likelihood/tests
COPY integration /opt/spark-likelihood/integration
COPY tooling/*.py tooling/*.md tooling/lock-provenance.json /opt/spark-likelihood/tooling/
COPY tooling/locks /opt/spark-likelihood/tooling/locks
COPY tooling/tests /opt/spark-likelihood/tooling/tests
COPY --from=wheel-builder /opt/spark-likelihood-wheels /opt/spark-likelihood-wheels
RUN python3 -m pip install --no-index --no-deps --force-reinstall /opt/spark-likelihood-wheels/*.whl \
    && python3 /opt/spark-likelihood/tooling/prepare_environment.py \
         --spark-home /opt/spark --apply --output /opt/spark-likelihood/preparation.json \
    && python3 /opt/spark-likelihood/tooling/check_environment.py \
         --output /opt/spark-likelihood/environment.json \
    && python3 -m pip check \
    && python3 -I -c 'import ds60_spark_likelihood; print(ds60_spark_likelihood.__version__)'
RUN mkdir -p /work && chown 65534:65534 /work
ENV JAVA_TOOL_OPTIONS=-Duser.home=/tmp
WORKDIR /work
USER 65534:65534
HEALTHCHECK NONE
ENTRYPOINT ["/opt/spark/bin/spark-submit"]
CMD ["--help"]
