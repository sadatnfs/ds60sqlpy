ARG TORCH_IMAGE=ds60sqlpy-worker-llm-torch-cpu:1.1.0
ARG SPARK_IMAGE=ds60sqlpy-worker-spark-local-python:1.1.0
FROM ${TORCH_IMAGE} AS torch
FROM ${SPARK_IMAGE}
USER root
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY --from=torch /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY courses/advanced-spark-modeling/projects/spark-torch/requirements.lock /tmp/requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/requirements.lock \
    && python -m pip check && rm /tmp/requirements.lock
RUN python -c 'import torch,pandas,pyarrow,scipy,lightning; assert torch.__version__ == "2.9.1+cpu"; assert lightning.__version__ == "2.6.1"'
COPY packages/spark-likelihood/ /opt/ds60-package-source/
RUN cp -a /opt/ds60-package-source /tmp/likelihood-build \
    && SOURCE_DATE_EPOCH=315532800 python -m pip wheel --no-index --no-deps --no-build-isolation \
        --wheel-dir /opt/ds60-wheels /tmp/likelihood-build \
    && python -m pip install --no-index --no-deps --force-reinstall /opt/ds60-wheels/*.whl \
    && rm -rf /tmp/likelihood-build
RUN python -I -m ds60_spark_likelihood.integrations.prepare_spark \
    --archive /opt/spark/python/lib/pyspark.zip --apply >/opt/spark/DS60_PATCHES.json
COPY courses/advanced-spark-modeling/projects/spark-torch/ /opt/spark-torch/
ENV PYTHONPATH=/opt/spark-torch PYTHONDONTWRITEBYTECODE=1 \
    SPARK_LOCAL_IP=127.0.0.1 PYSPARK_PYTHON=/usr/local/bin/python \
    PYSPARK_DRIVER_PYTHON=/usr/local/bin/python OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    HOME=/tmp CUDA_VISIBLE_DEVICES=""
WORKDIR /tmp
USER 65534:65534
ENTRYPOINT ["python", "/opt/spark-torch/runner.py"]
