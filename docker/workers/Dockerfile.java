ARG DS60_JAVA_IMAGE=eclipse-temurin:21-jdk-jammy@sha256:432e54724c3e57d1846aeb886f4d339f3b0522931c4e64119c2797013b7cfc3c
ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
FROM ${DS60_JAVA_IMAGE} AS java
FROM ${DS60_PYTHON_IMAGE}
COPY --from=java /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk PATH="/opt/java/openjdk/bin:$PATH"
# H2 is an embedded, in-process JDBC engine for offline transaction lessons.
# Download only during image build; the SHA256 is pinned from Maven Central.
COPY docker/workers/fetch_pinned.py /tmp/fetch_pinned.py
RUN python /tmp/fetch_pinned.py https://repo.maven.apache.org/maven2/com/h2database/h2/2.5.252/h2-2.5.252.jar 90b11dc413da82070ef15fc943282c1408e6ffd34fa68998335fea8603b5ff20 /opt/course-libs/h2-2.5.252.jar && rm /tmp/fetch_pinned.py
RUN java -version && javac -version && install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=java21
ENTRYPOINT ["python", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
