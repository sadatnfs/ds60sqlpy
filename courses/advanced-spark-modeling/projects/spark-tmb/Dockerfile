# Build only from already prepared native images. Runtime never downloads packages.
ARG TMB_IMAGE=ds60-tmb-local:dev-1.9.25
ARG SPARK_IMAGE=ds60sqlpy-worker-spark-local-python:1.1.0
ARG JAVA_IMAGE=ds60sqlpy-worker-java21:1.1.0
FROM ${SPARK_IMAGE} AS spark
FROM ${JAVA_IMAGE} AS java
FROM ${TMB_IMAGE} AS prepared
USER root
COPY --from=spark /usr/local/ /usr/local/
COPY --from=spark /opt/spark/ /opt/spark/
COPY --from=java /opt/java/openjdk/ /opt/java/openjdk/
ENV JAVA_HOME=/opt/java/openjdk PATH="/opt/java/openjdk/bin:/usr/local/bin:$PATH" \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/lib/R/lib SPARK_HOME=/opt/spark \
    PYSPARK_PYTHON=/usr/local/bin/python PYSPARK_DRIVER_PYTHON=/usr/local/bin/python \
    SPARK_LOCAL_IP=127.0.0.1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MAKEFLAGS=-j1 \
    PYTHONDONTWRITEBYTECODE=1 HOME=/tmp TMB_PROJECT_ROOT=/opt/tmb-project \
    TMB_BUILD_DIR=/opt/tmb-models
RUN python -c 'import ctypes,ssl,sys; assert sys.version_info[:2] == (3,12); ctypes.CDLL("/usr/lib/R/lib/libR.so")' \
    && java -version && Rscript --vanilla -e 'stopifnot(as.character(getRversion()) == "4.6.1", as.character(packageVersion("TMB")) == "1.9.25")'
COPY courses/advanced-spark-modeling/projects/spark-tmb/bootstrap.lock /tmp/bootstrap.lock
COPY courses/advanced-spark-modeling/projects/spark-tmb/requirements.lock /tmp/requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/bootstrap.lock \
    && RPY2_CFFI_MODE=ABI python -m pip install --no-cache-dir --require-hashes --no-build-isolation -r /tmp/requirements.lock \
    && python -m pip check
# Install only the reusable pure core wheel; this R reference does not need Torch.
COPY packages/spark-likelihood/ /opt/ds60-package-source/
RUN cp -a /opt/ds60-package-source /tmp/likelihood-build \
    && SOURCE_DATE_EPOCH=315532800 python -m pip wheel --no-index --no-deps --no-build-isolation \
       --wheel-dir /opt/ds60-wheels /tmp/likelihood-build \
    && python -m pip install --no-index --no-deps --force-reinstall /opt/ds60-wheels/*.whl \
    && python -I -c 'import pathlib,sys,ds60_spark_likelihood as package; assert "site-packages" in pathlib.Path(package.__file__).parts; assert not any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules); assert "torch" not in sys.modules' \
    && rm -rf /tmp/likelihood-build
COPY courses/tmb-modeling/projects/tmb-local/ /opt/tmb-project/
WORKDIR /opt/tmb-project
RUN Rscript --vanilla R/compile.R /opt/tmb-project /opt/tmb-models \
    && Rscript --vanilla tests/acceptance.R \
    && python tests/bridge_acceptance.py
FROM prepared
COPY courses/advanced-spark-modeling/projects/spark-tmb/ /opt/spark-tmb/
COPY courses/tmb-modeling/projects/tmb-cpp-api/ /opt/tmb-cpp-api/
ENV PYTHONPATH=/opt/spark-tmb SPARK_TMB_BUILD_DIR=/opt/spark-tmb-models RPY2_CFFI_MODE=ABI
RUN python /opt/spark-tmb/prepare_models.py /opt/spark-tmb-models \
    && chmod -R a+rX /opt/tmb-project /opt/tmb-models /opt/spark-tmb /opt/spark-tmb-models /opt/tmb-cpp-api /opt/ds60-package-source /opt/ds60-wheels
WORKDIR /tmp
USER 65534:65534
ENTRYPOINT ["python", "/opt/spark-tmb/runner.py"]
