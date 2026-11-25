# The official Swift image on Amazon Linux 2023 carries the same 6.3.3 toolchain
# as the Ubuntu image with a much smaller OS package set: no Ubuntu kernel
# headers or their open advisories. Its python3 is 3.9, so the worker runs on
# the distribution's python3.12; the healthcheck's stdlib call works with either.
ARG DS60_SWIFT_IMAGE=swift:6.3.3-amazonlinux2023@sha256:d5cb8e6ef1810f6b13bd36cd03f1cd1bda2f742fabcca959fc5fb0c0ccb39ba8
FROM ${DS60_SWIFT_IMAGE}
# --releasever=latest applies Amazon Linux security updates newer than the
# image's locked repository snapshot, like apt-get upgrade on the Debian workers.
# hadolint ignore=DL3041
RUN dnf -y upgrade --releasever=latest \
    && dnf -y install --releasever=latest python3.12 \
    && dnf clean all && rm -rf /var/cache/dnf \
    && install -d -m 0700 /run/ds60 \
    && python3.12 -c 'import sys; assert sys.version_info[:2] == (3, 12)' \
    && command -v stdbuf
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=swift-linux
ENTRYPOINT ["python3.12", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
