ARG DS60_PYTHON_IMAGE=python:3.12-slim-bookworm
FROM ${DS60_PYTHON_IMAGE} AS toolchain
RUN apt-get update && apt-get install -y --no-install-recommends g++ make ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
COPY docker/workers/native/releases.lock.json /tmp/native-releases.lock.json
COPY docker/workers/native/install_native.py /tmp/install_native.py
RUN TARGETARCH=${TARGETARCH} python /tmp/install_native.py stan
WORKDIR /opt/cmdstan
RUN printf 'O=1\nPRECOMPILED_HEADERS=true\n' >make/local && make -j2 build
COPY docker/workers/native/probe.stan /opt/cmdstan/probe.stan
RUN make -j1 /opt/cmdstan/probe && chmod -R a+rX /opt/cmdstan
FROM toolchain
ARG TARGETARCH
COPY docker/workers/requirements-stan.${TARGETARCH}.lock /tmp/stan-python.lock
RUN python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/stan-python.lock
ENV CMDSTAN=/opt/cmdstan
WORKDIR /opt/worker
RUN install -d -m 0700 /run/ds60
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py src/ds60sqlpy/stan_runner.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=stan-cpu
ENTRYPOINT ["python", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
