# Rocker builds R 4.6.1 from source on Ubuntu LTS, a stable and scannable base; the
# locked CRAN closure targets R 4.6.1, which Debian stable does not package.
ARG DS60_R_IMAGE=rocker/r-ver:4.6.1@sha256:780bc87219250a6dfffef6c812999731986fd94d8d5f7e572d1157c923d1b4bb
FROM ${DS60_R_IMAGE}
# hadolint ignore=DL3005,DL3008
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    python3 ca-certificates g++ gcc gfortran make libcurl4-openssl-dev libssl-dev libxml2-dev libuv1-dev libicu-dev \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 /run/ds60
COPY docker/workers/r/packages.lock.json /tmp/r-packages.lock.json
COPY docker/workers/r/install_packages.py /tmp/install_packages.py
# The C, C++ and Fortran compilers, make and the C headers stay installed: learners
# build and install local source packages (R CMD INSTALL, Rcpp, cpp11) into a per-job
# library, and the classroom qualification proves that path. The worker stays offline.
# The openssl package's vignette embeds sample private keys that secret scans flag.
RUN python3 /tmp/install_packages.py && rm /tmp/install_packages.py /tmp/r-packages.lock.json \
    && rm -rf /usr/local/lib/R/site-library/openssl/doc \
    && Rscript --vanilla -e 'invisible(lapply(rownames(installed.packages(lib.loc = .libPaths()[1])), loadNamespace))'
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py src/ds60sqlpy/worker_figures.R /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=r-statistics
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
