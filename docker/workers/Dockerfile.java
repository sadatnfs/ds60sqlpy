ARG DS60_JAVA_IMAGE=eclipse-temurin:21-jdk-jammy@sha256:742daacb9316be4b6fc60258f6e4ac2a11882f6c597373c92290a57bfad0d2e0
ARG DS60_PYTHON_IMAGE=python:3.12.12-slim-bookworm
FROM ${DS60_JAVA_IMAGE} AS java
FROM ${DS60_PYTHON_IMAGE}
COPY --from=java /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk PATH="/opt/java/openjdk/bin:$PATH"
# H2 is an embedded, in-process JDBC engine for offline transaction lessons.
# Download only during image build; the SHA256 is pinned from Maven Central.
RUN python -c "import hashlib,pathlib,urllib.request; u='https://repo.maven.apache.org/maven2/com/h2database/h2/2.5.252/h2-2.5.252.jar'; d=urllib.request.urlopen(u,timeout=60).read(); assert hashlib.sha256(d).hexdigest()=='90b11dc413da82070ef15fc943282c1408e6ffd34fa68998335fea8603b5ff20'; p=pathlib.Path('/opt/course-libs'); p.mkdir(); (p/'h2-2.5.252.jar').write_bytes(d)"
RUN java -version && javac -version && install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=java21
ENTRYPOINT ["python", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
