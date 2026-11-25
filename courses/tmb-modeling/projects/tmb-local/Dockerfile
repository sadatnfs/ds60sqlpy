# Supply an already qualified native R statistics image. No architecture emulation.
ARG R_BASE_IMAGE
FROM ${R_BASE_IMAGE} AS dependencies
USER root
# The R statistics worker already carries the C, C++ and Fortran toolchain.
# Naming it here keeps the TMB build self-describing; apt leaves present packages as they are.
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ gfortran make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/tmb-project
COPY dependencies.lock.json prepare_dependencies.py ./
ENV MAKEFLAGS=-j1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
RUN python3 prepare_dependencies.py

FROM dependencies AS standalone
COPY models ./models
COPY R ./R
COPY tests ./tests
COPY python ./python
RUN Rscript --vanilla R/compile.R /opt/tmb-project /opt/tmb-models
ENV TMB_BUILD_DIR=/opt/tmb-models
RUN Rscript --vanilla tests/acceptance.R
# Models and dependencies are compiled above as root; the runtime only reads them.
USER 65534:65534
ENTRYPOINT ["Rscript", "--vanilla"]
CMD ["tests/acceptance.R"]
