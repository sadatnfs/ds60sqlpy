ARG DS60_SWIFT_IMAGE=swift:6.3.3-noble@sha256:4f42306306fe7e5a773a8d47d7e2a24dc3a975d1feb77996297ecfd7c329b1e9
FROM ${DS60_SWIFT_IMAGE}
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/* && install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=swift-linux
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
