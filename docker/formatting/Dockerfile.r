# Build from the repository root. Only the shared locked R tool inputs are copied.
# Keep the R image separate from the Ubuntu formatting image to preserve its ABI.
ARG DS60_R_IMAGE=r-base:4.6.1@sha256:ad9b3bbca751f3ead77704fed4c20246127647b3d567b2bf970b7789e8d7b9a8
FROM ${DS60_R_IMAGE}
RUN apt-get update && apt-get install -y -t unstable --no-install-recommends \
    python3 ca-certificates libcurl4-openssl-dev libssl-dev libxml2-dev libuv1-dev libicu-dev \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 /run/ds60
COPY docker/workers/r/packages.lock.json /tmp/r-packages.lock.json
COPY docker/workers/r/install_packages.py /tmp/install_packages.py
RUN python3 /tmp/install_packages.py && rm /tmp/install_packages.py /tmp/r-packages.lock.json
RUN Rscript --vanilla -e 'stopifnot(as.character(packageVersion("styler")) == "1.11.0", as.character(packageVersion("lintr")) == "3.4.0")'
WORKDIR /workspace
CMD ["python3", "scripts/format_repo.py", "--check", "--language", "r"]
