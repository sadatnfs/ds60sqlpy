# The shared Python slim base is Debian 13 slim with the worker's patched
# CPython; Debian's own python3 package (and its unfixed CVEs) is not installed.
ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_PYTHON_IMAGE}
# Debian 13's gcc is GCC 14. Install only the C toolchain and make, then apply
# Debian security updates newer than the pinned base. No Python packages are
# installed, so pip is removed rather than upgraded.
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends gcc libc6-dev make \
    && python -m pip uninstall --yes pip \
    && rm -rf /var/lib/apt/lists/* && install -d -m 0700 /run/ds60 \
    && gcc --version | grep -q " 14\."
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=c17
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
