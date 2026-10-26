ARG DS60_R_IMAGE=r-base:4.6.1@sha256:ad9b3bbca751f3ead77704fed4c20246127647b3d567b2bf970b7789e8d7b9a8
FROM ${DS60_R_IMAGE}
RUN apt-get update && apt-get install -y -t unstable --no-install-recommends \
    python3 ca-certificates libcurl4-openssl-dev libssl-dev libxml2-dev libuv1-dev libicu-dev \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 /run/ds60
COPY docker/workers/r/packages.lock.json /tmp/r-packages.lock.json
COPY docker/workers/r/install_packages.py /tmp/install_packages.py
RUN python3 /tmp/install_packages.py && rm /tmp/install_packages.py /tmp/r-packages.lock.json
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py src/ds60sqlpy/worker_figures.R /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=r-statistics
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
