ARG BASE_IMAGE=ds60sqlpy-worker-llm-torch-cpu:1.3.0
FROM ${BASE_IMAGE}
USER root
COPY requirements.lock /tmp/inference-requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/inference-requirements.lock
WORKDIR /opt/inference
COPY serving_*.py server.py prepare.py check_model.py corpus.txt index.html app.js style.css ./
ENV PYTHONDONTWRITEBYTECODE=1 HOME=/tmp CUDA_VISIBLE_DEVICES=""
USER 65534:65534
ENTRYPOINT ["python", "-m", "uvicorn", "server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--no-access-log", "--timeout-keep-alive", "5", "--timeout-graceful-shutdown", "20", "--limit-concurrency", "24", "--h11-max-incomplete-event-size", "16384"]
