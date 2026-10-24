ARG DS60_GO_IMAGE=golang:1.27.3-bookworm@sha256:972b4110ba0f47539a975c31e52c64765e1ff19f2d74469ae4a595c6676e80a5
FROM ${DS60_GO_IMAGE}
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/* && install -d -m 0700 /run/ds60
# Compile the standard library once. Jobs read immutable exports and never run
# a package manager, fetch a module or rebuild a writable shared cache.
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOMAXPROCS=2 GOCACHE=/opt/go-cache
RUN mkdir -p /opt/course-go \
    && go list -export -f '{{if .Export}}packagefile {{.ImportPath}}={{.Export}}{{end}}' std > /opt/course-go/importcfg \
    && test -s /opt/course-go/importcfg && chmod -R a+rX /opt/course-go /opt/go-cache
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=go
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
