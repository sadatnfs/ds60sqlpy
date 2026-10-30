ARG WEB_BASE_IMAGE=ds60sqlpy-worker-python-web:1.2.0
FROM ${WEB_BASE_IMAGE}
WORKDIR /opt/web-lab
COPY . /opt/web-lab/
RUN WEB_PREPARING=1 python manage.py collectstatic --noinput --verbosity 0 \
    && python -m compileall -q .
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT []
CMD ["python", "serve.py", "fastapi"]
