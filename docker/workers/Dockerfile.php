ARG DS60_PHP_IMAGE=php:8.4.27-cli-bookworm@sha256:496b5e02fe9fe44fcfb715023b931048111dc4e0bc719789d83c906be9f04b05
FROM ${DS60_PHP_IMAGE}
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && php -r "exit(extension_loaded('pdo_sqlite') ? 0 : 1);" \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 /run/ds60
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=php-cli
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
