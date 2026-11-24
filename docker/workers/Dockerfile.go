ARG DS60_GO_IMAGE=golang:1.27.4-trixie@sha256:f18c3d73a184fb0582828510722e723b63a93f7188d11dd223d9be6f6880e65d
ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_GO_IMAGE} AS go
FROM ${DS60_PYTHON_IMAGE}
# Only the Go distribution is copied onto the shared Debian 13 Python slim base;
# the SDK image's compilers, VCS tools and headers are not needed because jobs
# build with CGO disabled. No Python packages are installed, so pip is removed.
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall --yes pip && install -d -m 0700 /run/ds60
COPY --from=go /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:$PATH"
# Compile the standard library once. Jobs read immutable exports and never run
# a package manager, fetch a module or rebuild a writable shared cache.
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOMAXPROCS=2 GOCACHE=/opt/go-cache
RUN mkdir -p /opt/course-go \
    && go list -export -f '{{if .Export}}packagefile {{.ImportPath}}={{.Export}}{{end}}' std >/opt/course-go/importcfg \
    && test -s /opt/course-go/importcfg && chmod -R a+rX /opt/course-go /opt/go-cache
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=go
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
