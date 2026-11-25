ARG DS60_PHP_IMAGE=php:8.4.28-cli-trixie@sha256:6b13a8678b38ca38e4e3950be57b664ed8c8706131a0586111f68792aede4c58
ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_PYTHON_IMAGE} AS python
FROM ${DS60_PHP_IMAGE}
# The worker needs only the Python standard library. Copy the patched upstream
# CPython instead of installing Debian python3, which carries its own CVE backlog.
COPY --from=python /usr/local/bin/python3.12 /usr/local/bin/python3.12
COPY --from=python /usr/local/lib/libpython3.12.so.1.0 /usr/local/lib/libpython3.12.so.1.0
COPY --from=python /usr/local/lib/python3.12 /usr/local/lib/python3.12
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y \
    && ln -s python3.12 /usr/local/bin/python3 \
    && rm -rf /usr/local/lib/python3.12/site-packages/* /usr/local/lib/python3.12/ensurepip \
    && ldconfig \
    && python3 -c "import json, sqlite3, ssl, http.server" \
    && php -r "exit(extension_loaded('pdo_sqlite') ? 0 : 1);" \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=php-cli
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
