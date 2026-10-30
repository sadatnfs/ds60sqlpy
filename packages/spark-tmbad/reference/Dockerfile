# Build context is this optional reference directory, independently of the classroom.
ARG R_BASE_IMAGE=r-base:4.6.1@sha256:ad9b3bbca751f3ead77704fed4c20246127647b3d567b2bf970b7789e8d7b9a8
FROM ${R_BASE_IMAGE}
USER root
ARG PREPARED_OS_PACKAGES=0
RUN if [ "$PREPARED_OS_PACKAGES" = 0 ]; then \
      apt-get update && apt-get install -y --no-install-recommends \
        python3 g++ gfortran make cmake pkg-config libnlopt-dev libicu-dev \
        libcurl4-openssl-dev libssl-dev libxml2-dev libblas-dev liblapack-dev ca-certificates \
      && rm -rf /var/lib/apt/lists/*; \
    elif [ "$PREPARED_OS_PACKAGES" != 1 ]; then exit 2; fi
WORKDIR /opt/reference
COPY . /opt/reference/
ENV MAKEFLAGS=-j1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    R_LIBS_USER=/opt/reference-prepared/library R_LIBS_SITE=/opt/reference-prepared/library \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN python3 prepare.py --output /opt/reference-prepared --allow-download \
    && Rscript --vanilla tests/pure.R /opt/reference \
    && chmod -R a+rX /opt/reference /opt/reference-prepared \
    && mkdir /work && chown 65534:65534 /work
WORKDIR /work
USER 65534:65534
ENTRYPOINT ["python3", "/opt/reference/python/client.py"]
CMD ["--list"]
