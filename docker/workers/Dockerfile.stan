ARG DS60_PYTHON_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_PYTHON_IMAGE} AS toolchain
# Apply Debian security updates newer than the pinned base image.
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends g++ make ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
COPY docker/workers/native/releases.lock.json /tmp/native-releases.lock.json
COPY docker/workers/native/install_native.py /tmp/install_native.py
RUN TARGETARCH=${TARGETARCH} python /tmp/install_native.py stan
WORKDIR /opt/cmdstan
RUN printf 'O=1\nPRECOMPILED_HEADERS=true\n' >make/local && make -j2 build
COPY docker/workers/native/probe.stan /opt/cmdstan/probe.stan
RUN make -j1 /opt/cmdstan/probe && chmod -R a+rX /opt/cmdstan
# Learner compiles: hide GCC's informational arm64 ABI notes ("parameter passing
# ... changed in GCC 10.1"), about 20 KB printed before any real error.
RUN printf 'CXXFLAGS += -Wno-psabi\n' >>make/local
FROM toolchain
ARG TARGETARCH
COPY docker/workers/requirements-stan.${TARGETARCH}.lock /tmp/stan-python.lock
COPY requirements/bootstrap-pip.lock /tmp/bootstrap-pip.lock
# Optional anonymous mirror for restricted networks; locked hashes are still required.
# pip is upgraded for the locked install, then removed because nothing uses it at run time.
ARG DS60_PYTHON_INDEX_URL
RUN python -m pip install ${DS60_PYTHON_INDEX_URL:+--index-url "$DS60_PYTHON_INDEX_URL"} --no-cache-dir \
    --require-hashes -r /tmp/bootstrap-pip.lock && rm /tmp/bootstrap-pip.lock
RUN python -m pip install ${DS60_PYTHON_INDEX_URL:+--index-url "$DS60_PYTHON_INDEX_URL"} --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/stan-python.lock \
    && python -m pip uninstall --yes pip
ENV CMDSTAN=/opt/cmdstan
WORKDIR /opt/worker
RUN install -d -m 0700 /run/ds60
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py src/ds60sqlpy/stan_runner.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=stan-cpu
ENTRYPOINT ["python", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
