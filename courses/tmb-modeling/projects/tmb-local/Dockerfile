# Supply an already qualified native R statistics image. No architecture emulation.
ARG R_BASE_IMAGE
FROM ${R_BASE_IMAGE} AS dependencies
USER root
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
ENTRYPOINT ["Rscript", "--vanilla"]
CMD ["tests/acceptance.R"]
