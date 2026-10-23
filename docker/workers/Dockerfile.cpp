ARG DS60_CPP_IMAGE=gcc:14.3.0-bookworm
FROM ${DS60_CPP_IMAGE}
RUN apt-get update && apt-get install -y --no-install-recommends python3 cmake ninja-build \
    && rm -rf /var/lib/apt/lists/*
# Bookworm apt CMake is 3.25; authored projects require 3.28 or newer.
# Keep the compiler layer cached and add only an image-local CMake environment.
RUN apt-get update && apt-get install -y --no-install-recommends python3-venv \
    && rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
COPY docker/workers/requirements-cmake.${TARGETARCH}.lock /tmp/requirements-cmake.txt
RUN python3 -m venv /opt/cmake \
    && /opt/cmake/bin/python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/requirements-cmake.txt
ENV PATH="/opt/cmake/bin:$PATH"
RUN install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py /opt/worker/src/ds60sqlpy/
COPY courses/cpp/fixtures/ /opt/worker/courses/cpp/fixtures/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=cpp20
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
