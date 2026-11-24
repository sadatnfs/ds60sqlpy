ARG DS60_JAVA_IMAGE=eclipse-temurin:21-jdk-noble@sha256:a09e64f4976df9c4f2029c6abe64fc26f069a342ec9a7f147dce7b1933ebda16
ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_JAVA_IMAGE} AS java
FROM ${DS60_PYTHON_IMAGE}
# Apply Debian security updates newer than the pinned base image.
# This image installs no Python packages, so pip is removed rather than upgraded.
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall --yes pip
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
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
