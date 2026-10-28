ARG BASE_IMAGE=python:3.12.13-slim-trixie@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
FROM ${BASE_IMAGE}
USER root
COPY install.py requirements.amd64.lock requirements.arm64.lock /tmp/preparation/
RUN python3 /tmp/preparation/install.py && rm -r /tmp/preparation
ENV PYTHONPATH=/opt/ballista PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /project
USER 1000:1000
ENTRYPOINT ["python3"]
LABEL org.ds60.workshop.kind="apache-ballista" org.ds60.upstream.version="54.1.0"
