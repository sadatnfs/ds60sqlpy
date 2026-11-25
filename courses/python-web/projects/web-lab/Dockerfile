ARG WEB_BASE_IMAGE=ds60sqlpy-worker-python-web:2.1.1
FROM ${WEB_BASE_IMAGE}
WORKDIR /opt/web-lab
COPY . /opt/web-lab/
RUN WEB_PREPARING=1 python manage.py collectstatic --noinput --verbosity 0 \
    && python -m compileall -q .
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# compose.yaml supplies the host UID and GID; plain docker run uses nobody.
USER 65534:65534
ENTRYPOINT []
CMD ["python", "serve.py", "fastapi"]
